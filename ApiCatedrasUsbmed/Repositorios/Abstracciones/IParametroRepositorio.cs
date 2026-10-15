using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IParametroRepositorio
{
    Task<List<Parametro>> ObtenerTodosAsync(int? limite = null);
    Task<Parametro?> ObtenerPorIdAsync(string clave);
    Task<bool> CrearAsync(Parametro entidad);
    Task<bool> ActualizarAsync(Parametro entidad);
    Task<bool> EliminarAsync(string clave);
    Task<List<Parametro>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<Parametro> entidades);
    Task<int> ActualizarLoteAsync(List<Parametro> entidades);
}
