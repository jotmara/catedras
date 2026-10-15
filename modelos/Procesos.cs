using System.ComponentModel.DataAnnotations;

namespace ApiCatedrasUsbmed.Modelos;

// ─────────────────────────────────────────────────────────── Acceso ─────────

/// <summary>Cuerpo de POST /api/acceso/solicitar-clave.</summary>
public class SolicitudClave
{
    /// <summary>Codigo del ASIS, numero de documento o correo. Las tres vias valen (RN-06).</summary>
    [Required] public string Identificador { get; set; } = string.Empty;

    /// <summary>El token del QR o del enlace.</summary>
    [Required] public Guid Token { get; set; }
}

/// <summary>Cuerpo de POST /api/acceso/validar.</summary>
public class ValidacionClave
{
    [Required] public long IdClave { get; set; }
    [Required] public string Clave { get; set; } = string.Empty;
}

/// <summary>Lo que devuelve sp_solicitar_clave.</summary>
public class ResultadoSolicitudClave
{
    public long IdClave { get; set; }
    public string Clave { get; set; } = string.Empty;        // NO se expone al cliente
    public string EnviadoA { get; set; } = string.Empty;     // se enmascara al exponerlo
}

/// <summary>Datos publicos de un enlace, para la pantalla de bienvenida.</summary>
public class EnlacePublico
{
    public Guid Token { get; set; }
    public string Catedra { get; set; } = string.Empty;
    public string? Sesion { get; set; }
    public short NumeroReunion { get; set; }
    public DateTimeOffset Inicio { get; set; }
    public DateTimeOffset Fin { get; set; }
    public string Sede { get; set; } = string.Empty;
    public string Modalidad { get; set; } = string.Empty;
    public string? Lugar { get; set; }
    public bool VentanaAbierta { get; set; }
    public DateTimeOffset VentanaInicio { get; set; }
    public DateTimeOffset VentanaFin { get; set; }
}

// ─────────────────────────────────────────────────────────── Encuesta ───────

public class RespuestaEncuestaEntrada
{
    [Required] public List<ItemRespuesta> Respuestas { get; set; } = new();
}

public class ItemRespuesta
{
    [Required] public long Pregunta { get; set; }
    public short? Numero { get; set; }
    public string? Texto { get; set; }
    public long? Opcion { get; set; }
}

// ─────────────────────────────────────────────────────────── Enlace ─────────

public class EmisionEnlace
{
    [Required] public long IdSesion { get; set; }
    public int? MinutosAntes { get; set; }
    public int? MinutosDespues { get; set; }
}

// ─────────────────────────────────────────────────────────── Migracion ──────

/// <summary>Una fila del archivo plano del ASIS. TRES columnas, ni una mas.</summary>
public class FilaArchivoAsis
{
    public short Reunion { get; set; }
    public string IdAsis { get; set; } = string.Empty;
    public string Programa { get; set; } = string.Empty;
}

public class ResultadoLote
{
    [Required] public string Estado { get; set; } = string.Empty;   // catedras.estado_proceso
    public string? InstanciaProcesoAsis { get; set; }
    public string? Observaciones { get; set; }
}
