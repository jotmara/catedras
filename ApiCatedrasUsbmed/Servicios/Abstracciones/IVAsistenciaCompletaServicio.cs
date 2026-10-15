using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IVAsistenciaCompletaServicio
{
    Task<List<VAsistenciaCompleta>> ObtenerTodosAsync(int? limite = null);
    Task<List<VAsistenciaCompleta>> ObtenerPorColumnaAsync(string columna, string valor);
}
