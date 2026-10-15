using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("tipo_pregunta")]
public class TipoPregunta
{
    [Key]
    [Column("id_tipo_pregunta")]
    [Required]
    [MaxLength(15)]
    public string IdTipoPregunta { get; set; } = string.Empty;
    [Column("nombre")]
    [Required]
    [MaxLength(60)]
    public string Nombre { get; set; } = string.Empty;
    [Column("guarda_numero")]
    public bool GuardaNumero { get; set; }
    [Column("guarda_texto")]
    public bool GuardaTexto { get; set; }
    [Column("guarda_opcion")]
    public bool GuardaOpcion { get; set; }
}
