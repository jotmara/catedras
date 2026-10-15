using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IRegistroAsistenciaServicio
{
    Task<List<RegistroAsistencia>> ObtenerTodosAsync(int? limite = null);
    Task<RegistroAsistencia?> ObtenerPorIdAsync(long idRegistro);
    Task<bool> CrearAsync(RegistroAsistencia entidad);
    Task<bool> ActualizarAsync(RegistroAsistencia entidad);
    Task<bool> EliminarAsync(long idRegistro);
    Task<List<RegistroAsistencia>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<RegistroAsistencia> entidades);
    Task<int> ActualizarLoteAsync(List<RegistroAsistencia> entidades);
}
