using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IPreguntaServicio
{
    Task<List<Pregunta>> ObtenerTodosAsync(int? limite = null);
    Task<Pregunta?> ObtenerPorIdAsync(long idPregunta);
    Task<bool> CrearAsync(Pregunta entidad);
    Task<bool> ActualizarAsync(Pregunta entidad);
    Task<bool> EliminarAsync(long idPregunta);
    Task<List<Pregunta>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<Pregunta> entidades);
    Task<int> ActualizarLoteAsync(List<Pregunta> entidades);
}
