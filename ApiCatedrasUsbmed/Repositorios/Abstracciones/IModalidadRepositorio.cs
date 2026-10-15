using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IModalidadRepositorio
{
    Task<List<Modalidad>> ObtenerTodosAsync(int? limite = null);
    Task<Modalidad?> ObtenerPorIdAsync(string idModalidad);
    Task<bool> CrearAsync(Modalidad entidad);
    Task<bool> ActualizarAsync(Modalidad entidad);
    Task<bool> EliminarAsync(string idModalidad);
    Task<List<Modalidad>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<Modalidad> entidades);
    Task<int> ActualizarLoteAsync(List<Modalidad> entidades);
}
