using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class ProgramaAcademicoRepositorio : IProgramaAcademicoRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.programa_academico";
    private static readonly string[] Pk = { "codigo" };

    public ProgramaAcademicoRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "codigo", "nombre", "fk_facultad", "nivel", "activo" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<ProgramaAcademico>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<ProgramaAcademico>(sql)).AsList();
    }

    public async Task<ProgramaAcademico?> ObtenerPorIdAsync(string codigo)
    {
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE codigo = @Codigo";
        return await con.QueryFirstOrDefaultAsync<ProgramaAcademico>(sql, new { Codigo = codigo });
    }

    public async Task<bool> CrearAsync(ProgramaAcademico entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarInsertSQL<ProgramaAcademico>(Tabla, pkAutogenerada: false);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> ActualizarAsync(ProgramaAcademico entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarUpdateSQL<ProgramaAcademico>(Tabla, Pk);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> EliminarAsync(string codigo)
    {
        using var con = _cx.Crear();
        var sql = $"DELETE FROM {Tabla} WHERE codigo = @Codigo";
        return await con.ExecuteAsync(sql, new { Codigo = codigo }) > 0;
    }

    public async Task<List<ProgramaAcademico>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<ProgramaAcademico>(sql, new { Valor = valor })).AsList();
    }

    public async Task<int> CrearMasivoAsync(List<ProgramaAcademico> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarInsertSQL<ProgramaAcademico>(Tabla, pkAutogenerada: false);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }

    public async Task<int> ActualizarLoteAsync(List<ProgramaAcademico> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarUpdateSQL<ProgramaAcademico>(Tabla, Pk);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }
}
