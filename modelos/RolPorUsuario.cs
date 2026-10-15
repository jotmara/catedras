using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("rol_por_usuario")]
public class RolPorUsuario
{
    [Key]
    [Column("fk_usuario")]
    public long FkUsuario { get; set; }
    [Key]
    [Column("fk_rol")]
    [Required]
    [MaxLength(20)]
    public string FkRol { get; set; } = string.Empty;
    [Key]
    [Column("fecha_ini")]
    public DateOnly FechaIni { get; set; }
    [Column("fecha_fin")]
    public DateOnly? FechaFin { get; set; }
}
