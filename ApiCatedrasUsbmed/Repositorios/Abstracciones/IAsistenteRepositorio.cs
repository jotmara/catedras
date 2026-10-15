using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IAsistenteRepositorio
{
    Task<List<Asistente>> ObtenerTodosAsync(int? limite = null);
    Task<Asistente?> ObtenerPorIdAsync(long idAsistente);
    Task<bool> CrearAsync(Asistente entidad);
    Task<bool> ActualizarAsync(Asistente entidad);
    Task<bool> EliminarAsync(long idAsistente);
    Task<List<Asistente>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<Asistente> entidades);
    Task<int> ActualizarLoteAsync(List<Asistente> entidades);
}
