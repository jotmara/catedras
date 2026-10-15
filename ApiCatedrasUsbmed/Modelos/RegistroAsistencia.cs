using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("registro_asistencia")]
public class RegistroAsistencia
{
    [Key]
    [Column("id_registro")]
    public long IdRegistro { get; set; }
    [Column("fk_sesion")]
    public long FkSesion { get; set; }
    [Column("fk_asistente")]
    public long FkAsistente { get; set; }
    [Column("fk_enlace")]
    public long? FkEnlace { get; set; }
    [Column("fk_clave")]
    public long? FkClave { get; set; }
    [Column("registrado_en")]
    public DateTimeOffset RegistradoEn { get; set; }
    [Column("fk_programa_snapshot")]
    [MaxLength(5)]
    public string? FkProgramaSnapshot { get; set; }
    [Column("fk_vinculacion_snapshot")]
    [Required]
    [MaxLength(15)]
    public string FkVinculacionSnapshot { get; set; } = string.Empty;
    [Column("origen")]
    [Required]
    [MaxLength(15)]
    public string Origen { get; set; } = string.Empty;
    [Column("ip")]
    public string? Ip { get; set; }
    [Column("user_agent")]
    [MaxLength(300)]
    public string? UserAgent { get; set; }
}
