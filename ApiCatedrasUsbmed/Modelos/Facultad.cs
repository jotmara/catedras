using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("facultad")]
public class Facultad
{
    [Key]
    [Column("id_facultad")]
    [Required]
    [MaxLength(10)]
    public string IdFacultad { get; set; } = string.Empty;
    [Column("nombre")]
    [Required]
    [MaxLength(120)]
    public string Nombre { get; set; } = string.Empty;
    [Column("fk_facultad_padre")]
    [MaxLength(10)]
    public string? FkFacultadPadre { get; set; }
    [Column("activo")]
    public bool Activo { get; set; }
}
