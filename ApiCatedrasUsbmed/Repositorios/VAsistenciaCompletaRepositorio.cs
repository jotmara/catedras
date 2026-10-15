using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class VAsistenciaCompletaRepositorio : IVAsistenciaCompletaRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.v_asistencia_completa";

    public VAsistenciaCompletaRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "id_registro", "registrado_en", "origen", "id_evento_asis", "catedra", "id_sesion", "numero_reunion", "sesion", "inicio", "periodo", "sede", "modalidad", "id_asistente", "id_asis", "asistente", "es_externo", "programa", "programa_nombre", "facultad", "vinculacion", "es_interno", "respondio_encuesta" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<VAsistenciaCompleta>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<VAsistenciaCompleta>(sql)).AsList();
    }

    public async Task<List<VAsistenciaCompleta>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<VAsistenciaCompleta>(sql, new { Valor = valor })).AsList();
    }
}
