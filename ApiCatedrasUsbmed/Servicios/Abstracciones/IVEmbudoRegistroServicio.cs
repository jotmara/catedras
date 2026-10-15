using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IVEmbudoRegistroServicio
{
    Task<List<VEmbudoRegistro>> ObtenerTodosAsync(int? limite = null);
    Task<List<VEmbudoRegistro>> ObtenerPorColumnaAsync(string columna, string valor);
}
