using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class UsuarioServicio : IUsuarioServicio
{
    private readonly IUsuarioRepositorio _repo;
    public UsuarioServicio(IUsuarioRepositorio repo) => _repo = repo;

    public Task<List<Usuario>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<Usuario?> ObtenerPorIdAsync(long idUsuario) => _repo.ObtenerPorIdAsync(idUsuario);
    public Task<bool> CrearAsync(Usuario entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(Usuario entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idUsuario) => _repo.EliminarAsync(idUsuario);
    public Task<List<Usuario>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<Usuario> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<Usuario> entidades) => _repo.ActualizarLoteAsync(entidades);
}
