using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Controllers;

/// <summary>
/// CRUD de enlaces. Para EMITIR uno hay que usar POST /api/enlace/emitir, que llama al
/// procedimiento sp_emitir_enlace: revoca el anterior, calcula la ventana desde los
/// parametros y genera el token. Crear uno por aqui saltaria esa logica.
/// </summary>
[Route("api/enlace_registro")]
[ApiController]
[Authorize]
public class EnlaceRegistroController : ControllerBase
{
    private readonly IEnlaceRegistroServicio _svc;
    private readonly ILogger<EnlaceRegistroController> _log;

    public EnlaceRegistroController(IEnlaceRegistroServicio svc, ILogger<EnlaceRegistroController> log)
    { _svc = svc; _log = log; }

    private IActionResult Error(Exception ex)
    {
        _log.LogError(ex, "Error en enlace_registro");
        return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier });
    }

    [HttpGet]
    public async Task<IActionResult> ObtenerTodos([FromQuery] int? limite = null)
    {
        try { return Ok(await _svc.ObtenerTodosAsync(limite)); }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { return Error(ex); }
    }

    [HttpGet("{idEnlace:long}")]
    public async Task<IActionResult> ObtenerPorId(long idEnlace)
    {
        try
        {
            var r = await _svc.ObtenerPorIdAsync(idEnlace);
            return r is null ? NotFound(new { mensaje = "Registro no encontrado" }) : Ok(r);
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { return Error(ex); }
    }

    [HttpGet("sesion/{idSesion:long}/vigente")]
    public async Task<IActionResult> ObtenerVigente(long idSesion)
    {
        try
        {
            var r = await _svc.ObtenerVigenteDeSesionAsync(idSesion);
            return r is null ? NotFound(new { mensaje = "La sesion no tiene enlace vigente" }) : Ok(r);
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { return Error(ex); }
    }

    [HttpPost]
    public async Task<IActionResult> Crear([FromBody] EnlaceRegistro entidad)
    {
        try
        {
            var ok = await _svc.CrearAsync(entidad);
            return ok ? Ok(new { mensaje = "Registro creado" }) : BadRequest(new { mensaje = "No se pudo crear" });
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { return Error(ex); }
    }

    [HttpPut("{idEnlace:long}")]
    public async Task<IActionResult> Actualizar(long idEnlace, [FromBody] EnlaceRegistro entidad)
    {
        try
        {
            entidad.IdEnlace = idEnlace;
            var ok = await _svc.ActualizarAsync(entidad);
            return ok ? Ok(new { mensaje = "Registro actualizado" }) : NotFound(new { mensaje = "Registro no encontrado" });
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { return Error(ex); }
    }

    /// <summary>Revoca el enlace (marca revocado_en). No borra: RN-32.</summary>
    [HttpDelete("{idEnlace:long}")]
    public async Task<IActionResult> Revocar(long idEnlace)
    {
        try
        {
            var ok = await _svc.RevocarAsync(idEnlace);
            return ok ? Ok(new { mensaje = "Enlace revocado" })
                      : NotFound(new { mensaje = "No existe o ya estaba revocado" });
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { return Error(ex); }
    }

    [HttpGet("por/{columna}/{valor}")]
    public async Task<IActionResult> ObtenerPorColumna(string columna, string valor)
    {
        try { return Ok(await _svc.ObtenerPorColumnaAsync(columna, valor)); }
        catch (ArgumentException ex) { return BadRequest(new { mensaje = ex.Message }); }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { return Error(ex); }
    }
}
