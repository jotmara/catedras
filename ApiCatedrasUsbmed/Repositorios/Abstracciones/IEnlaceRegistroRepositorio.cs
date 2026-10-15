using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IEnlaceRegistroRepositorio
{
    Task<List<EnlaceRegistro>> ObtenerTodosAsync(int? limite = null);
    Task<EnlaceRegistro?> ObtenerPorIdAsync(long idEnlace);
    Task<EnlaceRegistro?> ObtenerPorTokenAsync(Guid token);
    Task<EnlaceRegistro?> ObtenerVigenteDeSesionAsync(long idSesion);
    Task<bool> CrearAsync(EnlaceRegistro entidad);
    Task<bool> ActualizarAsync(EnlaceRegistro entidad);
    Task<bool> RevocarAsync(long idEnlace);
    Task<List<EnlaceRegistro>> ObtenerPorColumnaAsync(string columna, string valor);
}
