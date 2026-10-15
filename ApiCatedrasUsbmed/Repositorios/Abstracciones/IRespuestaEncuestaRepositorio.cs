using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IRespuestaEncuestaRepositorio
{
    Task<List<RespuestaEncuesta>> ObtenerTodosAsync(int? limite = null);
    Task<RespuestaEncuesta?> ObtenerPorIdAsync(long idRespuesta);
    Task<bool> CrearAsync(RespuestaEncuesta entidad);
    Task<bool> ActualizarAsync(RespuestaEncuesta entidad);
    Task<bool> EliminarAsync(long idRespuesta);
    Task<List<RespuestaEncuesta>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<RespuestaEncuesta> entidades);
    Task<int> ActualizarLoteAsync(List<RespuestaEncuesta> entidades);
}
