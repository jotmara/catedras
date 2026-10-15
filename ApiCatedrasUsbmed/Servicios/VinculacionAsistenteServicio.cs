using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class VinculacionAsistenteServicio : IVinculacionAsistenteServicio
{
    private readonly IVinculacionAsistenteRepositorio _repo;
    public VinculacionAsistenteServicio(IVinculacionAsistenteRepositorio repo) => _repo = repo;

    public Task<List<VinculacionAsistente>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<VinculacionAsistente?> ObtenerPorIdAsync(long fkAsistente, string fkTipoVinculacion, DateOnly fechaIni) => _repo.ObtenerPorIdAsync(fkAsistente, fkTipoVinculacion, fechaIni);
    public Task<bool> CrearAsync(VinculacionAsistente entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(VinculacionAsistente entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long fkAsistente, string fkTipoVinculacion, DateOnly fechaIni) => _repo.EliminarAsync(fkAsistente, fkTipoVinculacion, fechaIni);
    public Task<List<VinculacionAsistente>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<VinculacionAsistente> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<VinculacionAsistente> entidades) => _repo.ActualizarLoteAsync(entidades);
}
