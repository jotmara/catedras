using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IAliasProgramaRepositorio
{
    Task<List<AliasPrograma>> ObtenerTodosAsync(int? limite = null);
    Task<AliasPrograma?> ObtenerPorIdAsync(long idAlias);
    Task<bool> CrearAsync(AliasPrograma entidad);
    Task<bool> ActualizarAsync(AliasPrograma entidad);
    Task<bool> EliminarAsync(long idAlias);
    Task<List<AliasPrograma>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<AliasPrograma> entidades);
    Task<int> ActualizarLoteAsync(List<AliasPrograma> entidades);
}
