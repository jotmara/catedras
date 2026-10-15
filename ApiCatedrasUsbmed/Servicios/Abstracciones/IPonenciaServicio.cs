using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IPonenciaServicio
{
    Task<List<Ponencia>> ObtenerTodosAsync(int? limite = null);
    Task<Ponencia?> ObtenerPorIdAsync(long fkSesion, long fkAsistente, string rol);
    Task<bool> CrearAsync(Ponencia entidad);
    Task<bool> ActualizarAsync(Ponencia entidad);
    Task<bool> EliminarAsync(long fkSesion, long fkAsistente, string rol);
    Task<List<Ponencia>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<Ponencia> entidades);
    Task<int> ActualizarLoteAsync(List<Ponencia> entidades);
}
