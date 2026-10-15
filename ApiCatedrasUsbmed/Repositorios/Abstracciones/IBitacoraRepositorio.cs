using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IBitacoraRepositorio
{
    Task<List<Bitacora>> ObtenerTodosAsync(int? limite = null);
    Task<Bitacora?> ObtenerPorIdAsync(long idBitacora);
    Task<bool> CrearAsync(Bitacora entidad);
    Task<bool> ActualizarAsync(Bitacora entidad);
    Task<bool> EliminarAsync(long idBitacora);
    Task<List<Bitacora>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<Bitacora> entidades);
    Task<int> ActualizarLoteAsync(List<Bitacora> entidades);
}
