using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("clave_acceso")]
public class ClaveAcceso
{
    [Key]
    [Column("id_clave")]
    public long IdClave { get; set; }
    [Column("fk_asistente")]
    public long FkAsistente { get; set; }
    [Column("fk_enlace")]
    public long FkEnlace { get; set; }
    [Column("clave_hash")]
    [JsonIgnore]   // nunca sale en el JSON de respuesta
    public byte[] ClaveHash { get; set; } = Array.Empty<byte>();
    [Column("enviado_a")]
    [Required]
    public string EnviadoA { get; set; } = string.Empty;
    [Column("es_correo_institucional")]
    public bool EsCorreoInstitucional { get; set; }
    [Column("generado_en")]
    public DateTimeOffset GeneradoEn { get; set; }
    [Column("expira_en")]
    public DateTimeOffset ExpiraEn { get; set; }
    [Column("usado_en")]
    public DateTimeOffset? UsadoEn { get; set; }
    [Column("intentos")]
    public short Intentos { get; set; }
    [Column("ip_solicitud")]
    public string? IpSolicitud { get; set; }
}
