using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("v_asistente_vigente")]
public class VAsistenteVigente
{
    [Column("id_asistente")]
    public long? IdAsistente { get; set; }
    [Column("id_asis")]
    [MaxLength(15)]
    public string? IdAsis { get; set; }
    [Column("nombre_completo")]
    public string? NombreCompleto { get; set; }
    [Column("es_externo")]
    public bool? EsExterno { get; set; }
    [Column("correo_contacto")]
    public string? CorreoContacto { get; set; }
    [Column("tiene_correo_institucional")]
    public bool? TieneCorreoInstitucional { get; set; }
    [Column("documento_vigente")]
    [MaxLength(20)]
    public string? DocumentoVigente { get; set; }
    [Column("tipo_documento")]
    [MaxLength(5)]
    public string? TipoDocumento { get; set; }
    [Column("vinculacion")]
    [MaxLength(15)]
    public string? Vinculacion { get; set; }
    [Column("vinculacion_nombre")]
    [MaxLength(60)]
    public string? VinculacionNombre { get; set; }
    [Column("es_interno")]
    public bool? EsInterno { get; set; }
    [Column("exige_programa")]
    public bool? ExigePrograma { get; set; }
    [Column("activo")]
    public bool? Activo { get; set; }
}
