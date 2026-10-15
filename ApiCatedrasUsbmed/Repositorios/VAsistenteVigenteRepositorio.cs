using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class VAsistenteVigenteRepositorio : IVAsistenteVigenteRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.v_asistente_vigente";

    public VAsistenteVigenteRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "id_asistente", "id_asis", "nombre_completo", "es_externo", "correo_contacto", "tiene_correo_institucional", "documento_vigente", "tipo_documento", "vinculacion", "vinculacion_nombre", "es_interno", "exige_programa", "activo" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<VAsistenteVigente>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<VAsistenteVigente>(sql)).AsList();
    }

    public async Task<List<VAsistenteVigente>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<VAsistenteVigente>(sql, new { Valor = valor })).AsList();
    }
}
