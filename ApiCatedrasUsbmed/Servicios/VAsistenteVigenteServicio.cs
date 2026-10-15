using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class VAsistenteVigenteServicio : IVAsistenteVigenteServicio
{
    private readonly IVAsistenteVigenteRepositorio _repo;
    public VAsistenteVigenteServicio(IVAsistenteVigenteRepositorio repo) => _repo = repo;

    public Task<List<VAsistenteVigente>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<List<VAsistenteVigente>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
}
