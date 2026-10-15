namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IProcesoEnlaceServicio
{
    Task<long> EmitirAsync(long idSesion, int? minutosAntes, int? minutosDespues, long? idUsuario);
    Task<short> SiguienteReunionAsync(string idEventoAsis);
    Task<byte[]?> GenerarQrAsync(long idEnlace);
}
