using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class PeriodoAcademicoServicio : IPeriodoAcademicoServicio
{
    private readonly IPeriodoAcademicoRepositorio _repo;
    public PeriodoAcademicoServicio(IPeriodoAcademicoRepositorio repo) => _repo = repo;

    public Task<List<PeriodoAcademico>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<PeriodoAcademico?> ObtenerPorIdAsync(string idPeriodo) => _repo.ObtenerPorIdAsync(idPeriodo);
    public Task<bool> CrearAsync(PeriodoAcademico entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(PeriodoAcademico entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(string idPeriodo) => _repo.EliminarAsync(idPeriodo);
    public Task<List<PeriodoAcademico>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<PeriodoAcademico> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<PeriodoAcademico> entidades) => _repo.ActualizarLoteAsync(entidades);
}
