using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IVPendienteMigracionServicio
{
    Task<List<VPendienteMigracion>> ObtenerTodosAsync(int? limite = null);
    Task<List<VPendienteMigracion>> ObtenerPorColumnaAsync(string columna, string valor);
}
