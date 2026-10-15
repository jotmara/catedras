using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class ModalidadServicio : IModalidadServicio
{
    private readonly IModalidadRepositorio _repo;
    public ModalidadServicio(IModalidadRepositorio repo) => _repo = repo;

    public Task<List<Modalidad>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<Modalidad?> ObtenerPorIdAsync(string idModalidad) => _repo.ObtenerPorIdAsync(idModalidad);
    public Task<bool> CrearAsync(Modalidad entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(Modalidad entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(string idModalidad) => _repo.EliminarAsync(idModalidad);
    public Task<List<Modalidad>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<Modalidad> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<Modalidad> entidades) => _repo.ActualizarLoteAsync(entidades);
}
