using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IClaveAccesoServicio
{
    Task<List<ClaveAcceso>> ObtenerTodosAsync(int? limite = null);
    Task<ClaveAcceso?> ObtenerPorIdAsync(long idClave);
    Task<bool> CrearAsync(ClaveAcceso entidad);
    Task<bool> ActualizarAsync(ClaveAcceso entidad);
    Task<bool> EliminarAsync(long idClave);
    Task<List<ClaveAcceso>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<ClaveAcceso> entidades);
    Task<int> ActualizarLoteAsync(List<ClaveAcceso> entidades);
}
