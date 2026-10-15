namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IServicioCorreo
{
    /// <summary>Devuelve false si el envio esta desactivado por configuracion.</summary>
    Task<bool> EnviarClaveAsync(string destino, string clave);
}
