using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IDetalleMigracionServicio
{
    Task<List<DetalleMigracion>> ObtenerTodosAsync(int? limite = null);
    Task<DetalleMigracion?> ObtenerPorIdAsync(long idDetalle);
    Task<bool> CrearAsync(DetalleMigracion entidad);
    Task<bool> ActualizarAsync(DetalleMigracion entidad);
    Task<bool> EliminarAsync(long idDetalle);
    Task<List<DetalleMigracion>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<DetalleMigracion> entidades);
    Task<int> ActualizarLoteAsync(List<DetalleMigracion> entidades);
}
