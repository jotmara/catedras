namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IProcesoEnlaceRepositorio
{
    Task<long> EmitirAsync(long idSesion, int? minutosAntes, int? minutosDespues, long? idUsuario);
    Task<short> SiguienteReunionAsync(string idEventoAsis);
    Task<(string url, string? rutaQr)?> ObtenerUrlAsync(long idEnlace);
}
