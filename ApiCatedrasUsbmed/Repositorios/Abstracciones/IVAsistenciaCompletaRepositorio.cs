using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

/// <summary>Vista de solo lectura.</summary>
public interface IVAsistenciaCompletaRepositorio
{
    Task<List<VAsistenciaCompleta>> ObtenerTodosAsync(int? limite = null);
    Task<List<VAsistenciaCompleta>> ObtenerPorColumnaAsync(string columna, string valor);
}
