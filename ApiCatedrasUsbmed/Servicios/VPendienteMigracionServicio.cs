using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class VPendienteMigracionServicio : IVPendienteMigracionServicio
{
    private readonly IVPendienteMigracionRepositorio _repo;
    public VPendienteMigracionServicio(IVPendienteMigracionRepositorio repo) => _repo = repo;

    public Task<List<VPendienteMigracion>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<List<VPendienteMigracion>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
}
