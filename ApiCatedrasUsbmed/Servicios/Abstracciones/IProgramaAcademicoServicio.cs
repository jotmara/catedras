using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IProgramaAcademicoServicio
{
    Task<List<ProgramaAcademico>> ObtenerTodosAsync(int? limite = null);
    Task<ProgramaAcademico?> ObtenerPorIdAsync(string codigo);
    Task<bool> CrearAsync(ProgramaAcademico entidad);
    Task<bool> ActualizarAsync(ProgramaAcademico entidad);
    Task<bool> EliminarAsync(string codigo);
    Task<List<ProgramaAcademico>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<ProgramaAcademico> entidades);
    Task<int> ActualizarLoteAsync(List<ProgramaAcademico> entidades);
}
