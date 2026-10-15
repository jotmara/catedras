using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IEstadoProcesoServicio
{
    Task<List<EstadoProceso>> ObtenerTodosAsync(int? limite = null);
    Task<EstadoProceso?> ObtenerPorIdAsync(string idEstado);
    Task<bool> CrearAsync(EstadoProceso entidad);
    Task<bool> ActualizarAsync(EstadoProceso entidad);
    Task<bool> EliminarAsync(string idEstado);
    Task<List<EstadoProceso>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<EstadoProceso> entidades);
    Task<int> ActualizarLoteAsync(List<EstadoProceso> entidades);
}
