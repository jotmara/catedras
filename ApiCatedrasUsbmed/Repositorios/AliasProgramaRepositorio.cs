using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class AliasProgramaRepositorio : IAliasProgramaRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.alias_programa";
    private static readonly string[] Pk = { "id_alias" };

    public AliasProgramaRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "id_alias", "texto_normalizado", "fk_programa", "origen", "creado_en" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<AliasPrograma>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<AliasPrograma>(sql)).AsList();
    }

    public async Task<AliasPrograma?> ObtenerPorIdAsync(long idAlias)
    {
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE id_alias = @IdAlias";
        return await con.QueryFirstOrDefaultAsync<AliasPrograma>(sql, new { IdAlias = idAlias });
    }

    public async Task<bool> CrearAsync(AliasPrograma entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarInsertSQL<AliasPrograma>(Tabla, pkAutogenerada: true);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> ActualizarAsync(AliasPrograma entidad)
    {
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarUpdateSQL<AliasPrograma>(Tabla, Pk);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }

    public async Task<bool> EliminarAsync(long idAlias)
    {
        using var con = _cx.Crear();
        var sql = $"DELETE FROM {Tabla} WHERE id_alias = @IdAlias";
        return await con.ExecuteAsync(sql, new { IdAlias = idAlias }) > 0;
    }

    public async Task<List<AliasPrograma>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<AliasPrograma>(sql, new { Valor = valor })).AsList();
    }

    public async Task<int> CrearMasivoAsync(List<AliasPrograma> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarInsertSQL<AliasPrograma>(Tabla, pkAutogenerada: true);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }

    public async Task<int> ActualizarLoteAsync(List<AliasPrograma> entidades)
    {
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarUpdateSQL<AliasPrograma>(Tabla, Pk);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }
}
