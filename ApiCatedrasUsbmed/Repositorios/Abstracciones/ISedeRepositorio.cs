using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface ISedeRepositorio
{
    Task<List<Sede>> ObtenerTodosAsync(int? limite = null);
    Task<Sede?> ObtenerPorIdAsync(string idSede);
    Task<bool> CrearAsync(Sede entidad);
    Task<bool> ActualizarAsync(Sede entidad);
    Task<bool> EliminarAsync(string idSede);
    Task<List<Sede>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<Sede> entidades);
    Task<int> ActualizarLoteAsync(List<Sede> entidades);
}
