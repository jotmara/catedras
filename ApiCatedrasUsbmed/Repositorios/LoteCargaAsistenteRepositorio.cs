using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class LoteCargaAsistenteRepositorio : ILoteCargaAsistenteRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.lote_carga_asistente";
    private static readonly string[] Pk = { "id_lote_carga" };

    public LoteCargaAsistenteRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "id_lote_carga", "nombre_archivo", "cargado_en", "fk_usuario", "filas_leidas", "filas_aceptadas", "filas_rechazadas", "observaciones" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<LoteCargaAsistente>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<LoteCargaAsistente>(sql)).AsList();
    }

    public async Task<LoteCargaAsistente?> ObtenerPorIdAsync(long idLoteCarga)
    {
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE id_lote_carga = @IdLoteCarga";
        return await con.QueryFirstOrDefaultAsync<LoteCargaAsistente>(sql, new { IdLoteCarga = idLoteCarga });
    }

    public async Task<bool> CrearAsync(LoteCargaAsistente entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarInsertSQL<LoteCargaAsistente>(Tabla, pkAutogenerada: true);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> ActualizarAsync(LoteCargaAsistente entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarUpdateSQL<LoteCargaAsistente>(Tabla, Pk);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> EliminarAsync(long idLoteCarga)
    {
        using var con = _cx.Crear();
        var sql = $"DELETE FROM {Tabla} WHERE id_lote_carga = @IdLoteCarga";
        return await con.ExecuteAsync(sql, new { IdLoteCarga = idLoteCarga }) > 0;
    }

    public async Task<List<LoteCargaAsistente>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<LoteCargaAsistente>(sql, new { Valor = valor })).AsList();
    }

    public async Task<int> CrearMasivoAsync(List<LoteCargaAsistente> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarInsertSQL<LoteCargaAsistente>(Tabla, pkAutogenerada: true);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }

    public async Task<int> ActualizarLoteAsync(List<LoteCargaAsistente> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarUpdateSQL<LoteCargaAsistente>(Tabla, Pk);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }
}
