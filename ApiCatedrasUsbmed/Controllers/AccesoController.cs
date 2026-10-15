using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.RateLimiting;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Controllers;

/// <summary>
/// Camino B - ASISTENTE. El flujo del QR: ver la catedra, pedir la clave al correo,
/// validarla y quedar registrado.
///
/// ANONIMO: el QR se proyecta en un auditorio y el asistente no tiene credenciales.
/// Es una desviacion respecto de ApiEvalFormativaUsbmed, que solo tiene un endpoint
/// anonimo. A cambio se defiende con:
///   - limite de tasa por IP
///   - respuesta UNIFORME aunque el identificador no exista, para que el endpoint no
///     sirva para enumerar el maestro de 14.808 personas
///   - el correo de destino se devuelve enmascarado
/// </summary>
[Route("api/acceso")]
[ApiController]
[AllowAnonymous]
[EnableRateLimiting("acceso-publico")]
public class AccesoController : ControllerBase
{
    private readonly IProcesoAccesoServicio _svc;
    private readonly ILogger<AccesoController> _log;

    public AccesoController(IProcesoAccesoServicio svc, ILogger<AccesoController> log)
    { _svc = svc; _log = log; }

    private string? Ip => HttpContext.Connection.RemoteIpAddress?.ToString();

    /// <summary>
    /// Pantalla de bienvenida: que catedra es y si la ventana esta abierta.
    /// Alimenta "el sistema debe mostrar una pantalla con imagen corporativa y el titulo
    /// de la catedra abierta a la que asiste".
    /// </summary>
    [HttpGet("enlace/{token:guid}")]
    public async Task<IActionResult> ObtenerEnlace(Guid token)
    {
        var e = await _svc.ObtenerEnlacePublicoAsync(token);
        return e is null
            ? NotFound(new { mensaje = "El enlace no existe." })
            : Ok(e);
    }

    [HttpPost("solicitar-clave")]
    public async Task<IActionResult> SolicitarClave([FromBody] SolicitudClave cuerpo)
    {
        try
        {
            var (enviada, correo, idClave) = await _svc.SolicitarClaveAsync(
                cuerpo.Identificador, cuerpo.Token, Ip);

            if (idClave == 0)
            {
                // Respuesta NEUTRA a proposito: no se dice si el identificador existe.
                _log.LogInformation("Solicitud de clave sin resolucion desde {Ip}", Ip);
                return Ok(new
                {
                    mensaje = "Si el identificador corresponde a una persona registrada, " +
                              "se envio una clave a su correo.",
                    enviada = false
                });
            }

            return Ok(new
            {
                mensaje = "Si el identificador corresponde a una persona registrada, " +
                          "se envio una clave a su correo.",
                id_clave = idClave,
                enviado_a = correo,
                enviada
            });
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex)
        {
            _log.LogError(ex, "Error al solicitar clave");
            return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier });
        }
    }

    [HttpPost("validar")]
    public async Task<IActionResult> Validar([FromBody] ValidacionClave cuerpo)
    {
        try
        {
            var idRegistro = await _svc.ValidarYRegistrarAsync(
                cuerpo.IdClave, cuerpo.Clave, Ip, Request.Headers.UserAgent.ToString());

            return Ok(new { mensaje = "Registro exitoso.", id_registro = idRegistro });
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex)
        {
            _log.LogError(ex, "Error al validar clave");
            return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier });
        }
    }

    /// <summary>La encuesta rapida de calidad, despues de registrarse.</summary>
    [HttpPost("registro/{idRegistro:long}/encuesta")]
    public async Task<IActionResult> ResponderEncuesta(long idRegistro, [FromBody] RespuestaEncuestaEntrada cuerpo)
    {
        try
        {
            var id = await _svc.ResponderEncuestaAsync(idRegistro, cuerpo);
            return Ok(new { mensaje = "Encuesta registrada.", id_respuesta = id });
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex)
        {
            _log.LogError(ex, "Error al responder encuesta");
            return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier });
        }
    }
}
