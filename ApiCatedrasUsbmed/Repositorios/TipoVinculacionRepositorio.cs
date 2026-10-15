using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class TipoVinculacionRepositorio : ITipoVinculacionRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.tipo_vinculacion";
    private static readonly string[] Pk = { "id_tipo_vinculacion" };

    public TipoVinculacionRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "id_tipo_vinculacion", "nombre", "es_interno", "exige_programa", "activo" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<TipoVinculacion>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<TipoVinculacion>(sql)).AsList();
    }

    public async Task<TipoVinculacion?> ObtenerPorIdAsync(string idTipoVinculacion)
    {
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE id_tipo_vinculacion = @IdTipoVinculacion";
        return await con.QueryFirstOrDefaultAsync<TipoVinculacion>(sql, new { IdTipoVinculacion = idTipoVinculacion });
    }

    public async Task<bool> CrearAsync(TipoVinculacion entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarInsertSQL<TipoVinculacion>(Tabla, pkAutogenerada: false);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> ActualizarAsync(TipoVinculacion entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarUpdateSQL<TipoVinculacion>(Tabla, Pk);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> EliminarAsync(string idTipoVinculacion)
    {
        using var con = _cx.Crear();
        var sql = $"DELETE FROM {Tabla} WHERE id_tipo_vinculacion = @IdTipoVinculacion";
        return await con.ExecuteAsync(sql, new { IdTipoVinculacion = idTipoVinculacion }) > 0;
    }

    public async Task<List<TipoVinculacion>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<TipoVinculacion>(sql, new { Valor = valor })).AsList();
    }

    public async Task<int> CrearMasivoAsync(List<TipoVinculacion> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarInsertSQL<TipoVinculacion>(Tabla, pkAutogenerada: false);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }

    public async Task<int> ActualizarLoteAsync(List<TipoVinculacion> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarUpdateSQL<TipoVinculacion>(Tabla, Pk);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }
}
