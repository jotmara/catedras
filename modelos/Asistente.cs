using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("asistente")]
public class Asistente
{
    [Key]
    [Column("id_asistente")]
    public long IdAsistente { get; set; }
    [Column("id_asis")]
    [MaxLength(15)]
    public string? IdAsis { get; set; }
    [Column("nombres")]
    [Required]
    [MaxLength(100)]
    public string Nombres { get; set; } = string.Empty;
    [Column("apellidos")]
    [Required]
    [MaxLength(100)]
    public string Apellidos { get; set; } = string.Empty;
    [Column("nombre_completo_asis")]
    [MaxLength(200)]
    public string? NombreCompletoAsis { get; set; }
    [Column("correo_institucional")]
    public string? CorreoInstitucional { get; set; }
    [Column("correo_personal")]
    public string? CorreoPersonal { get; set; }
    [Column("celular")]
    [MaxLength(20)]
    public string? Celular { get; set; }
    [Column("es_externo")]
    public bool EsExterno { get; set; }
    [Column("activo")]
    public bool Activo { get; set; }
    [Column("creado_en")]
    public DateTimeOffset CreadoEn { get; set; }
    [Column("fk_lote_carga")]
    public long? FkLoteCarga { get; set; }
}
