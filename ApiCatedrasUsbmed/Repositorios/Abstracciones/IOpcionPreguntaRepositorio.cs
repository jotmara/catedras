using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IOpcionPreguntaRepositorio
{
    Task<List<OpcionPregunta>> ObtenerTodosAsync(int? limite = null);
    Task<OpcionPregunta?> ObtenerPorIdAsync(long idOpcion);
    Task<bool> CrearAsync(OpcionPregunta entidad);
    Task<bool> ActualizarAsync(OpcionPregunta entidad);
    Task<bool> EliminarAsync(long idOpcion);
    Task<List<OpcionPregunta>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<OpcionPregunta> entidades);
    Task<int> ActualizarLoteAsync(List<OpcionPregunta> entidades);
}
