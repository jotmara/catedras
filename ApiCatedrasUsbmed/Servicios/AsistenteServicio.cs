using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class AsistenteServicio : IAsistenteServicio
{
    private readonly IAsistenteRepositorio _repo;
    public AsistenteServicio(IAsistenteRepositorio repo) => _repo = repo;

    public Task<List<Asistente>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<Asistente?> ObtenerPorIdAsync(long idAsistente) => _repo.ObtenerPorIdAsync(idAsistente);
    public Task<bool> CrearAsync(Asistente entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(Asistente entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idAsistente) => _repo.EliminarAsync(idAsistente);
    public Task<List<Asistente>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<Asistente> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<Asistente> entidades) => _repo.ActualizarLoteAsync(entidades);
}
