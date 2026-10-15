using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class LoteCargaAsistenteServicio : ILoteCargaAsistenteServicio
{
    private readonly ILoteCargaAsistenteRepositorio _repo;
    public LoteCargaAsistenteServicio(ILoteCargaAsistenteRepositorio repo) => _repo = repo;

    public Task<List<LoteCargaAsistente>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<LoteCargaAsistente?> ObtenerPorIdAsync(long idLoteCarga) => _repo.ObtenerPorIdAsync(idLoteCarga);
    public Task<bool> CrearAsync(LoteCargaAsistente entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(LoteCargaAsistente entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idLoteCarga) => _repo.EliminarAsync(idLoteCarga);
    public Task<List<LoteCargaAsistente>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<LoteCargaAsistente> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<LoteCargaAsistente> entidades) => _repo.ActualizarLoteAsync(entidades);
}
