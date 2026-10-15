using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class FacultadServicio : IFacultadServicio
{
    private readonly IFacultadRepositorio _repo;
    public FacultadServicio(IFacultadRepositorio repo) => _repo = repo;

    public Task<List<Facultad>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<Facultad?> ObtenerPorIdAsync(string idFacultad) => _repo.ObtenerPorIdAsync(idFacultad);
    public Task<bool> CrearAsync(Facultad entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(Facultad entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(string idFacultad) => _repo.EliminarAsync(idFacultad);
    public Task<List<Facultad>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<Facultad> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<Facultad> entidades) => _repo.ActualizarLoteAsync(entidades);
}
