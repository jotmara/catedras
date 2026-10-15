using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("sede")]
public class Sede
{
    [Key]
    [Column("id_sede")]
    [Required]
    [MaxLength(15)]
    public string IdSede { get; set; } = string.Empty;
    [Column("nombre")]
    [Required]
    [MaxLength(80)]
    public string Nombre { get; set; } = string.Empty;
    [Column("direccion")]
    [MaxLength(200)]
    public string? Direccion { get; set; }
    [Column("es_virtual")]
    public bool EsVirtual { get; set; }
    [Column("activo")]
    public bool Activo { get; set; }
}
