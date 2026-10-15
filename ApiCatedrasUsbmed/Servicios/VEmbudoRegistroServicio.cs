using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class VEmbudoRegistroServicio : IVEmbudoRegistroServicio
{
    private readonly IVEmbudoRegistroRepositorio _repo;
    public VEmbudoRegistroServicio(IVEmbudoRegistroRepositorio repo) => _repo = repo;

    public Task<List<VEmbudoRegistro>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<List<VEmbudoRegistro>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
}
