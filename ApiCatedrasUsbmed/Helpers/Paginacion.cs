namespace ApiCatedrasUsbmed.Helpers;

/// <summary>
/// Tope de filas de los GET de listado.
///
/// POR QUE EXISTE. Sin tope, GET /api/asistente devuelve las 14.811 personas del maestro
/// -5,3 MB con sus documentos y correos- en una sola llamada. Eso es un problema de dos
/// caras:
///
///   1. Proteccion de datos: una peticion basta para volcar el maestro completo.
///      El plan lo anoto como riesgo (§7.2, punto 3) y hasta ahora no estaba puesto.
///   2. Rendimiento del cliente: la API sirve 1,3 MB en 45 ms, pero el navegador tarda
///      varios segundos en pintar ese JSON. El cuello de botella no es la base.
///
/// El tope NO sustituye a la autorizacion por rol: la complementa.
/// </summary>
public static class Paginacion
{
    /// <summary>Filas que se devuelven cuando el cliente no pide un limite.</summary>
    public const int PorDefecto = 100;

    /// <summary>Techo duro. Ni pidiendo mas se devuelven mas.</summary>
    public const int Maximo = 1000;

    /// <summary>Normaliza lo que pida el cliente: nulo o fuera de rango se ajusta.</summary>
    public static int Resolver(int? solicitado)
    {
        if (solicitado is null || solicitado <= 0) return PorDefecto;
        return solicitado.Value > Maximo ? Maximo : solicitado.Value;
    }
}
