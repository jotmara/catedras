using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface ILoteCargaAsistenteServicio
{
    Task<List<LoteCargaAsistente>> ObtenerTodosAsync(int? limite = null);
    Task<LoteCargaAsistente?> ObtenerPorIdAsync(long idLoteCarga);
    Task<bool> CrearAsync(LoteCargaAsistente entidad);
    Task<bool> ActualizarAsync(LoteCargaAsistente entidad);
    Task<bool> EliminarAsync(long idLoteCarga);
    Task<List<LoteCargaAsistente>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<LoteCargaAsistente> entidades);
    Task<int> ActualizarLoteAsync(List<LoteCargaAsistente> entidades);
}
