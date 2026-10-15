using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("v_embudo_registro")]
public class VEmbudoRegistro
{
    [Column("id_sesion")]
    public long? IdSesion { get; set; }
    [Column("catedra")]
    [MaxLength(200)]
    public string? Catedra { get; set; }
    [Column("numero_reunion")]
    public short? NumeroReunion { get; set; }
    [Column("enlaces")]
    public long? Enlaces { get; set; }
    [Column("claves_enviadas")]
    public long? ClavesEnviadas { get; set; }
    [Column("claves_usadas")]
    public long? ClavesUsadas { get; set; }
    [Column("registros")]
    public long? Registros { get; set; }
    [Column("encuestas")]
    public long? Encuestas { get; set; }
}
