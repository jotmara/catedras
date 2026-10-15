using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IPreguntaRepositorio
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
