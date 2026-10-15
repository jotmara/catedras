using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class LoteMigracionServicio : ILoteMigracionServicio
{
    private readonly ILoteMigracionRepositorio _repo;
    public LoteMigracionServicio(ILoteMigracionRepositorio repo) => _repo = repo;

    public Task<List<LoteMigracion>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<LoteMigracion?> ObtenerPorIdAsync(long idLoteMigracion) => _repo.ObtenerPorIdAsync(idLoteMigracion);
    public Task<bool> CrearAsync(LoteMigracion entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(LoteMigracion entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idLoteMigracion) => _repo.EliminarAsync(idLoteMigracion);
    public Task<List<LoteMigracion>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<LoteMigracion> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<LoteMigracion> entidades) => _repo.ActualizarLoteAsync(entidades);
}
