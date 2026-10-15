using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class TipoVinculacionServicio : ITipoVinculacionServicio
{
    private readonly ITipoVinculacionRepositorio _repo;
    public TipoVinculacionServicio(ITipoVinculacionRepositorio repo) => _repo = repo;

    public Task<List<TipoVinculacion>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<TipoVinculacion?> ObtenerPorIdAsync(string idTipoVinculacion) => _repo.ObtenerPorIdAsync(idTipoVinculacion);
    public Task<bool> CrearAsync(TipoVinculacion entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(TipoVinculacion entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(string idTipoVinculacion) => _repo.EliminarAsync(idTipoVinculacion);
    public Task<List<TipoVinculacion>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<TipoVinculacion> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<TipoVinculacion> entidades) => _repo.ActualizarLoteAsync(entidades);
}
