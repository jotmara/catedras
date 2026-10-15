using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class TipoPreguntaServicio : ITipoPreguntaServicio
{
    private readonly ITipoPreguntaRepositorio _repo;
    public TipoPreguntaServicio(ITipoPreguntaRepositorio repo) => _repo = repo;

    public Task<List<TipoPregunta>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<TipoPregunta?> ObtenerPorIdAsync(string idTipoPregunta) => _repo.ObtenerPorIdAsync(idTipoPregunta);
    public Task<bool> CrearAsync(TipoPregunta entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(TipoPregunta entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(string idTipoPregunta) => _repo.EliminarAsync(idTipoPregunta);
    public Task<List<TipoPregunta>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<TipoPregunta> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<TipoPregunta> entidades) => _repo.ActualizarLoteAsync(entidades);
}
