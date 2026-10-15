using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("v_evaluacion_sesion")]
public class VEvaluacionSesion
{
    [Column("id_sesion")]
    public long? IdSesion { get; set; }
    [Column("catedra")]
    [MaxLength(200)]
    public string? Catedra { get; set; }
    [Column("numero_reunion")]
    public short? NumeroReunion { get; set; }
    [Column("orden")]
    public short? Orden { get; set; }
    [Column("enunciado")]
    [MaxLength(300)]
    public string? Enunciado { get; set; }
    [Column("tipo")]
    [MaxLength(15)]
    public string? Tipo { get; set; }
    [Column("respuestas")]
    public long? Respuestas { get; set; }
    [Column("promedio")]
    public decimal? Promedio { get; set; }
    [Column("minimo")]
    public short? Minimo { get; set; }
    [Column("maximo")]
    public short? Maximo { get; set; }
}
