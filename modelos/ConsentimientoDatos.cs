using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("consentimiento_datos")]
public class ConsentimientoDatos
{
    [Key]
    [Column("id_consentimiento")]
    public long IdConsentimiento { get; set; }
    [Column("fk_asistente")]
    public long FkAsistente { get; set; }
    [Column("version_politica")]
    [Required]
    [MaxLength(20)]
    public string VersionPolitica { get; set; } = string.Empty;
    [Column("aceptado_en")]
    public DateTimeOffset AceptadoEn { get; set; }
    [Column("ip")]
    public string? Ip { get; set; }
    [Column("canal")]
    [Required]
    [MaxLength(20)]
    public string Canal { get; set; } = string.Empty;
}
