using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface ITipoDocumentoServicio
{
    Task<List<TipoDocumento>> ObtenerTodosAsync(int? limite = null);
    Task<TipoDocumento?> ObtenerPorIdAsync(string idTipoDocumento);
    Task<bool> CrearAsync(TipoDocumento entidad);
    Task<bool> ActualizarAsync(TipoDocumento entidad);
    Task<bool> EliminarAsync(string idTipoDocumento);
    Task<List<TipoDocumento>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<TipoDocumento> entidades);
    Task<int> ActualizarLoteAsync(List<TipoDocumento> entidades);
}
