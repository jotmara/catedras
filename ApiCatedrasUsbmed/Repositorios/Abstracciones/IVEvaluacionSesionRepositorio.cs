using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

/// <summary>Vista de solo lectura.</summary>
public interface IVEvaluacionSesionRepositorio
{
    Task<List<VEvaluacionSesion>> ObtenerTodosAsync(int? limite = null);
    Task<List<VEvaluacionSesion>> ObtenerPorColumnaAsync(string columna, string valor);
}
