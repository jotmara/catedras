using System.ComponentModel.DataAnnotations.Schema;

namespace ApiCatedrasUsbmed.Modelos;

/// <summary>
/// CONTROL de RN-15: registros hechos fuera de la ventana de su enlace.
/// DEBE DEVOLVER SIEMPRE CERO FILAS. Si alguna vez devuelve algo, es que se desactivo
/// el disparador o que alguien inserto por detras.
///
/// A mano: la vista expone `ventana` como tstzrange. Se proyecta con lower()/upper().
/// </summary>
[Table("v_control_ventana")]
public class VControlVentana
{
    [Column("id_registro")]    public long IdRegistro { get; set; }
    [Column("registrado_en")]  public DateTimeOffset RegistradoEn { get; set; }
    [Column("ventana_inicio")] public DateTimeOffset VentanaInicio { get; set; }
    [Column("ventana_fin")]    public DateTimeOffset VentanaFin { get; set; }
    [Column("origen")]         public string Origen { get; set; } = string.Empty;
}
