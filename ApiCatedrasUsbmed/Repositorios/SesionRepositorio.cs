using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class SesionRepositorio : ISesionRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.sesion";
    private static readonly string[] Pk = { "id_sesion" };

    public SesionRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "id_sesion", "fk_catedra", "numero_reunion", "numero_reunion_asis", "titulo", "inicio", "fin", "fk_modalidad", "fk_sede", "fk_periodo", "fk_encuesta", "lugar", "enlace_virtual", "cupo", "estado", "creado_en" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<Sesion>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<Sesion>(sql)).AsList();
    }

    public async Task<Sesion?> ObtenerPorIdAsync(long idSesion)
    {
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE id_sesion = @IdSesion";
        return await con.QueryFirstOrDefaultAsync<Sesion>(sql, new { IdSesion = idSesion });
    }

    public async Task<bool> CrearAsync(Sesion entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarInsertSQL<Sesion>(Tabla, pkAutogenerada: true);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> ActualizarAsync(Sesion entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarUpdateSQL<Sesion>(Tabla, Pk);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> EliminarAsync(long idSesion)
    {
        using var con = _cx.Crear();
        var sql = $"DELETE FROM {Tabla} WHERE id_sesion = @IdSesion";
        return await con.ExecuteAsync(sql, new { IdSesion = idSesion }) > 0;
    }

    public async Task<List<Sesion>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<Sesion>(sql, new { Valor = valor })).AsList();
    }

    public async Task<int> CrearMasivoAsync(List<Sesion> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarInsertSQL<Sesion>(Tabla, pkAutogenerada: true);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }

    public async Task<int> ActualizarLoteAsync(List<Sesion> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarUpdateSQL<Sesion>(Tabla, Pk);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }
}
