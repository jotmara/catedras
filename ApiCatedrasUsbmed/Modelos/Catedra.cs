using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("catedra")]
public class Catedra
{
    [Key]
    [Column("id_catedra")]
    public long IdCatedra { get; set; }
    [Column("id_evento_asis")]
    [Required]
    [MaxLength(9)]
    public string IdEventoAsis { get; set; } = string.Empty;
    [Column("nombre")]
    [Required]
    [MaxLength(200)]
    public string Nombre { get; set; } = string.Empty;
    [Column("nombre_asis")]
    [DatabaseGenerated(DatabaseGeneratedOption.Computed)]
    [MaxLength(30)]
    public string? NombreAsis { get; set; }
    [Column("fk_tipo_evento")]
    [Required]
    [MaxLength(4)]
    public string FkTipoEvento { get; set; } = string.Empty;
    [Column("fk_dependencia")]
    [MaxLength(15)]
    public string? FkDependencia { get; set; }
    [Column("activo")]
    public bool Activo { get; set; }
    [Column("creado_en")]
    public DateTimeOffset CreadoEn { get; set; }
}
