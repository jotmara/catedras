using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class VEvaluacionSesionServicio : IVEvaluacionSesionServicio
{
    private readonly IVEvaluacionSesionRepositorio _repo;
    public VEvaluacionSesionServicio(IVEvaluacionSesionRepositorio repo) => _repo = repo;

    public Task<List<VEvaluacionSesion>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<List<VEvaluacionSesion>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
}
