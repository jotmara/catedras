using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IFacultadServicio
{
    Task<List<Facultad>> ObtenerTodosAsync(int? limite = null);
    Task<Facultad?> ObtenerPorIdAsync(string idFacultad);
    Task<bool> CrearAsync(Facultad entidad);
    Task<bool> ActualizarAsync(Facultad entidad);
    Task<bool> EliminarAsync(string idFacultad);
    Task<List<Facultad>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<Facultad> entidades);
    Task<int> ActualizarLoteAsync(List<Facultad> entidades);
}
