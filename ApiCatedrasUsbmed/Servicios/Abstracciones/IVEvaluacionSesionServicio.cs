using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IVEvaluacionSesionServicio
{
    Task<List<VEvaluacionSesion>> ObtenerTodosAsync(int? limite = null);
    Task<List<VEvaluacionSesion>> ObtenerPorColumnaAsync(string columna, string valor);
}
