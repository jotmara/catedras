using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class ClaveAccesoServicio : IClaveAccesoServicio
{
    private readonly IClaveAccesoRepositorio _repo;
    public ClaveAccesoServicio(IClaveAccesoRepositorio repo) => _repo = repo;

    public Task<List<ClaveAcceso>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<ClaveAcceso?> ObtenerPorIdAsync(long idClave) => _repo.ObtenerPorIdAsync(idClave);
    public Task<bool> CrearAsync(ClaveAcceso entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(ClaveAcceso entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idClave) => _repo.EliminarAsync(idClave);
    public Task<List<ClaveAcceso>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<ClaveAcceso> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<ClaveAcceso> entidades) => _repo.ActualizarLoteAsync(entidades);
}
