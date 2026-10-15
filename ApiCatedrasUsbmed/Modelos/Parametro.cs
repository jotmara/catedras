using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("parametro")]
public class Parametro
{
    [Key]
    [Column("clave")]
    [Required]
    [MaxLength(60)]
    public string Clave { get; set; } = string.Empty;
    [Column("valor")]
    [Required]
    [MaxLength(200)]
    public string Valor { get; set; } = string.Empty;
    [Column("tipo_dato")]
    [Required]
    [MaxLength(15)]
    public string TipoDato { get; set; } = string.Empty;
    [Column("descripcion")]
    [Required]
    [MaxLength(300)]
    public string Descripcion { get; set; } = string.Empty;
    [Column("fk_usuario_modifica")]
    public long? FkUsuarioModifica { get; set; }
    [Column("modificado_en")]
    public DateTimeOffset ModificadoEn { get; set; }
}
