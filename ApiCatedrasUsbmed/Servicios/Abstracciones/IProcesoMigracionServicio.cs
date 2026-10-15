using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IProcesoMigracionServicio
{
    Task<List<FilaArchivoAsis>> ExportarAsync(long idSesion);
    Task<(byte[] contenido, string nombre)?> GenerarArchivoAsync(long idSesion);
    Task<(byte[] contenido, string nombre)?> GenerarCsvAsync(long idSesion);
    Task<(bool exito, string ruta, int filas)> ExportarACarpetaAsync(long idSesion, string? rutaDestino);
    Task<long> GenerarLoteAsync(long idSesion, long? idUsuario);
    Task<bool> RegistrarResultadoAsync(long idLote, ResultadoLote r);
}
