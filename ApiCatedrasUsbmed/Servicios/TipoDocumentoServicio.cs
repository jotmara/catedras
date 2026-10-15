using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class TipoDocumentoServicio : ITipoDocumentoServicio
{
    private readonly ITipoDocumentoRepositorio _repo;
    public TipoDocumentoServicio(ITipoDocumentoRepositorio repo) => _repo = repo;

    public Task<List<TipoDocumento>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<TipoDocumento?> ObtenerPorIdAsync(string idTipoDocumento) => _repo.ObtenerPorIdAsync(idTipoDocumento);
    public Task<bool> CrearAsync(TipoDocumento entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(TipoDocumento entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(string idTipoDocumento) => _repo.EliminarAsync(idTipoDocumento);
    public Task<List<TipoDocumento>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<TipoDocumento> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<TipoDocumento> entidades) => _repo.ActualizarLoteAsync(entidades);
}
