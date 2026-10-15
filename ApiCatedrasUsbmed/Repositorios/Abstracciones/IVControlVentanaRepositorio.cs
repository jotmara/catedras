using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IVControlVentanaRepositorio
{
    Task<List<VControlVentana>> ObtenerTodosAsync(int? limite = null);
}
