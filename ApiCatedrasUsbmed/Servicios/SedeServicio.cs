using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class SedeServicio : ISedeServicio
{
    private readonly ISedeRepositorio _repo;
    public SedeServicio(ISedeRepositorio repo) => _repo = repo;

    public Task<List<Sede>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<Sede?> ObtenerPorIdAsync(string idSede) => _repo.ObtenerPorIdAsync(idSede);
    public Task<bool> CrearAsync(Sede entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(Sede entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(string idSede) => _repo.EliminarAsync(idSede);
    public Task<List<Sede>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<Sede> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<Sede> entidades) => _repo.ActualizarLoteAsync(entidades);
}
