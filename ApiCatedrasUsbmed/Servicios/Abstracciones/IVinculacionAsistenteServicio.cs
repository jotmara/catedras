using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IVinculacionAsistenteServicio
{
    Task<List<VinculacionAsistente>> ObtenerTodosAsync(int? limite = null);
    Task<VinculacionAsistente?> ObtenerPorIdAsync(long fkAsistente, string fkTipoVinculacion, DateOnly fechaIni);
    Task<bool> CrearAsync(VinculacionAsistente entidad);
    Task<bool> ActualizarAsync(VinculacionAsistente entidad);
    Task<bool> EliminarAsync(long fkAsistente, string fkTipoVinculacion, DateOnly fechaIni);
    Task<List<VinculacionAsistente>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<VinculacionAsistente> entidades);
    Task<int> ActualizarLoteAsync(List<VinculacionAsistente> entidades);
}
