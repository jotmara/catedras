using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("ponencia")]
public class Ponencia
{
    [Key]
    [Column("fk_sesion")]
    public long FkSesion { get; set; }
    [Key]
    [Column("fk_asistente")]
    public long FkAsistente { get; set; }
    [Key]
    [Column("rol")]
    [Required]
    [MaxLength(15)]
    public string Rol { get; set; } = string.Empty;
}
