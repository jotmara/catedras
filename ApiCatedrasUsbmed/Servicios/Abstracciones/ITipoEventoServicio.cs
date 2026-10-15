using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface ITipoEventoServicio
{
    Task<List<TipoEvento>> ObtenerTodosAsync(int? limite = null);
    Task<TipoEvento?> ObtenerPorIdAsync(string idTipoEvento);
    Task<bool> CrearAsync(TipoEvento entidad);
    Task<bool> ActualizarAsync(TipoEvento entidad);
    Task<bool> EliminarAsync(string idTipoEvento);
    Task<List<TipoEvento>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<TipoEvento> entidades);
    Task<int> ActualizarLoteAsync(List<TipoEvento> entidades);
}
