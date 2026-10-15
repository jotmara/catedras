using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IUsuarioRepositorio
{
    Task<List<Usuario>> ObtenerTodosAsync(int? limite = null);
    Task<Usuario?> ObtenerPorIdAsync(long idUsuario);
    Task<bool> CrearAsync(Usuario entidad);
    Task<bool> ActualizarAsync(Usuario entidad);
    Task<bool> EliminarAsync(long idUsuario);
    Task<List<Usuario>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<Usuario> entidades);
    Task<int> ActualizarLoteAsync(List<Usuario> entidades);
}
