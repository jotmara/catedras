using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("pregunta")]
public class Pregunta
{
    [Key]
    [Column("id_pregunta")]
    public long IdPregunta { get; set; }
    [Column("fk_encuesta")]
    public long FkEncuesta { get; set; }
    [Column("enunciado")]
    [Required]
    [MaxLength(300)]
    public string Enunciado { get; set; } = string.Empty;
    [Column("orden")]
    public short Orden { get; set; }
    [Column("fk_tipo_pregunta")]
    [Required]
    [MaxLength(15)]
    public string FkTipoPregunta { get; set; } = string.Empty;
    [Column("obligatoria")]
    public bool Obligatoria { get; set; }
    [Column("valor_min")]
    public short? ValorMin { get; set; }
    [Column("valor_max")]
    public short? ValorMax { get; set; }
}
