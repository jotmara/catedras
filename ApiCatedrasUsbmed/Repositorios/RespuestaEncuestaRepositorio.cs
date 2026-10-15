using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class RespuestaEncuestaRepositorio : IRespuestaEncuestaRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.respuesta_encuesta";
    private static readonly string[] Pk = { "id_respuesta" };

    public RespuestaEncuestaRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "id_respuesta", "fk_registro", "fk_encuesta", "respondida_en", "completa" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<RespuestaEncuesta>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<RespuestaEncuesta>(sql)).AsList();
    }

    public async Task<RespuestaEncuesta?> ObtenerPorIdAsync(long idRespuesta)
    {
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE id_respuesta = @IdRespuesta";
        return await con.QueryFirstOrDefaultAsync<RespuestaEncuesta>(sql, new { IdRespuesta = idRespuesta });
    }

    public async Task<bool> CrearAsync(RespuestaEncuesta entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarInsertSQL<RespuestaEncuesta>(Tabla, pkAutogenerada: true);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> ActualizarAsync(RespuestaEncuesta entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarUpdateSQL<RespuestaEncuesta>(Tabla, Pk);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> EliminarAsync(long idRespuesta)
    {
        using var con = _cx.Crear();
        var sql = $"DELETE FROM {Tabla} WHERE id_respuesta = @IdRespuesta";
        return await con.ExecuteAsync(sql, new { IdRespuesta = idRespuesta }) > 0;
    }

    public async Task<List<RespuestaEncuesta>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<RespuestaEncuesta>(sql, new { Valor = valor })).AsList();
    }

    public async Task<int> CrearMasivoAsync(List<RespuestaEncuesta> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarInsertSQL<RespuestaEncuesta>(Tabla, pkAutogenerada: true);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }

    public async Task<int> ActualizarLoteAsync(List<RespuestaEncuesta> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarUpdateSQL<RespuestaEncuesta>(Tabla, Pk);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }
}
