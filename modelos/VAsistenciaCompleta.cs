using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("v_asistencia_completa")]
public class VAsistenciaCompleta
{
    [Column("id_registro")]
    public long? IdRegistro { get; set; }
    [Column("registrado_en")]
    public DateTimeOffset? RegistradoEn { get; set; }
    [Column("origen")]
    [MaxLength(15)]
    public string? Origen { get; set; }
    [Column("id_evento_asis")]
    [MaxLength(9)]
    public string? IdEventoAsis { get; set; }
    [Column("catedra")]
    [MaxLength(200)]
    public string? Catedra { get; set; }
    [Column("id_sesion")]
    public long? IdSesion { get; set; }
    [Column("numero_reunion")]
    public short? NumeroReunion { get; set; }
    [Column("sesion")]
    [MaxLength(200)]
    public string? Sesion { get; set; }
    [Column("inicio")]
    public DateTimeOffset? Inicio { get; set; }
    [Column("periodo")]
    [MaxLength(6)]
    public string? Periodo { get; set; }
    [Column("sede")]
    [MaxLength(80)]
    public string? Sede { get; set; }
    [Column("modalidad")]
    [MaxLength(60)]
    public string? Modalidad { get; set; }
    [Column("id_asistente")]
    public long? IdAsistente { get; set; }
    [Column("id_asis")]
    [MaxLength(15)]
    public string? IdAsis { get; set; }
    [Column("asistente")]
    public string? Asistente { get; set; }
    [Column("es_externo")]
    public bool? EsExterno { get; set; }
    [Column("programa")]
    [MaxLength(5)]
    public string? Programa { get; set; }
    [Column("programa_nombre")]
    [MaxLength(150)]
    public string? ProgramaNombre { get; set; }
    [Column("facultad")]
    [MaxLength(10)]
    public string? Facultad { get; set; }
    [Column("vinculacion")]
    [MaxLength(15)]
    public string? Vinculacion { get; set; }
    [Column("es_interno")]
    public bool? EsInterno { get; set; }
    [Column("respondio_encuesta")]
    public bool? RespondioEncuesta { get; set; }
}
