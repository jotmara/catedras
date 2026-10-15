using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class DetalleMigracionRepositorio : IDetalleMigracionRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.detalle_migracion";
    private static readonly string[] Pk = { "id_detalle" };

    public DetalleMigracionRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "id_detalle", "fk_lote_migracion", "fk_registro", "id_asis_enviado", "programa_enviado", "reunion_enviada", "resultado", "mensaje" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<DetalleMigracion>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<DetalleMigracion>(sql)).AsList();
    }

    public async Task<DetalleMigracion?> ObtenerPorIdAsync(long idDetalle)
    {
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE id_detalle = @IdDetalle";
        return await con.QueryFirstOrDefaultAsync<DetalleMigracion>(sql, new { IdDetalle = idDetalle });
    }

    public async Task<bool> CrearAsync(DetalleMigracion entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarInsertSQL<DetalleMigracion>(Tabla, pkAutogenerada: true);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> ActualizarAsync(DetalleMigracion entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarUpdateSQL<DetalleMigracion>(Tabla, Pk);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> EliminarAsync(long idDetalle)
    {
        using var con = _cx.Crear();
        var sql = $"DELETE FROM {Tabla} WHERE id_detalle = @IdDetalle";
        return await con.ExecuteAsync(sql, new { IdDetalle = idDetalle }) > 0;
    }

    public async Task<List<DetalleMigracion>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<DetalleMigracion>(sql, new { Valor = valor })).AsList();
    }

    public async Task<int> CrearMasivoAsync(List<DetalleMigracion> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarInsertSQL<DetalleMigracion>(Tabla, pkAutogenerada: true);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }

    public async Task<int> ActualizarLoteAsync(List<DetalleMigracion> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarUpdateSQL<DetalleMigracion>(Tabla, Pk);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }
}
