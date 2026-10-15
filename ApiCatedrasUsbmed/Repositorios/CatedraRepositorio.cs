using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class CatedraRepositorio : ICatedraRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.catedra";
    private static readonly string[] Pk = { "id_catedra" };

    public CatedraRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "id_catedra", "id_evento_asis", "nombre", "nombre_asis", "fk_tipo_evento", "fk_dependencia", "activo", "creado_en" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<Catedra>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<Catedra>(sql)).AsList();
    }

    public async Task<Catedra?> ObtenerPorIdAsync(long idCatedra)
    {
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE id_catedra = @IdCatedra";
        return await con.QueryFirstOrDefaultAsync<Catedra>(sql, new { IdCatedra = idCatedra });
    }

    public async Task<bool> CrearAsync(Catedra entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarInsertSQL<Catedra>(Tabla, pkAutogenerada: true);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> ActualizarAsync(Catedra entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarUpdateSQL<Catedra>(Tabla, Pk);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> EliminarAsync(long idCatedra)
    {
        using var con = _cx.Crear();
        var sql = $"DELETE FROM {Tabla} WHERE id_catedra = @IdCatedra";
        return await con.ExecuteAsync(sql, new { IdCatedra = idCatedra }) > 0;
    }

    public async Task<List<Catedra>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<Catedra>(sql, new { Valor = valor })).AsList();
    }

    public async Task<int> CrearMasivoAsync(List<Catedra> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarInsertSQL<Catedra>(Tabla, pkAutogenerada: true);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }

    public async Task<int> ActualizarLoteAsync(List<Catedra> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarUpdateSQL<Catedra>(Tabla, Pk);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }
}
