using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("sesion")]
public class Sesion
{
    [Key]
    [Column("id_sesion")]
    public long IdSesion { get; set; }
    [Column("fk_catedra")]
    public long FkCatedra { get; set; }
    [Column("numero_reunion")]
    public short NumeroReunion { get; set; }
    [Column("numero_reunion_asis")]
    public short? NumeroReunionAsis { get; set; }
    [Column("titulo")]
    [MaxLength(200)]
    public string? Titulo { get; set; }
    [Column("inicio")]
    public DateTimeOffset Inicio { get; set; }
    [Column("fin")]
    public DateTimeOffset Fin { get; set; }
    [Column("fk_modalidad")]
    [Required]
    [MaxLength(15)]
    public string FkModalidad { get; set; } = string.Empty;
    [Column("fk_sede")]
    [Required]
    [MaxLength(15)]
    public string FkSede { get; set; } = string.Empty;
    [Column("fk_periodo")]
    [Required]
    [MaxLength(6)]
    public string FkPeriodo { get; set; } = string.Empty;
    [Column("fk_encuesta")]
    public long? FkEncuesta { get; set; }
    [Column("lugar")]
    [MaxLength(200)]
    public string? Lugar { get; set; }
    [Column("enlace_virtual")]
    [MaxLength(300)]
    public string? EnlaceVirtual { get; set; }
    [Column("cupo")]
    public int? Cupo { get; set; }
    [Column("estado")]
    [Required]
    [MaxLength(15)]
    public string Estado { get; set; } = string.Empty;
    [Column("creado_en")]
    public DateTimeOffset CreadoEn { get; set; }
}
