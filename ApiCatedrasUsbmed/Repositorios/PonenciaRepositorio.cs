using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class PonenciaRepositorio : IPonenciaRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.ponencia";
    private static readonly string[] Pk = { "fk_sesion", "fk_asistente", "rol" };

    public PonenciaRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "fk_sesion", "fk_asistente", "rol" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<Ponencia>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<Ponencia>(sql)).AsList();
    }

    public async Task<Ponencia?> ObtenerPorIdAsync(long fkSesion, long fkAsistente, string rol)
    {
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE fk_sesion = @FkSesion AND fk_asistente = @FkAsistente AND rol = @Rol";
        return await con.QueryFirstOrDefaultAsync<Ponencia>(sql, new { FkSesion = fkSesion, FkAsistente = fkAsistente, Rol = rol });
    }

    public async Task<bool> CrearAsync(Ponencia entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarInsertSQL<Ponencia>(Tabla, pkAutogenerada: false);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> ActualizarAsync(Ponencia entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarUpdateSQL<Ponencia>(Tabla, Pk);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> EliminarAsync(long fkSesion, long fkAsistente, string rol)
    {
        using var con = _cx.Crear();
        var sql = $"DELETE FROM {Tabla} WHERE fk_sesion = @FkSesion AND fk_asistente = @FkAsistente AND rol = @Rol";
        return await con.ExecuteAsync(sql, new { FkSesion = fkSesion, FkAsistente = fkAsistente, Rol = rol }) > 0;
    }

    public async Task<List<Ponencia>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<Ponencia>(sql, new { Valor = valor })).AsList();
    }

    public async Task<int> CrearMasivoAsync(List<Ponencia> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarInsertSQL<Ponencia>(Tabla, pkAutogenerada: false);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }

    public async Task<int> ActualizarLoteAsync(List<Ponencia> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarUpdateSQL<Ponencia>(Tabla, Pk);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }
}
