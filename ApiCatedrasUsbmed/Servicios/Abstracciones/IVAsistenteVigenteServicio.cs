using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IVAsistenteVigenteServicio
{
    Task<List<VAsistenteVigente>> ObtenerTodosAsync(int? limite = null);
    Task<List<VAsistenteVigente>> ObtenerPorColumnaAsync(string columna, string valor);
}
