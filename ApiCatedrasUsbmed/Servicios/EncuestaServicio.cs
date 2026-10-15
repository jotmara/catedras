using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class EncuestaServicio : IEncuestaServicio
{
    private readonly IEncuestaRepositorio _repo;
    public EncuestaServicio(IEncuestaRepositorio repo) => _repo = repo;

    public Task<List<Encuesta>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<Encuesta?> ObtenerPorIdAsync(long idEncuesta) => _repo.ObtenerPorIdAsync(idEncuesta);
    public Task<bool> CrearAsync(Encuesta entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(Encuesta entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idEncuesta) => _repo.EliminarAsync(idEncuesta);
    public Task<List<Encuesta>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<Encuesta> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<Encuesta> entidades) => _repo.ActualizarLoteAsync(entidades);
}
