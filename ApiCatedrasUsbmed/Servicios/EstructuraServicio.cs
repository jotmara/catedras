using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class EstructuraServicio : IEstructuraServicio
{
    private readonly IEstructuraRepositorio _repo;
    public EstructuraServicio(IEstructuraRepositorio repo) => _repo = repo;

    public Task<List<dynamic>> ObtenerColumnasAsync(string tabla) => _repo.ObtenerColumnasAsync(tabla);
    public Task<List<string>> ListarTablasAsync() => _repo.ListarTablasAsync();
}
