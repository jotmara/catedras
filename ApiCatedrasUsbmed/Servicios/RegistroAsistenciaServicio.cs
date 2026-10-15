using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class RegistroAsistenciaServicio : IRegistroAsistenciaServicio
{
    private readonly IRegistroAsistenciaRepositorio _repo;
    public RegistroAsistenciaServicio(IRegistroAsistenciaRepositorio repo) => _repo = repo;

    public Task<List<RegistroAsistencia>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<RegistroAsistencia?> ObtenerPorIdAsync(long idRegistro) => _repo.ObtenerPorIdAsync(idRegistro);
    public Task<bool> CrearAsync(RegistroAsistencia entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(RegistroAsistencia entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idRegistro) => _repo.EliminarAsync(idRegistro);
    public Task<List<RegistroAsistencia>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<RegistroAsistencia> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<RegistroAsistencia> entidades) => _repo.ActualizarLoteAsync(entidades);
}
