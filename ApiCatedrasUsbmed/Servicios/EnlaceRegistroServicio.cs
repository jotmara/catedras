using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class EnlaceRegistroServicio : IEnlaceRegistroServicio
{
    private readonly IEnlaceRegistroRepositorio _repo;
    public EnlaceRegistroServicio(IEnlaceRegistroRepositorio repo) => _repo = repo;

    public Task<List<EnlaceRegistro>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<EnlaceRegistro?> ObtenerPorIdAsync(long idEnlace) => _repo.ObtenerPorIdAsync(idEnlace);
    public Task<EnlaceRegistro?> ObtenerPorTokenAsync(Guid token) => _repo.ObtenerPorTokenAsync(token);
    public Task<EnlaceRegistro?> ObtenerVigenteDeSesionAsync(long idSesion) => _repo.ObtenerVigenteDeSesionAsync(idSesion);
    public Task<bool> CrearAsync(EnlaceRegistro entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(EnlaceRegistro entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> RevocarAsync(long idEnlace) => _repo.RevocarAsync(idEnlace);
    public Task<List<EnlaceRegistro>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
}
