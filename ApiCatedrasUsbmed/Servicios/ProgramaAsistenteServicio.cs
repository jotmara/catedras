using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class ProgramaAsistenteServicio : IProgramaAsistenteServicio
{
    private readonly IProgramaAsistenteRepositorio _repo;
    public ProgramaAsistenteServicio(IProgramaAsistenteRepositorio repo) => _repo = repo;

    public Task<List<ProgramaAsistente>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<ProgramaAsistente?> ObtenerPorIdAsync(long fkAsistente, string fkPrograma, string fkPeriodo) => _repo.ObtenerPorIdAsync(fkAsistente, fkPrograma, fkPeriodo);
    public Task<bool> CrearAsync(ProgramaAsistente entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(ProgramaAsistente entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long fkAsistente, string fkPrograma, string fkPeriodo) => _repo.EliminarAsync(fkAsistente, fkPrograma, fkPeriodo);
    public Task<List<ProgramaAsistente>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<ProgramaAsistente> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<ProgramaAsistente> entidades) => _repo.ActualizarLoteAsync(entidades);
}
