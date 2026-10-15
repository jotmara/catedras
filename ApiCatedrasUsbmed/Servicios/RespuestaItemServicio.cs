using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class RespuestaItemServicio : IRespuestaItemServicio
{
    private readonly IRespuestaItemRepositorio _repo;
    public RespuestaItemServicio(IRespuestaItemRepositorio repo) => _repo = repo;

    public Task<List<RespuestaItem>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<RespuestaItem?> ObtenerPorIdAsync(long idItem) => _repo.ObtenerPorIdAsync(idItem);
    public Task<bool> CrearAsync(RespuestaItem entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(RespuestaItem entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idItem) => _repo.EliminarAsync(idItem);
    public Task<List<RespuestaItem>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<RespuestaItem> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<RespuestaItem> entidades) => _repo.ActualizarLoteAsync(entidades);
}
