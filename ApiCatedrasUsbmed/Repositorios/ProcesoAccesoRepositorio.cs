using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

/// <summary>
/// Repositorio de PROCESO: no compone INSERT, llama a las rutinas de la base.
///
/// Es deliberado. El registro de un asistente tiene que pasar por
/// sp_validar_clave_y_registrar porque ahi viven la comprobacion de la ventana (RN-15),
/// las dos instantaneas (RN-22), la excepcion de Rutas de Paz (RN-07) y el cupo (RN-38).
/// Un INSERT directo sobre registro_asistencia saltaria la mitad de esas reglas.
///
/// Usa CrearApp(): el camino publico va con el rol minimo, que NO puede leer la tabla
/// asistente entera.
/// </summary>
public class ProcesoAccesoRepositorio : IProcesoAccesoRepositorio
{
    private readonly IFabricaConexion _cx;
    public ProcesoAccesoRepositorio(IFabricaConexion cx) => _cx = cx;

    public async Task<EnlacePublico?> ObtenerEnlacePublicoAsync(Guid token)
    {
        using var con = _cx.CrearApp();
        const string sql = @"
            SELECT e.token,
                   c.nombre                AS catedra,
                   s.titulo                AS sesion,
                   s.numero_reunion,
                   s.inicio, s.fin,
                   sd.nombre               AS sede,
                   m.nombre                AS modalidad,
                   s.lugar,
                   (e.ventana @> now() AND e.revocado_en IS NULL) AS ventana_abierta,
                   lower(e.ventana)        AS ventana_inicio,
                   upper(e.ventana)        AS ventana_fin
              FROM catedras.enlace_registro e
              JOIN catedras.sesion    s  ON s.id_sesion    = e.fk_sesion
              JOIN catedras.catedra   c  ON c.id_catedra   = s.fk_catedra
              JOIN catedras.sede      sd ON sd.id_sede     = s.fk_sede
              JOIN catedras.modalidad m  ON m.id_modalidad = s.fk_modalidad
             WHERE e.token = @Token";
        return await con.QueryFirstOrDefaultAsync<EnlacePublico>(sql, new { Token = token });
    }

    public async Task<ResultadoSolicitudClave?> SolicitarClaveAsync(string identificador, Guid token, string? ip)
    {
        using var con = _cx.CrearApp();
        // sp_solicitar_clave usa parametros INOUT y se invoca con CALL, que no devuelve
        // un conjunto de resultados: Dapper no puede recoger esos valores de salida.
        // Por eso se llama al envoltorio fn_solicitar_clave_api, que hace el CALL por
        // dentro y DEVUELVE las tres columnas. Ver sql/19-funciones-api.sql.
        const string sql = @"
            SELECT * FROM catedras.fn_solicitar_clave_api(@Identificador, @Token, CAST(@Ip AS inet))";
        return await con.QueryFirstOrDefaultAsync<ResultadoSolicitudClave>(
            sql, new { Identificador = identificador, Token = token, Ip = ip });
    }

    public async Task<long> ValidarYRegistrarAsync(long idClave, string clave, string? ip, string? userAgent)
    {
        using var con = _cx.CrearApp();
        const string sql = @"SELECT catedras.fn_validar_clave_api(
                                 @IdClave, @Clave, CAST(@Ip AS inet), @UserAgent)";
        return await con.ExecuteScalarAsync<long>(sql,
            new { IdClave = idClave, Clave = clave, Ip = ip, UserAgent = userAgent });
    }

    public async Task<long> ResolverAsistenteAsync(string identificador)
    {
        using var con = _cx.CrearApp();
        var r = await con.ExecuteScalarAsync<long?>(
            "SELECT catedras.fn_resolver_asistente(@Id)", new { Id = identificador });
        return r ?? 0;
    }

    public async Task<long> ResponderEncuestaAsync(long idRegistro, string respuestasJson)
    {
        using var con = _cx.CrearApp();
        const string sql = @"SELECT catedras.fn_responder_encuesta_api(@IdRegistro, CAST(@Json AS jsonb))";
        return await con.ExecuteScalarAsync<long>(sql, new { IdRegistro = idRegistro, Json = respuestasJson });
    }
}
