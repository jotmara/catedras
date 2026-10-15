using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class VEmbudoRegistroRepositorio : IVEmbudoRegistroRepositorio
{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.v_embudo_registro";

    public VEmbudoRegistroRepositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) { "id_sesion", "catedra", "numero_reunion", "enlaces", "claves_enviadas", "claves_usadas", "registros", "encuestas" };

    private static void ValidarColumna(string columna)
    {
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{columna}'.");
    }

    public async Task<List<VEmbudoRegistro>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {Tabla} LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<VEmbudoRegistro>(sql)).AsList();
    }

    public async Task<List<VEmbudoRegistro>> ObtenerPorColumnaAsync(string columna, string valor)
    {
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {Tabla} WHERE CAST({columna} AS TEXT) = @Valor";
        return (await con.QueryAsync<VEmbudoRegistro>(sql, new { Valor = valor })).AsList();
    }
}
