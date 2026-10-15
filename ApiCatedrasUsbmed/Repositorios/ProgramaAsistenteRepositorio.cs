using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class ProgramaAsistenteRepositorio : IProgramaAsistenteRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.programa_asistente";
    private static readonly string[] Pk = { "fk_asistente", "fk_programa", "fk_periodo" };

    public ProgramaAsistenteRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "fk_asistente", "fk_programa", "fk_periodo", "estado" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<ProgramaAsistente>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<ProgramaAsistente>(sql)).AsList();
    }

    public async Task<ProgramaAsistente?> ObtenerPorIdAsync(long fkAsistente, string fkPrograma, string fkPeriodo)
    {
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE fk_asistente = @FkAsistente AND fk_programa = @FkPrograma AND fk_periodo = @FkPeriodo";
        return await con.QueryFirstOrDefaultAsync<ProgramaAsistente>(sql, new { FkAsistente = fkAsistente, FkPrograma = fkPrograma, FkPeriodo = fkPeriodo });
    }

    public async Task<bool> CrearAsync(ProgramaAsistente entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarInsertSQL<ProgramaAsistente>(Tabla, pkAutogenerada: false);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> ActualizarAsync(ProgramaAsistente entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarUpdateSQL<ProgramaAsistente>(Tabla, Pk);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> EliminarAsync(long fkAsistente, string fkPrograma, string fkPeriodo)
    {
        using var con = _cx.Crear();
        var sql = $"DELETE FROM {Tabla} WHERE fk_asistente = @FkAsistente AND fk_programa = @FkPrograma AND fk_periodo = @FkPeriodo";
        return await con.ExecuteAsync(sql, new { FkAsistente = fkAsistente, FkPrograma = fkPrograma, FkPeriodo = fkPeriodo }) > 0;
    }

    public async Task<List<ProgramaAsistente>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<ProgramaAsistente>(sql, new { Valor = valor })).AsList();
    }

    public async Task<int> CrearMasivoAsync(List<ProgramaAsistente> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarInsertSQL<ProgramaAsistente>(Tabla, pkAutogenerada: false);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }

    public async Task<int> ActualizarLoteAsync(List<ProgramaAsistente> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarUpdateSQL<ProgramaAsistente>(Tabla, Pk);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }
}
