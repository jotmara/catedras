using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IConsentimientoDatosServicio
{
    Task<List<ConsentimientoDatos>> ObtenerTodosAsync(int? limite = null);
    Task<ConsentimientoDatos?> ObtenerPorIdAsync(long idConsentimiento);
    Task<bool> CrearAsync(ConsentimientoDatos entidad);
    Task<bool> ActualizarAsync(ConsentimientoDatos entidad);
    Task<bool> EliminarAsync(long idConsentimiento);
    Task<List<ConsentimientoDatos>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<ConsentimientoDatos> entidades);
    Task<int> ActualizarLoteAsync(List<ConsentimientoDatos> entidades);
}
