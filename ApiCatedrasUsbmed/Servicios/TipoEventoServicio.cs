using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class TipoEventoServicio : ITipoEventoServicio
{
    private readonly ITipoEventoRepositorio _repo;
    public TipoEventoServicio(ITipoEventoRepositorio repo) => _repo = repo;

    public Task<List<TipoEvento>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<TipoEvento?> ObtenerPorIdAsync(string idTipoEvento) => _repo.ObtenerPorIdAsync(idTipoEvento);
    public Task<bool> CrearAsync(TipoEvento entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(TipoEvento entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(string idTipoEvento) => _repo.EliminarAsync(idTipoEvento);
    public Task<List<TipoEvento>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<TipoEvento> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<TipoEvento> entidades) => _repo.ActualizarLoteAsync(entidades);
}
