using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("documento_asistente")]
public class DocumentoAsistente
{
    [Key]
    [Column("id_documento")]
    public long IdDocumento { get; set; }
    [Column("fk_asistente")]
    public long FkAsistente { get; set; }
    [Column("fk_tipo_documento")]
    [Required]
    [MaxLength(5)]
    public string FkTipoDocumento { get; set; } = string.Empty;
    [Column("numero")]
    [Required]
    [MaxLength(20)]
    public string Numero { get; set; } = string.Empty;
    [Column("vigente")]
    public bool Vigente { get; set; }
    [Column("registrado_en")]
    public DateTimeOffset RegistradoEn { get; set; }
}
