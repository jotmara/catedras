using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class EstadoProcesoRepositorio : IEstadoProcesoRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.estado_proceso";
    private static readonly string[] Pk = { "id_estado" };

    public EstadoProcesoRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "id_estado", "nombre", "es_final", "es_exitoso" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<EstadoProceso>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<EstadoProceso>(sql)).AsList();
    }

    public async Task<EstadoProceso?> ObtenerPorIdAsync(string idEstado)
    {
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE id_estado = @IdEstado";
        return await con.QueryFirstOrDefaultAsync<EstadoProceso>(sql, new { IdEstado = idEstado });
    }

    public async Task<bool> CrearAsync(EstadoProceso entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarInsertSQL<EstadoProceso>(Tabla, pkAutogenerada: false);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> ActualizarAsync(EstadoProceso entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarUpdateSQL<EstadoProceso>(Tabla, Pk);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> EliminarAsync(string idEstado)
    {
        using var con = _cx.Crear();
        var sql = $"DELETE FROM {Tabla} WHERE id_estado = @IdEstado";
        return await con.ExecuteAsync(sql, new { IdEstado = idEstado }) > 0;
    }

    public async Task<List<EstadoProceso>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<EstadoProceso>(sql, new { Valor = valor })).AsList();
    }

    public async Task<int> CrearMasivoAsync(List<EstadoProceso> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarInsertSQL<EstadoProceso>(Tabla, pkAutogenerada: false);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }

    public async Task<int> ActualizarLoteAsync(List<EstadoProceso> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarUpdateSQL<EstadoProceso>(Tabla, Pk);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }
}
