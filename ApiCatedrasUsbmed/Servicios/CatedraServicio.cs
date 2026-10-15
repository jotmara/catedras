using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class CatedraServicio : ICatedraServicio
{
    private readonly ICatedraRepositorio _repo;
    public CatedraServicio(ICatedraRepositorio repo) => _repo = repo;

    public Task<List<Catedra>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<Catedra?> ObtenerPorIdAsync(long idCatedra) => _repo.ObtenerPorIdAsync(idCatedra);
    public Task<bool> CrearAsync(Catedra entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(Catedra entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idCatedra) => _repo.EliminarAsync(idCatedra);
    public Task<List<Catedra>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<Catedra> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<Catedra> entidades) => _repo.ActualizarLoteAsync(entidades);
}
