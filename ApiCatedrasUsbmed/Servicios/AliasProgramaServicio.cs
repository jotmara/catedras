using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class AliasProgramaServicio : IAliasProgramaServicio
{
    private readonly IAliasProgramaRepositorio _repo;
    public AliasProgramaServicio(IAliasProgramaRepositorio repo) => _repo = repo;

    public Task<List<AliasPrograma>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<AliasPrograma?> ObtenerPorIdAsync(long idAlias) => _repo.ObtenerPorIdAsync(idAlias);
    public Task<bool> CrearAsync(AliasPrograma entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(AliasPrograma entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idAlias) => _repo.EliminarAsync(idAlias);
    public Task<List<AliasPrograma>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<AliasPrograma> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<AliasPrograma> entidades) => _repo.ActualizarLoteAsync(entidades);
}
