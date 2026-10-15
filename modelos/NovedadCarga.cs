using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("novedad_carga")]
public class NovedadCarga
{
    [Key]
    [Column("id_novedad")]
    public long IdNovedad { get; set; }
    [Column("fk_lote_carga")]
    public long FkLoteCarga { get; set; }
    [Column("numero_fila")]
    public int NumeroFila { get; set; }
    [Column("contenido_crudo")]
    [Required]
    public string ContenidoCrudo { get; set; } = string.Empty;
    [Column("motivo")]
    [Required]
    [MaxLength(200)]
    public string Motivo { get; set; } = string.Empty;
}
