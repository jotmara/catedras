using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Controllers;

/// <summary>Generacion y trazabilidad del archivo plano del ASIS. Solo administracion.</summary>
[Route("api/migracion")]
[ApiController]
[Authorize(Roles = "ADMIN")]
public class MigracionController : ControllerBase
{
    private readonly IProcesoMigracionServicio _svc;
    private readonly ILogger<MigracionController> _log;

    public MigracionController(IProcesoMigracionServicio svc, ILogger<MigracionController> log)
    { _svc = svc; _log = log; }

    private IActionResult Error(Exception ex, string donde)
    {
        _log.LogError(ex, "Error en migracion: {Donde}", donde);
        return StatusCode(500, new { mensaje = "Error interno del servidor.", traceId = HttpContext.TraceIdentifier });
    }

    /// <summary>Previsualizacion en JSON de lo que va a salir en el archivo.</summary>
    [HttpGet("sesion/{idSesion:long}/previsualizar")]
    public async Task<IActionResult> Previsualizar(long idSesion)
    {
        try
        {
            var filas = await _svc.ExportarAsync(idSesion);
            return Ok(new { filas = filas.Count, columnas = 3, datos = filas });
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { return Error(ex, "previsualizar"); }
    }

    /// <summary>El archivo plano en Excel. Tres columnas, sin encabezado.</summary>
    [HttpGet("sesion/{idSesion:long}/archivo")]
    public async Task<IActionResult> Archivo(long idSesion)
    {
        try
        {
            var r = await _svc.GenerarArchivoAsync(idSesion);
            if (r is null)
                return NotFound(new
                {
                    mensaje = "No hay registros migrables en esa sesion. " +
                              "Revise /api/v_pendiente_migracion: puede haber asistentes sin ID o sin programa."
                });

            return File(r.Value.contenido,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        r.Value.nombre);
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { return Error(ex, "archivo"); }
    }

    /// <summary>Descarga directa en formato CSV compatible con ASIS/Oracle.</summary>
    [HttpGet("sesion/{idSesion:long}/csv")]
    public async Task<IActionResult> DescargarCsv(long idSesion)
    {
        try
        {
            var r = await _svc.GenerarCsvAsync(idSesion);
            if (r is null)
                return NotFound(new
                {
                    mensaje = "No hay registros migrables en esa sesion para exportar en CSV."
                });

            return File(r.Value.contenido, "text/csv; charset=utf-8", r.Value.nombre);
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { return Error(ex, "csv"); }
    }

    /// <summary>Deposita el archivo CSV directamente en la carpeta de intercambio configurada para ASIS/Oracle.</summary>
    [HttpPost("sesion/{idSesion:long}/transferir-carpeta")]
    public async Task<IActionResult> TransferirACarpeta(long idSesion, [FromQuery] string? rutaDestino)
    {
        try
        {
            var (exito, ruta, filas) = await _svc.ExportarACarpetaAsync(idSesion, rutaDestino);
            if (!exito)
                return BadRequest(new { mensaje = ruta });

            return Ok(new
            {
                mensaje = "Archivo CSV transferido exitosamente a la carpeta compartida.",
                ruta_archivo = ruta,
                total_filas = filas
            });
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { return Error(ex, "transferir-carpeta"); }
    }

    [HttpPost("sesion/{idSesion:long}/generar")]
    public async Task<IActionResult> GenerarLote(long idSesion)
    {
        try
        {
            var id = await _svc.GenerarLoteAsync(idSesion, null);
            return Ok(new { mensaje = "Lote generado", id_lote_migracion = id });
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { return Error(ex, "generar"); }
    }

    /// <summary>Cierra el ciclo con el Monitor Procesos del ASIS.</summary>
    [HttpPut("lote/{idLote:long}/resultado")]
    public async Task<IActionResult> RegistrarResultado(long idLote, [FromBody] ResultadoLote cuerpo)
    {
        try
        {
            var ok = await _svc.RegistrarResultadoAsync(idLote, cuerpo);
            return ok ? Ok(new { mensaje = "Resultado registrado" })
                      : NotFound(new { mensaje = "El lote no existe" });
        }
        catch (Npgsql.PostgresException) { throw; }
        catch (Exception ex) { return Error(ex, "resultado"); }
    }
}
