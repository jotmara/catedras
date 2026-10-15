using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class VinculacionAsistenteRepositorio : IVinculacionAsistenteRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.vinculacion_asistente";
    private static readonly string[] Pk = { "fk_asistente", "fk_tipo_vinculacion", "fecha_ini" };

    public VinculacionAsistenteRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "fk_asistente", "fk_tipo_vinculacion", "fecha_ini", "fecha_fin" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<VinculacionAsistente>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<VinculacionAsistente>(sql)).AsList();
    }

    public async Task<VinculacionAsistente?> ObtenerPorIdAsync(long fkAsistente, string fkTipoVinculacion, DateOnly fechaIni)
    {
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE fk_asistente = @FkAsistente AND fk_tipo_vinculacion = @FkTipoVinculacion AND fecha_ini = @FechaIni";
        return await con.QueryFirstOrDefaultAsync<VinculacionAsistente>(sql, new { FkAsistente = fkAsistente, FkTipoVinculacion = fkTipoVinculacion, FechaIni = fechaIni });
    }

    public async Task<bool> CrearAsync(VinculacionAsistente entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarInsertSQL<VinculacionAsistente>(Tabla, pkAutogenerada: false);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> ActualizarAsync(VinculacionAsistente entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarUpdateSQL<VinculacionAsistente>(Tabla, Pk);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> EliminarAsync(long fkAsistente, string fkTipoVinculacion, DateOnly fechaIni)
    {
        using var con = _cx.Crear();
        var sql = $"DELETE FROM {Tabla} WHERE fk_asistente = @FkAsistente AND fk_tipo_vinculacion = @FkTipoVinculacion AND fecha_ini = @FechaIni";
        return await con.ExecuteAsync(sql, new { FkAsistente = fkAsistente, FkTipoVinculacion = fkTipoVinculacion, FechaIni = fechaIni }) > 0;
    }

    public async Task<List<VinculacionAsistente>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<VinculacionAsistente>(sql, new { Valor = valor })).AsList();
    }

    public async Task<int> CrearMasivoAsync(List<VinculacionAsistente> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarInsertSQL<VinculacionAsistente>(Tabla, pkAutogenerada: false);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }

    public async Task<int> ActualizarLoteAsync(List<VinculacionAsistente> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarUpdateSQL<VinculacionAsistente>(Tabla, Pk);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }
}
