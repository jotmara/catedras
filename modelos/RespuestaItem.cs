using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("respuesta_item")]
public class RespuestaItem
{
    [Key]
    [Column("id_item")]
    public long IdItem { get; set; }
    [Column("fk_respuesta")]
    public long FkRespuesta { get; set; }
    [Column("fk_pregunta")]
    public long FkPregunta { get; set; }
    [Column("valor_numerico")]
    public short? ValorNumerico { get; set; }
    [Column("valor_texto")]
    public string? ValorTexto { get; set; }
    [Column("fk_opcion")]
    public long? FkOpcion { get; set; }
}
