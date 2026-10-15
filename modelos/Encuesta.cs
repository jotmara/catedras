using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("encuesta")]
public class Encuesta
{
    [Key]
    [Column("id_encuesta")]
    public long IdEncuesta { get; set; }
    [Column("nombre")]
    [Required]
    [MaxLength(120)]
    public string Nombre { get; set; } = string.Empty;
    [Column("version")]
    public short Version { get; set; }
    [Column("vigente_desde")]
    public DateOnly VigenteDesde { get; set; }
    [Column("vigente_hasta")]
    public DateOnly? VigenteHasta { get; set; }
    [Column("activa")]
    public bool Activa { get; set; }
}
