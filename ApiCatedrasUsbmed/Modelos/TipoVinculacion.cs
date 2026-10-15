using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("tipo_vinculacion")]
public class TipoVinculacion
{
    [Key]
    [Column("id_tipo_vinculacion")]
    [Required]
    [MaxLength(15)]
    public string IdTipoVinculacion { get; set; } = string.Empty;
    [Column("nombre")]
    [Required]
    [MaxLength(60)]
    public string Nombre { get; set; } = string.Empty;
    [Column("es_interno")]
    public bool EsInterno { get; set; }
    [Column("exige_programa")]
    public bool ExigePrograma { get; set; }
    [Column("activo")]
    public bool Activo { get; set; }
}
