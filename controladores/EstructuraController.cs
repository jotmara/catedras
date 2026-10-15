using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Controllers;

/// <summary>Metadata de las tablas, leida de information_schema.</summary>
[Route("api/estructuras")]
[ApiController]
[Authorize]
public class EstructuraController : ControllerBase
{
    private readonly IEstructuraServicio _svc;
    private readonly ILogger<EstructuraController> _log;

    public EstructuraController(IEstructuraServicio svc, ILogger<EstructuraController> log)
    { _svc = svc; _log = log; }

    [HttpGet]
    public async Task<IActionResult> Listar()
    {
        try { return Ok(await _svc.ListarTablasAsync()); }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex)
        {
            _log.LogError(ex, "Error al listar tablas");
            return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier });
        }
    }

    [HttpGet("{tabla}/modelo")]
    public async Task<IActionResult> ObtenerModelo(string tabla)
    {
        try
        {
            var cols = await _svc.ObtenerColumnasAsync(tabla);
            return cols.Count == 0
                ? NotFound(new { mensaje = $"La tabla '{tabla}' no existe en el esquema catedras." })
                : Ok(cols);
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex)
        {
            _log.LogError(ex, "Error al obtener modelo de {Tabla}", tabla);
            return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier });
        }
    }
}
