using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IRolPorUsuarioServicio
{
    Task<List<RolPorUsuario>> ObtenerTodosAsync(int? limite = null);
    Task<RolPorUsuario?> ObtenerPorIdAsync(long fkUsuario, string fkRol, DateOnly fechaIni);
    Task<bool> CrearAsync(RolPorUsuario entidad);
    Task<bool> ActualizarAsync(RolPorUsuario entidad);
    Task<bool> EliminarAsync(long fkUsuario, string fkRol, DateOnly fechaIni);
    Task<List<RolPorUsuario>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<RolPorUsuario> entidades);
    Task<int> ActualizarLoteAsync(List<RolPorUsuario> entidades);
}
