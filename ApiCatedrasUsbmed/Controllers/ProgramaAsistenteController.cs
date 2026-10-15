using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Controllers;

[Route("api/programa_asistente")]
[ApiController]
[Authorize]
public class ProgramaAsistenteController : ControllerBase
{
    private readonly IProgramaAsistenteServicio _svc;
    private readonly ILogger<ProgramaAsistenteController> _log;

    public ProgramaAsistenteController(IProgramaAsistenteServicio svc, ILogger<ProgramaAsistenteController> log) { _svc = svc; _log = log; }

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
        catch (Exception ex) { _log.LogError(ex, "Error en programa_asistente"); return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier }); }
    }

    [HttpGet("{fkAsistente}/{fkPrograma}/{fkPeriodo}")]
    public async Task<IActionResult> ObtenerPorId(long fkAsistente, string fkPrograma, string fkPeriodo)
    {
        try
        {
            var r = await _svc.ObtenerPorIdAsync(fkAsistente, fkPrograma, fkPeriodo);
            return r is null ? NotFound(new { mensaje = "Registro no encontrado" }) : Ok(r);
        }
        catch (ArgumentException ex) { return BadRequest(new { mensaje = ex.Message }); }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { _log.LogError(ex, "Error en programa_asistente"); return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier }); }
    }

    [HttpPost]
    public async Task<IActionResult> Crear([FromBody] ProgramaAsistente entidad)
    {
        try
        {
            var ok = await _svc.CrearAsync(entidad);
            return ok ? Ok(new { mensaje = "Registro creado" })
                      : BadRequest(new { mensaje = "No se pudo crear" });
        }
        catch (ArgumentException ex) { return BadRequest(new { mensaje = ex.Message }); }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { _log.LogError(ex, "Error en programa_asistente"); return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier }); }
    }

    [HttpPut("{fkAsistente}/{fkPrograma}/{fkPeriodo}")]
    public async Task<IActionResult> Actualizar(long fkAsistente, string fkPrograma, string fkPeriodo, [FromBody] ProgramaAsistente entidad)
    {
        try
        {
            var ok = await _svc.ActualizarAsync(entidad);
            return ok ? Ok(new { mensaje = "Registro actualizado" })
                      : NotFound(new { mensaje = "Registro no encontrado" });
        }
        catch (ArgumentException ex) { return BadRequest(new { mensaje = ex.Message }); }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { _log.LogError(ex, "Error en programa_asistente"); return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier }); }
    }

    /// <summary>
    /// RN-32: en esta base DELETE esta revocado para todos los roles. El endpoint existe
    /// para que el contrato sea honesto y explique el motivo, en vez de anunciar en Swagger
    /// una operacion que siempre fallaria con error de permisos.
    /// </summary>
    [HttpDelete("{fkAsistente}/{fkPrograma}/{fkPeriodo}")]
    public IActionResult Eliminar(long fkAsistente, string fkPrograma, string fkPeriodo) =>
        StatusCode(405, new { mensaje = "RN-32: en este sistema no se elimina. Use PUT sobre la columna de baja logica." });

    [HttpGet("por/{columna}/{valor}")]
    public async Task<IActionResult> ObtenerPorColumna(string columna, string valor)
    {
        try { return Ok(await _svc.ObtenerPorColumnaAsync(columna, valor)); }
        catch (ArgumentException ex) { return BadRequest(new { mensaje = ex.Message }); }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { _log.LogError(ex, "Error en programa_asistente"); return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier }); }
    }

    [HttpPost("masivo")]
    public async Task<IActionResult> CrearMasivo([FromBody] List<ProgramaAsistente> entidades)
    {
        try { var n = await _svc.CrearMasivoAsync(entidades); return Ok(new { mensaje = $"{n} registro(s) creado(s)", filas = n }); }
        catch (ArgumentException ex) { return BadRequest(new { mensaje = ex.Message }); }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { _log.LogError(ex, "Error en programa_asistente"); return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier }); }
    }

    [HttpPut("lote")]
    public async Task<IActionResult> ActualizarLote([FromBody] List<ProgramaAsistente> entidades)
    {
        try { var n = await _svc.ActualizarLoteAsync(entidades); return Ok(new { mensaje = $"{n} registro(s) actualizado(s)", filas = n }); }
        catch (ArgumentException ex) { return BadRequest(new { mensaje = ex.Message }); }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { _log.LogError(ex, "Error en programa_asistente"); return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier }); }
    }
}
