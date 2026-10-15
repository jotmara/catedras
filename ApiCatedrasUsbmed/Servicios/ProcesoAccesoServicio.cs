using System.Text.Json;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class ProcesoAccesoServicio : IProcesoAccesoServicio
{
    private readonly IProcesoAccesoRepositorio _repo;
    private readonly IServicioCorreo _correo;
    private readonly ILogger<ProcesoAccesoServicio> _log;

    public ProcesoAccesoServicio(IProcesoAccesoRepositorio repo, IServicioCorreo correo,
                                 ILogger<ProcesoAccesoServicio> log)
    { _repo = repo; _correo = correo; _log = log; }

    public Task<EnlacePublico?> ObtenerEnlacePublicoAsync(Guid token) =>
        _repo.ObtenerEnlacePublicoAsync(token);

    /// <summary>
    /// Pide la clave, la envia por correo y devuelve SOLO el correo enmascarado.
    ///
    /// La clave en claro nunca sale de aqui: el procedimiento la devuelve para poder
    /// enviarla, la base guarda solo el hash, y este metodo no la propaga al controlador.
    /// </summary>
    public async Task<(bool enviada, string correoEnmascarado, long idClave)> SolicitarClaveAsync(
        string identificador, Guid token, string? ip)
    {
        var r = await _repo.SolicitarClaveAsync(identificador, token, ip);
        if (r is null) return (false, string.Empty, 0);

        var enviada = await _correo.EnviarClaveAsync(r.EnviadoA, r.Clave);
        if (!enviada)
            _log.LogWarning("El correo esta desactivado: la clave {IdClave} se genero pero no se envio.", r.IdClave);

        return (enviada, Enmascarar(r.EnviadoA), r.IdClave);
    }

    public Task<long> ValidarYRegistrarAsync(long idClave, string clave, string? ip, string? userAgent) =>
        _repo.ValidarYRegistrarAsync(idClave, clave, ip, userAgent);

    public Task<long> ResponderEncuestaAsync(long idRegistro, RespuestaEncuestaEntrada entrada) =>
        _repo.ResponderEncuestaAsync(idRegistro,
            JsonSerializer.Serialize(entrada.Respuestas.Select(x => new
            {
                pregunta = x.Pregunta,
                numero = x.Numero,
                texto = x.Texto,
                opcion = x.Opcion
            })));

    /// <summary>
    /// a***@usbmed.edu.co. Devolver la direccion completa a un anonimo seria filtrar el
    /// directorio institucional.
    /// </summary>
    private static string Enmascarar(string correo)
    {
        if (string.IsNullOrWhiteSpace(correo) || !correo.Contains('@')) return "***";
        var partes = correo.Split('@');
        var u = partes[0];
        var visible = u.Length <= 2 ? u[..1] : u[..2];
        return $"{visible}{new string('*', Math.Max(3, u.Length - visible.Length))}@{partes[1]}";
    }
}
