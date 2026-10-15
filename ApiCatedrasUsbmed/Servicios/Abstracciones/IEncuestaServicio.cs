using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IEncuestaServicio
{
    Task<List<Encuesta>> ObtenerTodosAsync(int? limite = null);
    Task<Encuesta?> ObtenerPorIdAsync(long idEncuesta);
    Task<bool> CrearAsync(Encuesta entidad);
    Task<bool> ActualizarAsync(Encuesta entidad);
    Task<bool> EliminarAsync(long idEncuesta);
    Task<List<Encuesta>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<Encuesta> entidades);
    Task<int> ActualizarLoteAsync(List<Encuesta> entidades);
}
