using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class ProgramaAcademicoServicio : IProgramaAcademicoServicio
{
    private readonly IProgramaAcademicoRepositorio _repo;
    public ProgramaAcademicoServicio(IProgramaAcademicoRepositorio repo) => _repo = repo;

    public Task<List<ProgramaAcademico>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<ProgramaAcademico?> ObtenerPorIdAsync(string codigo) => _repo.ObtenerPorIdAsync(codigo);
    public Task<bool> CrearAsync(ProgramaAcademico entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(ProgramaAcademico entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(string codigo) => _repo.EliminarAsync(codigo);
    public Task<List<ProgramaAcademico>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<ProgramaAcademico> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<ProgramaAcademico> entidades) => _repo.ActualizarLoteAsync(entidades);
}
