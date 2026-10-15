using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class VControlVentanaRepositorio : IVControlVentanaRepositorio
{
    private readonly IFabricaConexion _cx;
    public VControlVentanaRepositorio(IFabricaConexion cx) => _cx = cx;

    public async Task<List<VControlVentana>> ObtenerTodosAsync(int? limite = null)
    {
        using var con = _cx.Crear();
        var sql = @"SELECT id_registro, registrado_en,
                           lower(ventana) AS ventana_inicio,
                           upper(ventana) AS ventana_fin,
                           origen
                      FROM catedras.v_control_ventana";
        sql += $" LIMIT {Paginacion.Resolver(limite)}";
        return (await con.QueryAsync<VControlVentana>(sql)).AsList();
    }
}
