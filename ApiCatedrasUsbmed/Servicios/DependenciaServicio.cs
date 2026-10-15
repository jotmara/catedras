using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class DependenciaServicio : IDependenciaServicio
{
    private readonly IDependenciaRepositorio _repo;
    public DependenciaServicio(IDependenciaRepositorio repo) => _repo = repo;

    public Task<List<Dependencia>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<Dependencia?> ObtenerPorIdAsync(string idDependencia) => _repo.ObtenerPorIdAsync(idDependencia);
    public Task<bool> CrearAsync(Dependencia entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(Dependencia entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(string idDependencia) => _repo.EliminarAsync(idDependencia);
    public Task<List<Dependencia>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<Dependencia> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<Dependencia> entidades) => _repo.ActualizarLoteAsync(entidades);
}
