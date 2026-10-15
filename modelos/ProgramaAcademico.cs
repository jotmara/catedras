using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("programa_academico")]
public class ProgramaAcademico
{
    [Key]
    [Column("codigo")]
    [Required]
    [MaxLength(5)]
    public string Codigo { get; set; } = string.Empty;
    [Column("nombre")]
    [Required]
    [MaxLength(150)]
    public string Nombre { get; set; } = string.Empty;
    [Column("fk_facultad")]
    [MaxLength(10)]
    public string? FkFacultad { get; set; }
    [Column("nivel")]
    [Required]
    [MaxLength(25)]
    public string Nivel { get; set; } = string.Empty;
    [Column("activo")]
    public bool Activo { get; set; }
}
