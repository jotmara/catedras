using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("bitacora")]
public class Bitacora
{
    [Key]
    [Column("id_bitacora")]
    public long IdBitacora { get; set; }
    [Column("ocurrido_en")]
    public DateTimeOffset OcurridoEn { get; set; }
    [Column("usuario_bd")]
    [Required]
    public string UsuarioBd { get; set; } = string.Empty;
    [Column("fk_usuario")]
    public long? FkUsuario { get; set; }
    [Column("nombre_tabla")]
    [Required]
    [MaxLength(63)]
    public string NombreTabla { get; set; } = string.Empty;
    [Column("operacion")]
    [Required]
    [MaxLength(10)]
    public string Operacion { get; set; } = string.Empty;
    [Column("llave")]
    [MaxLength(100)]
    public string? Llave { get; set; }
    [Column("datos_antes")]
    public string? DatosAntes { get; set; }
    [Column("datos_despues")]
    public string? DatosDespues { get; set; }
}
