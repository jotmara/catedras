using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("v_pendiente_migracion")]
public class VPendienteMigracion
{
    [Column("id_sesion")]
    public long? IdSesion { get; set; }
    [Column("id_evento_asis")]
    [MaxLength(9)]
    public string? IdEventoAsis { get; set; }
    [Column("catedra")]
    [MaxLength(200)]
    public string? Catedra { get; set; }
    [Column("numero_reunion")]
    public short? NumeroReunion { get; set; }
    [Column("inicio")]
    public DateTimeOffset? Inicio { get; set; }
    [Column("registros")]
    public long? Registros { get; set; }
    [Column("sin_id_asis")]
    public long? SinIdAsis { get; set; }
    [Column("sin_programa")]
    public long? SinPrograma { get; set; }
    [Column("externos")]
    public long? Externos { get; set; }
    [Column("migrables")]
    public long? Migrables { get; set; }
}
