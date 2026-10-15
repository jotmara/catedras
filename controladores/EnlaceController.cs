using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Controllers;

/// <summary>Emision de enlaces y QR. Solo administracion.</summary>
[Route("api/enlace")]
[ApiController]
[Authorize(Roles = "ADMIN,COORDINADOR")]
public class EnlaceController : ControllerBase
{
    private readonly IProcesoEnlaceServicio _svc;
    private readonly ILogger<EnlaceController> _log;

    public EnlaceController(IProcesoEnlaceServicio svc, ILogger<EnlaceController> log)
    { _svc = svc; _log = log; }

    /// <summary>El boton: genera el QR y la URL de una sesion, con su ventana horaria.</summary>
    [HttpPost("emitir")]
    public async Task<IActionResult> Emitir([FromBody] EmisionEnlace cuerpo)
    {
        try
        {
            var id = await _svc.EmitirAsync(cuerpo.IdSesion, cuerpo.MinutosAntes, cuerpo.MinutosDespues, null);
            return Ok(new { mensaje = "Enlace emitido", id_enlace = id });
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex)
        {
            _log.LogError(ex, "Error al emitir enlace");
            return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier });
        }
    }

    [HttpGet("{idEnlace:long}/qr")]
    [AllowAnonymous]
    [Produces("image/png")]
    public async Task<IActionResult> Qr(long idEnlace)
    {
        try
        {
            var png = await _svc.GenerarQrAsync(idEnlace);
            return png is null ? NotFound(new { mensaje = "El enlace no existe." }) : File(png, "image/png");
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex)
        {
            _log.LogError(ex, "Error al generar QR");
            return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier });
        }
    }

    /// <summary>El numero que hoy se busca a mano en un listado de 5.711 filas.</summary>
    [HttpGet("siguiente-reunion/{idEventoAsis}")]
    public async Task<IActionResult> SiguienteReunion(string idEventoAsis)
    {
        try
        {
            var n = await _svc.SiguienteReunionAsync(idEventoAsis);
            return Ok(new
            {
                id_evento_asis = idEventoAsis,
                siguiente_reunion = n,
                advertencia = "Es una PROPUESTA. Para catedras que ya existen en el ASIS la " +
                              "autoridad del consecutivo es el ASIS: verifique numero_reunion_asis."
            });
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex)
        {
            _log.LogError(ex, "Error al calcular la siguiente reunion");
            return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier });
        }
    }
}
