using System.Text.RegularExpressions;

namespace ApiCatedrasUsbmed.Helpers;

/// <summary>
/// Transforma el token [controller] de las rutas a snake_case, para que la URL
/// coincida con el nombre real de la tabla: RegistroAsistencia -> registro_asistencia.
/// </summary>
public partial class SnakeCaseRouteTransformer : IOutboundParameterTransformer
{
    public string? TransformOutbound(object? value) =>
        value is null ? null : SepararPalabras().Replace(value.ToString()!, "$1_$2").ToLowerInvariant();

    [GeneratedRegex("([a-z0-9])([A-Z])")]
    private static partial Regex SepararPalabras();
}
