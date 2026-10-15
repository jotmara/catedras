using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Controllers;

/// <summary>Vista de solo lectura: no expone POST, PUT ni DELETE.</summary>
[Route("api/v_asistencia_completa")]
[ApiController]
[Authorize]
public class VAsistenciaCompletaController : ControllerBase
{
    private readonly IVAsistenciaCompletaServicio _svc;
    private readonly ILogger<VAsistenciaCompletaController> _log;

    public VAsistenciaCompletaController(IVAsistenciaCompletaServicio svc, ILogger<VAsistenciaCompletaController> log) { _svc = svc; _log = log; }

    /// <summary>
    /// Devuelve como maximo {Paginacion.Maximo} filas; sin `limite`, {Paginacion.PorDefecto}.
    /// El tope aplicado viaja en la cabecera X-Limite-Aplicado.
    /// </summary>
    [HttpGet]
    public async Task<IActionResult> ObtenerTodos([FromQuery] int? limite = null)
    {
        try
        {
            var filas = await _svc.ObtenerTodosAsync(limite);
            Response.Headers["X-Limite-Aplicado"] = Paginacion.Resolver(limite).ToString();
            Response.Headers["X-Filas-Devueltas"] = filas.Count.ToString();
            return Ok(filas);
        }
        catch (ArgumentException ex) { return BadRequest(new { mensaje = ex.Message }); }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { _log.LogError(ex, "Error en v_asistencia_completa"); return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier }); }
    }

    [HttpGet("por/{columna}/{valor}")]
    public async Task<IActionResult> ObtenerPorColumna(string columna, string valor)
    {
        try { return Ok(await _svc.ObtenerPorColumnaAsync(columna, valor)); }
        catch (ArgumentException ex) { return BadRequest(new { mensaje = ex.Message }); }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { _log.LogError(ex, "Error en v_asistencia_completa"); return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier }); }
    }
}
