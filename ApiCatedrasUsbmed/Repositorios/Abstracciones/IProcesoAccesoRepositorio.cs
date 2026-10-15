using ApiCatedrasUsbmed.Modelos;

namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IProcesoAccesoRepositorio
{
    Task<EnlacePublico?> ObtenerEnlacePublicoAsync(Guid token);
    Task<ResultadoSolicitudClave?> SolicitarClaveAsync(string identificador, Guid token, string? ip);
    Task<long> ValidarYRegistrarAsync(long idClave, string clave, string? ip, string? userAgent);
    Task<long> ResolverAsistenteAsync(string identificador);
    Task<long> ResponderEncuestaAsync(long idRegistro, string respuestasJson);
}
