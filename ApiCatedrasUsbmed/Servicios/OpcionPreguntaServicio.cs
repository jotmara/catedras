using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class OpcionPreguntaServicio : IOpcionPreguntaServicio
{
    private readonly IOpcionPreguntaRepositorio _repo;
    public OpcionPreguntaServicio(IOpcionPreguntaRepositorio repo) => _repo = repo;

    public Task<List<OpcionPregunta>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<OpcionPregunta?> ObtenerPorIdAsync(long idOpcion) => _repo.ObtenerPorIdAsync(idOpcion);
    public Task<bool> CrearAsync(OpcionPregunta entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(OpcionPregunta entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idOpcion) => _repo.EliminarAsync(idOpcion);
    public Task<List<OpcionPregunta>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<OpcionPregunta> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<OpcionPregunta> entidades) => _repo.ActualizarLoteAsync(entidades);
}
