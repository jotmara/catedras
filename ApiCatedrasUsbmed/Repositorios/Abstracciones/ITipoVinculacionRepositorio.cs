using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface ITipoVinculacionRepositorio
{
    Task<List<TipoVinculacion>> ObtenerTodosAsync(int? limite = null);
    Task<TipoVinculacion?> ObtenerPorIdAsync(string idTipoVinculacion);
    Task<bool> CrearAsync(TipoVinculacion entidad);
    Task<bool> ActualizarAsync(TipoVinculacion entidad);
    Task<bool> EliminarAsync(string idTipoVinculacion);
    Task<List<TipoVinculacion>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<TipoVinculacion> entidades);
    Task<int> ActualizarLoteAsync(List<TipoVinculacion> entidades);
}
