using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface ITipoPreguntaRepositorio
{
    Task<List<TipoPregunta>> ObtenerTodosAsync(int? limite = null);
    Task<TipoPregunta?> ObtenerPorIdAsync(string idTipoPregunta);
    Task<bool> CrearAsync(TipoPregunta entidad);
    Task<bool> ActualizarAsync(TipoPregunta entidad);
    Task<bool> EliminarAsync(string idTipoPregunta);
    Task<List<TipoPregunta>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<TipoPregunta> entidades);
    Task<int> ActualizarLoteAsync(List<TipoPregunta> entidades);
}
