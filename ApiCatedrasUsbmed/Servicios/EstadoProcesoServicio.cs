using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class EstadoProcesoServicio : IEstadoProcesoServicio
{
    private readonly IEstadoProcesoRepositorio _repo;
    public EstadoProcesoServicio(IEstadoProcesoRepositorio repo) => _repo = repo;

    public Task<List<EstadoProceso>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<EstadoProceso?> ObtenerPorIdAsync(string idEstado) => _repo.ObtenerPorIdAsync(idEstado);
    public Task<bool> CrearAsync(EstadoProceso entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(EstadoProceso entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(string idEstado) => _repo.EliminarAsync(idEstado);
    public Task<List<EstadoProceso>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<EstadoProceso> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<EstadoProceso> entidades) => _repo.ActualizarLoteAsync(entidades);
}
