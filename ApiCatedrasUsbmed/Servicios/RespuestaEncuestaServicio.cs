using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class RespuestaEncuestaServicio : IRespuestaEncuestaServicio
{
    private readonly IRespuestaEncuestaRepositorio _repo;
    public RespuestaEncuestaServicio(IRespuestaEncuestaRepositorio repo) => _repo = repo;

    public Task<List<RespuestaEncuesta>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<RespuestaEncuesta?> ObtenerPorIdAsync(long idRespuesta) => _repo.ObtenerPorIdAsync(idRespuesta);
    public Task<bool> CrearAsync(RespuestaEncuesta entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(RespuestaEncuesta entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idRespuesta) => _repo.EliminarAsync(idRespuesta);
    public Task<List<RespuestaEncuesta>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<RespuestaEncuesta> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<RespuestaEncuesta> entidades) => _repo.ActualizarLoteAsync(entidades);
}
