using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IRolServicio
{
    Task<List<Rol>> ObtenerTodosAsync(int? limite = null);
    Task<Rol?> ObtenerPorIdAsync(string idRol);
    Task<bool> CrearAsync(Rol entidad);
    Task<bool> ActualizarAsync(Rol entidad);
    Task<bool> EliminarAsync(string idRol);
    Task<List<Rol>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<Rol> entidades);
    Task<int> ActualizarLoteAsync(List<Rol> entidades);
}
