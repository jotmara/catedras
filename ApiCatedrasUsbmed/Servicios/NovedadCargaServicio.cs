using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class NovedadCargaServicio : INovedadCargaServicio
{
    private readonly INovedadCargaRepositorio _repo;
    public NovedadCargaServicio(INovedadCargaRepositorio repo) => _repo = repo;

    public Task<List<NovedadCarga>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<NovedadCarga?> ObtenerPorIdAsync(long idNovedad) => _repo.ObtenerPorIdAsync(idNovedad);
    public Task<bool> CrearAsync(NovedadCarga entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(NovedadCarga entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idNovedad) => _repo.EliminarAsync(idNovedad);
    public Task<List<NovedadCarga>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<NovedadCarga> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<NovedadCarga> entidades) => _repo.ActualizarLoteAsync(entidades);
}
