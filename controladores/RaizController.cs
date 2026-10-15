using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Reflection;

namespace ApiCatedrasUsbmed.Controllers;

/// <summary>
/// Endpoint raiz. Devuelve quien es esta API, si esta viva y por donde se entra.
/// Es lo primero que ve alguien que abre la URL a secas, y evita el 404 seco.
/// </summary>
[Route("")]
[ApiController]
[AllowAnonymous]
public class RaizController : ControllerBase
{
    private readonly IWebHostEnvironment _entorno;

    public RaizController(IWebHostEnvironment entorno) => _entorno = entorno;

    [HttpGet]
    public IActionResult Inicio() => Ok(new
    {
        api         = "ApiCatedrasUsbmed",
        descripcion = "Registro y control de asistencia a catedras abiertas - "
                    + "Universidad de San Buenaventura, Medellin",
        version     = Assembly.GetExecutingAssembly().GetName().Version?.ToString(),
        entorno     = _entorno.EnvironmentName,
        estado      = "en linea",
        hora        = DateTimeOffset.Now,

        documentacion = _entorno.IsDevelopment() ? "/swagger" : "no publicada fuera de Development",

        autenticacion = new
        {
            administrador = "POST /api/autenticacion/token  con { email, contrasena }",
            asistente     = "POST /api/acceso/solicitar-clave  con { identificador, token }"
        },

        anonimos = new[]
        {
            "GET  /",
            "GET  /salud",
            "POST /api/autenticacion/token",
            "GET  /api/acceso/enlace/{token}",
            "POST /api/acceso/solicitar-clave",
            "POST /api/acceso/validar"
        },

        repositorio = "https://github.com/ccastro2050/proyectoCatedras"
    });

    /// <summary>Sonda de vida. La usa el proxy inverso y el servicio de systemd.</summary>
    [HttpGet("/salud")]
    public IActionResult Salud() => Ok(new { estado = "ok", hora = DateTimeOffset.Now });
}
