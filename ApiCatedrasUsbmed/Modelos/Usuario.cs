using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("usuario")]
public class Usuario
{
    [Key]
    [Column("id_usuario")]
    public long IdUsuario { get; set; }
    [Column("fk_asistente")]
    public long FkAsistente { get; set; }
    [Column("usuario")]
    [Required]
    [MaxLength(40)]
    public string NombreUsuario { get; set; } = string.Empty;
    [Column("clave_hash")]
    [JsonIgnore]   // nunca sale en el JSON de respuesta
    [Required]
    [MaxLength(255)]
    public string ClaveHash { get; set; } = string.Empty;
    [Column("activo")]
    public bool Activo { get; set; }
    [Column("ultimo_acceso")]
    public DateTimeOffset? UltimoAcceso { get; set; }
    [Column("creado_en")]
    public DateTimeOffset CreadoEn { get; set; }
}
