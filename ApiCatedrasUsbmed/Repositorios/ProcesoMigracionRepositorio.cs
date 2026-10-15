using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class ProcesoMigracionRepositorio : IProcesoMigracionRepositorio
{
    private readonly IFabricaConexion _cx;
    public ProcesoMigracionRepositorio(IFabricaConexion cx) => _cx = cx;

    /// <summary>
    /// fn_exportar_asis devuelve EXACTAMENTE tres columnas y ya filtra externos y
    /// registros sin programa (RN-08, RN-28). La API no debe anadir ni quitar nada.
    /// </summary>
    public async Task<List<FilaArchivoAsis>> ExportarAsync(long idSesion)
    {
        using var con = _cx.Crear();
        const string sql = @"SELECT reunion, id_asis, programa
                               FROM catedras.fn_exportar_asis(@IdSesion)";
        return (await con.QueryAsync<FilaArchivoAsis>(sql, new { IdSesion = idSesion })).AsList();
    }

    public async Task<long> GenerarLoteAsync(long idSesion, long? idUsuario)
    {
        using var con = _cx.Crear();
        return await con.ExecuteScalarAsync<long>(
            "SELECT catedras.fn_generar_lote_api(@IdSesion, @Usuario)",
            new { IdSesion = idSesion, Usuario = idUsuario });
    }

    public async Task<bool> RegistrarResultadoAsync(long idLote, ResultadoLote r)
    {
        using var con = _cx.Crear();
        const string sql = @"UPDATE catedras.lote_migracion
                                SET fk_estado_proceso      = @Estado,
                                    instancia_proceso_asis = @Instancia,
                                    observaciones          = COALESCE(@Obs, observaciones)
                              WHERE id_lote_migracion = @Id";
        return await con.ExecuteAsync(sql, new
        {
            Id = idLote, Estado = r.Estado, Instancia = r.InstanciaProcesoAsis, Obs = r.Observaciones
        }) > 0;
    }

    public async Task<string?> NombreArchivoAsync(long idSesion)
    {
        using var con = _cx.Crear();
        const string sql = @"SELECT 'ME_CATEDRA_' || c.id_evento_asis || '_R' || s.numero_reunion || '.xlsx'
                               FROM catedras.sesion s
                               JOIN catedras.catedra c ON c.id_catedra = s.fk_catedra
                              WHERE s.id_sesion = @Id";
        return await con.ExecuteScalarAsync<string?>(sql, new { Id = idSesion });
    }
}
