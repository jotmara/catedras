using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("lote_migracion")]
public class LoteMigracion
{
    [Key]
    [Column("id_lote_migracion")]
    public long IdLoteMigracion { get; set; }
    [Column("fk_sesion")]
    public long FkSesion { get; set; }
    [Column("nombre_proceso")]
    [Required]
    [MaxLength(60)]
    public string NombreProceso { get; set; } = string.Empty;
    [Column("nombre_archivo")]
    [Required]
    [MaxLength(200)]
    public string NombreArchivo { get; set; } = string.Empty;
    [Column("generado_en")]
    public DateTimeOffset GeneradoEn { get; set; }
    [Column("fk_usuario")]
    public long? FkUsuario { get; set; }
    [Column("instancia_proceso_asis")]
    [MaxLength(30)]
    public string? InstanciaProcesoAsis { get; set; }
    [Column("fk_estado_proceso")]
    [Required]
    [MaxLength(12)]
    public string FkEstadoProceso { get; set; } = string.Empty;
    [Column("total_filas")]
    public int TotalFilas { get; set; }
    [Column("observaciones")]
    public string? Observaciones { get; set; }
}
