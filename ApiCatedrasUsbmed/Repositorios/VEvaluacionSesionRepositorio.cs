using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class VEvaluacionSesionRepositorio : IVEvaluacionSesionRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.v_evaluacion_sesion";

    public VEvaluacionSesionRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "id_sesion", "catedra", "numero_reunion", "orden", "enunciado", "tipo", "respuestas", "promedio", "minimo", "maximo" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<VEvaluacionSesion>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<VEvaluacionSesion>(sql)).AsList();
    }

    public async Task<List<VEvaluacionSesion>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<VEvaluacionSesion>(sql, new { Valor = valor })).AsList();
    }
}
