using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("tipo_documento")]
public class TipoDocumento
{
    [Key]
    [Column("id_tipo_documento")]
    [Required]
    [MaxLength(5)]
    public string IdTipoDocumento { get; set; } = string.Empty;
    [Column("nombre")]
    [Required]
    [MaxLength(60)]
    public string Nombre { get; set; } = string.Empty;
    [Column("activo")]
    public bool Activo { get; set; }
}
