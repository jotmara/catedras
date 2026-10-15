using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Controllers;

/// <summary>Control de RN-15. Debe devolver siempre cero filas.</summary>
[Route("api/v_control_ventana")]
[ApiController]
[Authorize]
public class VControlVentanaController : ControllerBase
{
    private readonly IVControlVentanaServicio _svc;
    private readonly ILogger<VControlVentanaController> _log;

    public VControlVentanaController(IVControlVentanaServicio svc, ILogger<VControlVentanaController> log)
    { _svc = svc; _log = log; }

    [HttpGet]
    public async Task<IActionResult> ObtenerTodos([FromQuery] int? limite = null)
    {
        try
        {
            var filas = await _svc.ObtenerTodosAsync(limite);
            return Ok(new
            {
                control = "RN-15 - registros fuera de ventana",
                debe_ser_cero = 0,
                encontrados = filas.Count,
                filas
            });
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex)
        {
            _log.LogError(ex, "Error en v_control_ventana");
            return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier });
        }
    }
}
