using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface ILoteMigracionServicio
{
    Task<List<LoteMigracion>> ObtenerTodosAsync(int? limite = null);
    Task<LoteMigracion?> ObtenerPorIdAsync(long idLoteMigracion);
    Task<bool> CrearAsync(LoteMigracion entidad);
    Task<bool> ActualizarAsync(LoteMigracion entidad);
    Task<bool> EliminarAsync(long idLoteMigracion);
    Task<List<LoteMigracion>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<LoteMigracion> entidades);
    Task<int> ActualizarLoteAsync(List<LoteMigracion> entidades);
}
