using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("modalidad")]
public class Modalidad
{
    [Key]
    [Column("id_modalidad")]
    [Required]
    [MaxLength(15)]
    public string IdModalidad { get; set; } = string.Empty;
    [Column("nombre")]
    [Required]
    [MaxLength(60)]
    public string Nombre { get; set; } = string.Empty;
    [Column("canal_difusion")]
    [Required]
    [MaxLength(10)]
    public string CanalDifusion { get; set; } = string.Empty;
    [Column("activo")]
    public bool Activo { get; set; }
}
