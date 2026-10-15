using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

/// <summary>
/// EL UNICO repositorio con SQL escrito a mano.
///
/// Motivo: enlace_registro.ventana es un tstzrange. En el SELECT se proyecta con
/// lower()/upper() a dos columnas, y en el INSERT/UPDATE se reconstruye con tstzrange().
/// ConexionHelper no puede hacerlo porque trabaja columna a columna sobre el modelo.
///
/// El '[)' del tstzrange es deliberado: inicio incluido, fin excluido. Es el mismo que
/// usa sp_emitir_enlace en la base, y hay que mantenerlo igual para que la contencion
/// @> de RN-15 se comporte de la misma forma desde los dos lados.
/// </summary>
public class EnlaceRegistroRepositorio : IEnlaceRegistroRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.enlace_registro";

    // La proyeccion que convierte el rango en dos columnas del modelo.
    private const string Seleccion = @"
        SELECT id_enlace, fk_sesion, token, url_publica, ruta_imagen_qr, canal,
               lower(ventana) AS ventana_inicio,
               upper(ventana) AS ventana_fin,
               usos_maximos, revocado_en, fk_usuario_crea, creado_en
          FROM catedras.enlace_registro";

    public EnlaceRegistroRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas = new(StringComparer.OrdinalIgnoreCase)
    { "id_enlace", "fk_sesion", "token", "url_publica", "ruta_imagen_qr", "canal",
      "usos_maximos", "revocado_en", "fk_usuario_crea", "creado_en" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<EnlaceRegistro>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        var sql = $"{Seleccion} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<EnlaceRegistro>(sql)).AsList();
    }

    public async Task<EnlaceRegistro?> ObtenerPorIdAsync(long idEnlace)
    {
        using var con = _cx.Crear();
        return await con.QueryFirstOrDefaultAsync<EnlaceRegistro>(
            $"{Seleccion} WHERE id_enlace = @Id", new { Id = idEnlace });
    }

    public async Task<EnlaceRegistro?> ObtenerPorTokenAsync(Guid token)
    {
        using var con = _cx.CrearApp();      // lo consulta el camino publico
        return await con.QueryFirstOrDefaultAsync<EnlaceRegistro>(
            $"{Seleccion} WHERE token = @Token", new { Token = token });
    }

    public async Task<EnlaceRegistro?> ObtenerVigenteDeSesionAsync(long idSesion)
    {
        using var con = _cx.Crear();
        return await con.QueryFirstOrDefaultAsync<EnlaceRegistro>(
            $"{Seleccion} WHERE fk_sesion = @Id AND revocado_en IS NULL", new { Id = idSesion });
    }

    public async Task<bool> CrearAsync(EnlaceRegistro e)
    {
        using var con = _cx.Crear();
        const string sql = @"
            INSERT INTO catedras.enlace_registro
                   (fk_sesion, token, url_publica, ruta_imagen_qr, canal, ventana,
                    usos_maximos, revocado_en, fk_usuario_crea)
            VALUES (@FkSesion, @Token, @UrlPublica, @RutaImagenQr, @Canal,
                    tstzrange(@VentanaInicio, @VentanaFin, '[)'),
                    @UsosMaximos, @RevocadoEn, @FkUsuarioCrea)";
        return await con.ExecuteAsync(sql, e) > 0;
    }

    public async Task<bool> ActualizarAsync(EnlaceRegistro e)
    {
        using var con = _cx.Crear();
        const string sql = @"
            UPDATE catedras.enlace_registro
               SET fk_sesion = @FkSesion, url_publica = @UrlPublica,
                   ruta_imagen_qr = @RutaImagenQr, canal = @Canal,
                   ventana = tstzrange(@VentanaInicio, @VentanaFin, '[)'),
                   usos_maximos = @UsosMaximos, revocado_en = @RevocadoEn,
                   fk_usuario_crea = @FkUsuarioCrea
             WHERE id_enlace = @IdEnlace";
        return await con.ExecuteAsync(sql, e) > 0;
    }

    /// <summary>No borra: marca revocado_en. RN-32 y el WHERE del EXCLUDE de RN-36.</summary>
    public async Task<bool> RevocarAsync(long idEnlace)
    {
        using var con = _cx.Crear();
        const string sql = @"UPDATE catedras.enlace_registro
                                SET revocado_en = now()
                              WHERE id_enlace = @Id AND revocado_en IS NULL";
        return await con.ExecuteAsync(sql, new { Id = idEnlace }) > 0;
    }

    public async Task<List<EnlaceRegistro>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"{Seleccion} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<EnlaceRegistro>(sql, new { Valor = valor })).AsList();
    }
}
