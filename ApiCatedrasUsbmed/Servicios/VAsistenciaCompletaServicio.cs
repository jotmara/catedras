using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class VAsistenciaCompletaServicio : IVAsistenciaCompletaServicio
{
    private readonly IVAsistenciaCompletaRepositorio _repo;
    public VAsistenciaCompletaServicio(IVAsistenciaCompletaRepositorio repo) => _repo = repo;

    public Task<List<VAsistenciaCompleta>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<List<VAsistenciaCompleta>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
}
