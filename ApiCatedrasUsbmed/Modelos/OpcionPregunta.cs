using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("opcion_pregunta")]
public class OpcionPregunta
{
    [Key]
    [Column("id_opcion")]
    public long IdOpcion { get; set; }
    [Column("fk_pregunta")]
    public long FkPregunta { get; set; }
    [Column("etiqueta")]
    [Required]
    [MaxLength(150)]
    public string Etiqueta { get; set; } = string.Empty;
    [Column("valor")]
    public short? Valor { get; set; }
    [Column("orden")]
    public short Orden { get; set; }
}
