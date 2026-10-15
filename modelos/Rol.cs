using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("rol")]
public class Rol
{
    [Key]
    [Column("id_rol")]
    [Required]
    [MaxLength(20)]
    public string IdRol { get; set; } = string.Empty;
    [Column("nombre")]
    [Required]
    [MaxLength(60)]
    public string Nombre { get; set; } = string.Empty;
    [Column("descripcion")]
    [MaxLength(200)]
    public string? Descripcion { get; set; }
}
