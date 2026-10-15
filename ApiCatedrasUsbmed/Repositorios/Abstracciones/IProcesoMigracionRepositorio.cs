using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IProcesoMigracionRepositorio
{
    Task<List<FilaArchivoAsis>> ExportarAsync(long idSesion);
    Task<long> GenerarLoteAsync(long idSesion, long? idUsuario);
    Task<bool> RegistrarResultadoAsync(long idLote, ResultadoLote r);
    Task<string?> NombreArchivoAsync(long idSesion);
}
