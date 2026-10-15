using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IDocumentoAsistenteRepositorio
{
    Task<List<DocumentoAsistente>> ObtenerTodosAsync(int? limite = null);
    Task<DocumentoAsistente?> ObtenerPorIdAsync(long idDocumento);
    Task<bool> CrearAsync(DocumentoAsistente entidad);
    Task<bool> ActualizarAsync(DocumentoAsistente entidad);
    Task<bool> EliminarAsync(long idDocumento);
    Task<List<DocumentoAsistente>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<DocumentoAsistente> entidades);
    Task<int> ActualizarLoteAsync(List<DocumentoAsistente> entidades);
}
