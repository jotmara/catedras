using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class LoteMigracionRepositorio : ILoteMigracionRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.lote_migracion";
    private static readonly string[] Pk = { "id_lote_migracion" };

    public LoteMigracionRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "id_lote_migracion", "fk_sesion", "nombre_proceso", "nombre_archivo", "generado_en", "fk_usuario", "instancia_proceso_asis", "fk_estado_proceso", "total_filas", "observaciones" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<LoteMigracion>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<LoteMigracion>(sql)).AsList();
    }

    public async Task<LoteMigracion?> ObtenerPorIdAsync(long idLoteMigracion)
    {
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE id_lote_migracion = @IdLoteMigracion";
        return await con.QueryFirstOrDefaultAsync<LoteMigracion>(sql, new { IdLoteMigracion = idLoteMigracion });
    }

    public async Task<bool> CrearAsync(LoteMigracion entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarInsertSQL<LoteMigracion>(Tabla, pkAutogenerada: true);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> ActualizarAsync(LoteMigracion entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarUpdateSQL<LoteMigracion>(Tabla, Pk);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> EliminarAsync(long idLoteMigracion)
    {
        using var con = _cx.Crear();
        var sql = $"DELETE FROM {Tabla} WHERE id_lote_migracion = @IdLoteMigracion";
        return await con.ExecuteAsync(sql, new { IdLoteMigracion = idLoteMigracion }) > 0;
    }

    public async Task<List<LoteMigracion>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<LoteMigracion>(sql, new { Valor = valor })).AsList();
    }

    public async Task<int> CrearMasivoAsync(List<LoteMigracion> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarInsertSQL<LoteMigracion>(Tabla, pkAutogenerada: true);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }

    public async Task<int> ActualizarLoteAsync(List<LoteMigracion> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarUpdateSQL<LoteMigracion>(Tabla, Pk);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }
}
