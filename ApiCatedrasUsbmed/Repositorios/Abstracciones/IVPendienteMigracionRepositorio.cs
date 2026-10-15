using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

/// <summary>Vista de solo lectura.</summary>
public interface IVPendienteMigracionRepositorio
{
    Task<List<VPendienteMigracion>> ObtenerTodosAsync(int? limite = null);
    Task<List<VPendienteMigracion>> ObtenerPorColumnaAsync(string columna, string valor);
}
