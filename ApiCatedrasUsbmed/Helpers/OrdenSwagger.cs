using Microsoft.OpenApi.Models;
using Swashbuckle.AspNetCore.SwaggerGen;

namespace ApiCatedrasUsbmed.Helpers;

/// <summary>
/// Ordena las secciones de Swagger por UTILIDAD, no por alfabeto.
///
/// Por defecto Swagger UI lista los controladores en orden alfabetico, y con 48 grupos
/// eso deja "Autenticacion" enterrado entre "Asistente" y "Bitacora" — justo el endpoint
/// por el que TODO el mundo tiene que empezar, porque sin su token no funciona nada mas.
///
/// Swagger UI respeta el orden del arreglo `tags` del documento, asi que aqui se declara
/// primero lo que se usa primero y el resto queda alfabetico detras.
/// </summary>
public class OrdenSwagger : IDocumentFilter
{
    /// <summary>Lo que va arriba, en el orden en que se usa de verdad.</summary>
    private static readonly string[] Primero =
    {
        "Autenticacion",   // 1 · sin el token no se hace nada
        "Acceso",          // 2 · el flujo del asistente que escanea el QR
        "Enlace",          // 3 · emitir el QR y la URL
        "Migracion",       // 4 · el archivo plano del ASIS
        "Raiz",            // 5 · ficha de la API y sonda de vida
        "Estructura"       // 6 · metadata de las tablas
    };

    private static readonly Dictionary<string, string> Descripciones = new()
    {
        ["Autenticacion"] = "EMPIECE AQUI. Devuelve el JWT del administrador. "
                          + "Pegue el token en el boton Authorize de arriba.",
        ["Acceso"]        = "Flujo del ASISTENTE que escanea el QR: ver la catedra, pedir la "
                          + "clave al correo, validarla y responder la encuesta. Todos anonimos.",
        ["Enlace"]        = "Emite el enlace de registro de una sesion y genera su QR en PNG.",
        ["Migracion"]     = "Genera el archivo plano de tres columnas que se sube al ASIS.",
        ["Raiz"]          = "Ficha de la API y sonda de vida.",
        ["Estructura"]    = "Metadata de las tablas, leida de information_schema."
    };

    public void Apply(OpenApiDocument doc, DocumentFilterContext contexto)
    {
        var existentes = doc.Paths
            .SelectMany(p => p.Value.Operations.Values)
            .SelectMany(o => o.Tags ?? new List<OpenApiTag>())
            .Select(t => t.Name)
            .Where(n => !string.IsNullOrWhiteSpace(n))
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .ToList();

        var ordenadas = Primero.Where(p => existentes.Contains(p, StringComparer.OrdinalIgnoreCase))
            .Concat(existentes.Where(e => !Primero.Contains(e, StringComparer.OrdinalIgnoreCase))
                              .OrderBy(e => e, StringComparer.OrdinalIgnoreCase));

        doc.Tags = ordenadas
            .Select(n => new OpenApiTag
            {
                Name = n,
                Description = Descripciones.TryGetValue(n, out var d) ? d : null
            })
            .ToList();
    }
}
