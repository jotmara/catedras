using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IDependenciaServicio
{
    Task<List<Dependencia>> ObtenerTodosAsync(int? limite = null);
    Task<Dependencia?> ObtenerPorIdAsync(string idDependencia);
    Task<bool> CrearAsync(Dependencia entidad);
    Task<bool> ActualizarAsync(Dependencia entidad);
    Task<bool> EliminarAsync(string idDependencia);
    Task<List<Dependencia>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<Dependencia> entidades);
    Task<int> ActualizarLoteAsync(List<Dependencia> entidades);
}
