using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IVControlVentanaServicio
{
    Task<List<VControlVentana>> ObtenerTodosAsync(int? limite = null);
}
