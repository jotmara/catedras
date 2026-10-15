using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("dependencia")]
public class Dependencia
{
    [Key]
    [Column("id_dependencia")]
    [Required]
    [MaxLength(15)]
    public string IdDependencia { get; set; } = string.Empty;
    [Column("nombre")]
    [Required]
    [MaxLength(120)]
    public string Nombre { get; set; } = string.Empty;
    [Column("fk_dependencia_padre")]
    [MaxLength(15)]
    public string? FkDependenciaPadre { get; set; }
    [Column("activo")]
    public bool Activo { get; set; }
}
