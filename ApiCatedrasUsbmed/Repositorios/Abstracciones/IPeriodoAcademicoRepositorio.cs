using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IPeriodoAcademicoRepositorio
{
    Task<List<PeriodoAcademico>> ObtenerTodosAsync(int? limite = null);
    Task<PeriodoAcademico?> ObtenerPorIdAsync(string idPeriodo);
    Task<bool> CrearAsync(PeriodoAcademico entidad);
    Task<bool> ActualizarAsync(PeriodoAcademico entidad);
    Task<bool> EliminarAsync(string idPeriodo);
    Task<List<PeriodoAcademico>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<PeriodoAcademico> entidades);
    Task<int> ActualizarLoteAsync(List<PeriodoAcademico> entidades);
}
