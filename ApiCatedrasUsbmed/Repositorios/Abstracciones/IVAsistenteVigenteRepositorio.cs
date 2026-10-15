using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

/// <summary>Vista de solo lectura.</summary>
public interface IVAsistenteVigenteRepositorio
{
    Task<List<VAsistenteVigente>> ObtenerTodosAsync(int? limite = null);
    Task<List<VAsistenteVigente>> ObtenerPorColumnaAsync(string columna, string valor);
}
