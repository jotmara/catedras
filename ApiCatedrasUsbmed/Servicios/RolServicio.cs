using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class RolServicio : IRolServicio
{
    private readonly IRolRepositorio _repo;
    public RolServicio(IRolRepositorio repo) => _repo = repo;

    public Task<List<Rol>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<Rol?> ObtenerPorIdAsync(string idRol) => _repo.ObtenerPorIdAsync(idRol);
    public Task<bool> CrearAsync(Rol entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(Rol entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(string idRol) => _repo.EliminarAsync(idRol);
    public Task<List<Rol>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<Rol> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<Rol> entidades) => _repo.ActualizarLoteAsync(entidades);
}
