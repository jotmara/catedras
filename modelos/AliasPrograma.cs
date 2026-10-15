using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace ApiCatedrasUsbmed.Modelos;

[Table("alias_programa")]
public class AliasPrograma
{
    [Key]
    [Column("id_alias")]
    public long IdAlias { get; set; }
    [Column("texto_normalizado")]
    [Required]
    [MaxLength(200)]
    public string TextoNormalizado { get; set; } = string.Empty;
    [Column("fk_programa")]
    [Required]
    [MaxLength(5)]
    public string FkPrograma { get; set; } = string.Empty;
    [Column("origen")]
    [Required]
    [MaxLength(30)]
    public string Origen { get; set; } = string.Empty;
    [Column("creado_en")]
    public DateTimeOffset CreadoEn { get; set; }
}
