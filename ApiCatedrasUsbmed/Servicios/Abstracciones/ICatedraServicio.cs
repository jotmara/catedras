using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface ICatedraServicio
{
    Task<List<Catedra>> ObtenerTodosAsync(int? limite = null);
    Task<Catedra?> ObtenerPorIdAsync(long idCatedra);
    Task<bool> CrearAsync(Catedra entidad);
    Task<bool> ActualizarAsync(Catedra entidad);
    Task<bool> EliminarAsync(long idCatedra);
    Task<List<Catedra>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<Catedra> entidades);
    Task<int> ActualizarLoteAsync(List<Catedra> entidades);
}
