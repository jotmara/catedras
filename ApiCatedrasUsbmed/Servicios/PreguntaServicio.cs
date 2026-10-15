using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class PreguntaServicio : IPreguntaServicio
{
    private readonly IPreguntaRepositorio _repo;
    public PreguntaServicio(IPreguntaRepositorio repo) => _repo = repo;

    public Task<List<Pregunta>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<Pregunta?> ObtenerPorIdAsync(long idPregunta) => _repo.ObtenerPorIdAsync(idPregunta);
    public Task<bool> CrearAsync(Pregunta entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(Pregunta entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idPregunta) => _repo.EliminarAsync(idPregunta);
    public Task<List<Pregunta>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<Pregunta> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<Pregunta> entidades) => _repo.ActualizarLoteAsync(entidades);
}
