using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IProgramaAsistenteServicio
{
    Task<List<ProgramaAsistente>> ObtenerTodosAsync(int? limite = null);
    Task<ProgramaAsistente?> ObtenerPorIdAsync(long fkAsistente, string fkPrograma, string fkPeriodo);
    Task<bool> CrearAsync(ProgramaAsistente entidad);
    Task<bool> ActualizarAsync(ProgramaAsistente entidad);
    Task<bool> EliminarAsync(long fkAsistente, string fkPrograma, string fkPeriodo);
    Task<List<ProgramaAsistente>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<ProgramaAsistente> entidades);
    Task<int> ActualizarLoteAsync(List<ProgramaAsistente> entidades);
}
