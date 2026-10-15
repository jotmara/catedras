using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("estado_proceso")]
public class EstadoProceso
{
    [Key]
    [Column("id_estado")]
    [Required]
    [MaxLength(12)]
    public string IdEstado { get; set; } = string.Empty;
    [Column("nombre")]
    [Required]
    [MaxLength(40)]
    public string Nombre { get; set; } = string.Empty;
    [Column("es_final")]
    public bool EsFinal { get; set; }
    [Column("es_exitoso")]
    public bool EsExitoso { get; set; }
}
