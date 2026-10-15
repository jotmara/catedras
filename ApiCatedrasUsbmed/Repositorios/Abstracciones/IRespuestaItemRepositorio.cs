using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IRespuestaItemRepositorio
{
    Task<List<RespuestaItem>> ObtenerTodosAsync(int? limite = null);
    Task<RespuestaItem?> ObtenerPorIdAsync(long idItem);
    Task<bool> CrearAsync(RespuestaItem entidad);
    Task<bool> ActualizarAsync(RespuestaItem entidad);
    Task<bool> EliminarAsync(long idItem);
    Task<List<RespuestaItem>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<RespuestaItem> entidades);
    Task<int> ActualizarLoteAsync(List<RespuestaItem> entidades);
}
