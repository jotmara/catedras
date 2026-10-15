using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class RolPorUsuarioServicio : IRolPorUsuarioServicio
{
    private readonly IRolPorUsuarioRepositorio _repo;
    public RolPorUsuarioServicio(IRolPorUsuarioRepositorio repo) => _repo = repo;

    public Task<List<RolPorUsuario>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<RolPorUsuario?> ObtenerPorIdAsync(long fkUsuario, string fkRol, DateOnly fechaIni) => _repo.ObtenerPorIdAsync(fkUsuario, fkRol, fechaIni);
    public Task<bool> CrearAsync(RolPorUsuario entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(RolPorUsuario entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long fkUsuario, string fkRol, DateOnly fechaIni) => _repo.EliminarAsync(fkUsuario, fkRol, fechaIni);
    public Task<List<RolPorUsuario>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<RolPorUsuario> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<RolPorUsuario> entidades) => _repo.ActualizarLoteAsync(entidades);
}
