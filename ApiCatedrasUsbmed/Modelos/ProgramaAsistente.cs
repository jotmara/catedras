using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("programa_asistente")]
public class ProgramaAsistente
{
    [Key]
    [Column("fk_asistente")]
    public long FkAsistente { get; set; }
    [Key]
    [Column("fk_programa")]
    [Required]
    [MaxLength(5)]
    public string FkPrograma { get; set; } = string.Empty;
    [Key]
    [Column("fk_periodo")]
    [Required]
    [MaxLength(6)]
    public string FkPeriodo { get; set; } = string.Empty;
    [Column("estado")]
    [Required]
    [MaxLength(15)]
    public string Estado { get; set; } = string.Empty;
}
