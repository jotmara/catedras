using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

/// <summary>Vista de solo lectura.</summary>
public interface IVEmbudoRegistroRepositorio
{
    Task<List<VEmbudoRegistro>> ObtenerTodosAsync(int? limite = null);
    Task<List<VEmbudoRegistro>> ObtenerPorColumnaAsync(string columna, string valor);
}
