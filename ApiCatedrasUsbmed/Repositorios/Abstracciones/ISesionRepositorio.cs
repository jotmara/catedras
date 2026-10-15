using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface ISesionRepositorio
{
    Task<List<Sesion>> ObtenerTodosAsync(int? limite = null);
    Task<Sesion?> ObtenerPorIdAsync(long idSesion);
    Task<bool> CrearAsync(Sesion entidad);
    Task<bool> ActualizarAsync(Sesion entidad);
    Task<bool> EliminarAsync(long idSesion);
    Task<List<Sesion>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<Sesion> entidades);
    Task<int> ActualizarLoteAsync(List<Sesion> entidades);
}
