using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.ComponentModel.DataAnnotations;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Controllers;

/// <summary>
/// Camino A - ADMINISTRADOR. Emisor de tokens JWT, con BCrypt.
///
/// Aqui SI se distingue 404 de 401, al contrario que en /api/acceso: esta es una pantalla
/// de administracion interna, no un endpoint publico proyectado en un auditorio. La
/// amenaza es otra y por eso la respuesta es otra.
/// </summary>
[Route("api/autenticacion")]
[ApiController]
[AllowAnonymous]
public class AutenticacionController : ControllerBase
{
    private readonly IAutenticacionServicio _svc;
    private readonly ILogger<AutenticacionController> _log;

    public AutenticacionController(IAutenticacionServicio svc, ILogger<AutenticacionController> log)
    { _svc = svc; _log = log; }

    [HttpPost("token")]
    public async Task<IActionResult> GenerarToken([FromBody] Credenciales credenciales)
    {
        try
        {
            var codigo = await _svc.ValidarCredencialesAsync(credenciales.Email, credenciales.Contrasena);
            if (codigo == 404) return NotFound(new { estado = 404, mensaje = "Usuario no encontrado." });
            if (codigo == 401) return Unauthorized(new { estado = 401, mensaje = "Contrasena incorrecta." });

            var (token, expiracion, roles) = await _svc.GenerarTokenAsync(credenciales.Email);
            return Ok(new
            {
                estado = 200,
                mensaje = "Autenticacion exitosa.",
                usuario = credenciales.Email,
                roles,
                token,
                expiracion
            });
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Error al autenticar usuario");
            return StatusCode(500, new { estado = 500, mensaje = "Error interno durante la autenticacion." });
        }
    }
}

/// <summary>Cuerpo del POST /api/autenticacion/token.</summary>
public class Credenciales
{
    /// <summary>
    /// Correo institucional del administrador. Se aceptan tambien el correo personal
    /// y el login de catedras.usuario.usuario.
    /// </summary>
    /// <example>admin.catedras@usbmed.edu.co</example>
    [Required] public string Email { get; set; } = string.Empty;

    [Required] public string Contrasena { get; set; } = string.Empty;
}
