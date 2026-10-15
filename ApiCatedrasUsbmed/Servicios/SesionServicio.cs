using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class SesionServicio : ISesionServicio
{
    private readonly ISesionRepositorio _repo;
    public SesionServicio(ISesionRepositorio repo) => _repo = repo;

    public Task<List<Sesion>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<Sesion?> ObtenerPorIdAsync(long idSesion) => _repo.ObtenerPorIdAsync(idSesion);
    public Task<bool> CrearAsync(Sesion entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(Sesion entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idSesion) => _repo.EliminarAsync(idSesion);
    public Task<List<Sesion>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<Sesion> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<Sesion> entidades) => _repo.ActualizarLoteAsync(entidades);
}
