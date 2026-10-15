using System.Net;
using System.Net.Mail;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

/// <summary>
/// Envio de la clave de un solo uso.
///
/// CONFIG-GATED, FAIL-CLOSED, igual que el modulo Agente de ApiEvalFormativaUsbmed: sin
/// Correo:Activo=true no se envia nada y se devuelve false. La base sigue registrando el
/// intento, asi que el flujo se puede probar entero sin servidor SMTP.
/// </summary>
public class ServicioCorreo : IServicioCorreo
{
    private readonly IConfiguration _cfg;
    private readonly ILogger<ServicioCorreo> _log;

    public ServicioCorreo(IConfiguration cfg, ILogger<ServicioCorreo> log)
    { _cfg = cfg; _log = log; }

    public async Task<bool> EnviarClaveAsync(string destino, string clave)
    {
        if (!_cfg.GetValue<bool>("Correo:Activo"))
        {
            _log.LogInformation("Correo desactivado (Correo:Activo=false). No se envio a {Destino}.", destino);
            return false;
        }

        var host = _cfg["Correo:Host"];
        if (string.IsNullOrWhiteSpace(host))
        {
            _log.LogError("Correo:Activo=true pero Correo:Host no esta configurado.");
            return false;
        }

        var remitente = _cfg["Correo:Remitente"] ?? "catedras@usbmed.edu.co";

        using var mensaje = new MailMessage(remitente, destino)
        {
            Subject = "Su clave de acceso - Catedras Abiertas USB Medellin",
            IsBodyHtml = true,
            Body = $@"<div style=""font-family:Segoe UI,Arial,sans-serif;max-width:520px"">
  <h2 style=""color:#2d5a8c"">Catedras Abiertas</h2>
  <p>Universidad de San Buenaventura, Medellin</p>
  <p>Su clave de acceso para registrar la asistencia es:</p>
  <p style=""font-size:32px;letter-spacing:8px;font-weight:bold;color:#2d5a8c"">{clave}</p>
  <p>Es de un solo uso y caduca en pocos minutos.</p>
  <p style=""color:#888;font-size:12px"">Si usted no solicito esta clave, ignore este mensaje.</p>
</div>"
        };

        using var cliente = new SmtpClient(host, _cfg.GetValue<int?>("Correo:Puerto") ?? 587)
        {
            EnableSsl = _cfg.GetValue<bool?>("Correo:UsarSsl") ?? true
        };

        var usuario = _cfg["Correo:Usuario"];
        if (!string.IsNullOrWhiteSpace(usuario))
            cliente.Credentials = new NetworkCredential(usuario, _cfg["Correo:Contrasena"]);

        try
        {
            await cliente.SendMailAsync(mensaje);
            return true;
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Fallo el envio de la clave a {Destino}", destino);
            return false;
        }
    }
}
