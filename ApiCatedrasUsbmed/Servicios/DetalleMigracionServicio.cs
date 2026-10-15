using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class DetalleMigracionServicio : IDetalleMigracionServicio
{
    private readonly IDetalleMigracionRepositorio _repo;
    public DetalleMigracionServicio(IDetalleMigracionRepositorio repo) => _repo = repo;

    public Task<List<DetalleMigracion>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<DetalleMigracion?> ObtenerPorIdAsync(long idDetalle) => _repo.ObtenerPorIdAsync(idDetalle);
    public Task<bool> CrearAsync(DetalleMigracion entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(DetalleMigracion entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idDetalle) => _repo.EliminarAsync(idDetalle);
    public Task<List<DetalleMigracion>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<DetalleMigracion> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<DetalleMigracion> entidades) => _repo.ActualizarLoteAsync(entidades);
}
