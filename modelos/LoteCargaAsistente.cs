using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("lote_carga_asistente")]
public class LoteCargaAsistente
{
    [Key]
    [Column("id_lote_carga")]
    public long IdLoteCarga { get; set; }
    [Column("nombre_archivo")]
    [Required]
    [MaxLength(200)]
    public string NombreArchivo { get; set; } = string.Empty;
    [Column("cargado_en")]
    public DateTimeOffset CargadoEn { get; set; }
    [Column("fk_usuario")]
    public long? FkUsuario { get; set; }
    [Column("filas_leidas")]
    public int FilasLeidas { get; set; }
    [Column("filas_aceptadas")]
    public int FilasAceptadas { get; set; }
    [Column("filas_rechazadas")]
    public int FilasRechazadas { get; set; }
    [Column("observaciones")]
    public string? Observaciones { get; set; }
}
