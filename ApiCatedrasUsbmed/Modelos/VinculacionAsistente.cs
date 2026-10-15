using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("vinculacion_asistente")]
public class VinculacionAsistente
{
    [Key]
    [Column("fk_asistente")]
    public long FkAsistente { get; set; }
    [Key]
    [Column("fk_tipo_vinculacion")]
    [Required]
    [MaxLength(15)]
    public string FkTipoVinculacion { get; set; } = string.Empty;
    [Key]
    [Column("fecha_ini")]
    public DateOnly FechaIni { get; set; }
    [Column("fecha_fin")]
    public DateOnly? FechaFin { get; set; }
}
