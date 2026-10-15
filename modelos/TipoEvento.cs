using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("tipo_evento")]
public class TipoEvento
{
    [Key]
    [Column("id_tipo_evento")]
    [Required]
    [MaxLength(4)]
    public string IdTipoEvento { get; set; } = string.Empty;
    [Column("nombre")]
    [Required]
    [MaxLength(80)]
    public string Nombre { get; set; } = string.Empty;
    [Column("activo")]
    public bool Activo { get; set; }
}
