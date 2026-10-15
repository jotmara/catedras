using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class DocumentoAsistenteServicio : IDocumentoAsistenteServicio
{
    private readonly IDocumentoAsistenteRepositorio _repo;
    public DocumentoAsistenteServicio(IDocumentoAsistenteRepositorio repo) => _repo = repo;

    public Task<List<DocumentoAsistente>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<DocumentoAsistente?> ObtenerPorIdAsync(long idDocumento) => _repo.ObtenerPorIdAsync(idDocumento);
    public Task<bool> CrearAsync(DocumentoAsistente entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(DocumentoAsistente entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idDocumento) => _repo.EliminarAsync(idDocumento);
    public Task<List<DocumentoAsistente>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<DocumentoAsistente> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<DocumentoAsistente> entidades) => _repo.ActualizarLoteAsync(entidades);
}
