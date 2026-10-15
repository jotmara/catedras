using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace ApiCatedrasUsbmed.Modelos;

/// <summary>
/// Enlace de registro de una sesion: el QR o la URL.
///
/// ESCRITO A MANO, no generado. La columna `ventana` de la base es un tstzrange, que no
/// tiene equivalente en C#: Npgsql lo entrega como NpgsqlRange&lt;DateTimeOffset&gt;, que
/// serializa a un JSON que ningun cliente REST sabe construir.
///
/// La alternativa facil seria cambiar la base a dos columnas timestamptz. Se descarto:
/// el rango es justamente lo que hace DECLARATIVAS dos reglas — el EXCLUDE USING gist
/// que impide enlaces solapados (RN-36) y la contencion @> de la ventana (RN-15). Con
/// dos columnas, las dos volverian a ser codigo que alguien tendria que mantener.
///
/// Asi que se adapta la API, no el modelo: se exponen `ventana_inicio` y `ventana_fin`,
/// y EnlaceRegistroRepositorio construye el rango con tstzrange(). Es el UNICO repositorio
/// con SQL escrito a mano.
/// </summary>
[Table("enlace_registro")]
public class EnlaceRegistro
{
    [Key]
    [Column("id_enlace")]
    public long IdEnlace { get; set; }

    [Column("fk_sesion")]
    public long FkSesion { get; set; }

    [Column("token")]
    public Guid Token { get; set; }

    [Column("url_publica")]
    [Required]
    [MaxLength(300)]
    public string UrlPublica { get; set; } = string.Empty;

    [Column("ruta_imagen_qr")]
    [MaxLength(300)]
    public string? RutaImagenQr { get; set; }

    /// <summary>QR o ENLACE. Debe concordar con la modalidad de la sesion (RN-13).</summary>
    [Column("canal")]
    [Required]
    [MaxLength(10)]
    public string Canal { get; set; } = string.Empty;

    /// <summary>Proyeccion de lower(ventana). En la base es la cota inferior del tstzrange.</summary>
    [Column("ventana_inicio")]
    public DateTimeOffset VentanaInicio { get; set; }

    /// <summary>Proyeccion de upper(ventana).</summary>
    [Column("ventana_fin")]
    public DateTimeOffset VentanaFin { get; set; }

    [Column("usos_maximos")]
    public int? UsosMaximos { get; set; }

    [Column("revocado_en")]
    public DateTimeOffset? RevocadoEn { get; set; }

    [Column("fk_usuario_crea")]
    public long? FkUsuarioCrea { get; set; }

    [Column("creado_en")]
    public DateTimeOffset CreadoEn { get; set; }
}
