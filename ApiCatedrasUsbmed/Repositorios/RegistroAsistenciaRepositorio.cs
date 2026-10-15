using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class RegistroAsistenciaRepositorio : IRegistroAsistenciaRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.registro_asistencia";
    private static readonly string[] Pk = { "id_registro" };

    public RegistroAsistenciaRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "id_registro", "fk_sesion", "fk_asistente", "fk_enlace", "fk_clave", "registrado_en", "fk_programa_snapshot", "fk_vinculacion_snapshot", "origen", "ip", "user_agent" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<RegistroAsistencia>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<RegistroAsistencia>(sql)).AsList();
    }

    public async Task<RegistroAsistencia?> ObtenerPorIdAsync(long idRegistro)
    {
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE id_registro = @IdRegistro";
        return await con.QueryFirstOrDefaultAsync<RegistroAsistencia>(sql, new { IdRegistro = idRegistro });
    }

    public async Task<bool> CrearAsync(RegistroAsistencia entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarInsertSQL<RegistroAsistencia>(Tabla, pkAutogenerada: true);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> ActualizarAsync(RegistroAsistencia entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarUpdateSQL<RegistroAsistencia>(Tabla, Pk);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> EliminarAsync(long idRegistro)
    {
        using var con = _cx.Crear();
        var sql = $"DELETE FROM {Tabla} WHERE id_registro = @IdRegistro";
        return await con.ExecuteAsync(sql, new { IdRegistro = idRegistro }) > 0;
    }

    public async Task<List<RegistroAsistencia>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<RegistroAsistencia>(sql, new { Valor = valor })).AsList();
    }

    public async Task<int> CrearMasivoAsync(List<RegistroAsistencia> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarInsertSQL<RegistroAsistencia>(Tabla, pkAutogenerada: true);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }

    public async Task<int> ActualizarLoteAsync(List<RegistroAsistencia> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarUpdateSQL<RegistroAsistencia>(Tabla, Pk);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }
}
