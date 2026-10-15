using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("respuesta_encuesta")]
public class RespuestaEncuesta
{
    [Key]
    [Column("id_respuesta")]
    public long IdRespuesta { get; set; }
    [Column("fk_registro")]
    public long FkRegistro { get; set; }
    [Column("fk_encuesta")]
    public long FkEncuesta { get; set; }
    [Column("respondida_en")]
    public DateTimeOffset RespondidaEn { get; set; }
    [Column("completa")]
    public bool Completa { get; set; }
}
