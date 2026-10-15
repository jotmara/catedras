using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface INovedadCargaRepositorio
{
    Task<List<NovedadCarga>> ObtenerTodosAsync(int? limite = null);
    Task<NovedadCarga?> ObtenerPorIdAsync(long idNovedad);
    Task<bool> CrearAsync(NovedadCarga entidad);
    Task<bool> ActualizarAsync(NovedadCarga entidad);
    Task<bool> EliminarAsync(long idNovedad);
    Task<List<NovedadCarga>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<NovedadCarga> entidades);
    Task<int> ActualizarLoteAsync(List<NovedadCarga> entidades);
}
