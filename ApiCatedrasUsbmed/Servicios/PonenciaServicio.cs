using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class PonenciaServicio : IPonenciaServicio
{
    private readonly IPonenciaRepositorio _repo;
    public PonenciaServicio(IPonenciaRepositorio repo) => _repo = repo;

    public Task<List<Ponencia>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<Ponencia?> ObtenerPorIdAsync(long fkSesion, long fkAsistente, string rol) => _repo.ObtenerPorIdAsync(fkSesion, fkAsistente, rol);
    public Task<bool> CrearAsync(Ponencia entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(Ponencia entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long fkSesion, long fkAsistente, string rol) => _repo.EliminarAsync(fkSesion, fkAsistente, rol);
    public Task<List<Ponencia>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<Ponencia> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<Ponencia> entidades) => _repo.ActualizarLoteAsync(entidades);
}
