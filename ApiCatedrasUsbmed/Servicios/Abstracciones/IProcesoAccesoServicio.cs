using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IProcesoAccesoServicio
{
    Task<EnlacePublico?> ObtenerEnlacePublicoAsync(Guid token);
    Task<(bool enviada, string correoEnmascarado, long idClave)> SolicitarClaveAsync(
        string identificador, Guid token, string? ip);
    Task<long> ValidarYRegistrarAsync(long idClave, string clave, string? ip, string? userAgent);
    Task<long> ResponderEncuestaAsync(long idRegistro, RespuestaEncuestaEntrada entrada);
}
