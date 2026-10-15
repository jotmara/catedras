using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("periodo_academico")]
public class PeriodoAcademico
{
    [Key]
    [Column("id_periodo")]
    [Required]
    [MaxLength(6)]
    public string IdPeriodo { get; set; } = string.Empty;
    [Column("fecha_ini")]
    public DateOnly FechaIni { get; set; }
    [Column("fecha_fin")]
    public DateOnly FechaFin { get; set; }
    [Column("activo")]
    public bool Activo { get; set; }
}
