using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("detalle_migracion")]
public class DetalleMigracion
{
    [Key]
    [Column("id_detalle")]
    public long IdDetalle { get; set; }
    [Column("fk_lote_migracion")]
    public long FkLoteMigracion { get; set; }
    [Column("fk_registro")]
    public long FkRegistro { get; set; }
    [Column("id_asis_enviado")]
    [Required]
    [MaxLength(15)]
    public string IdAsisEnviado { get; set; } = string.Empty;
    [Column("programa_enviado")]
    [MaxLength(5)]
    public string? ProgramaEnviado { get; set; }
    [Column("reunion_enviada")]
    public short ReunionEnviada { get; set; }
    [Column("resultado")]
    [Required]
    [MaxLength(12)]
    public string Resultado { get; set; } = string.Empty;
    [Column("mensaje")]
    [MaxLength(300)]
    public string? Mensaje { get; set; }
}
