using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using Npgsql;

namespace ApiCatedrasUsbmed.Helpers;

/// <summary>
/// Traduce las excepciones de PostgreSQL a codigos HTTP con sentido.
///
/// No existe en la API de referencia, y aqui es imprescindible: las reglas de negocio de
/// esta base viven en restricciones y disparadores que lanzan RAISE EXCEPTION con el texto
/// ya redactado en espanol y con su numero de regla ("RN-15: ... esta fuera de la ventana").
///
/// Devolver eso como 500 seria mentir: es un error del CLIENTE, no del servidor. Y el
/// mensaje del disparador es la mejor documentacion de errores que puede tener el front,
/// asi que se devuelve tal cual.
/// </summary>
public class FiltroExcepcionPostgres : IExceptionFilter
{
    private readonly ILogger<FiltroExcepcionPostgres> _log;

    public FiltroExcepcionPostgres(ILogger<FiltroExcepcionPostgres> log) => _log = log;

    public void OnException(ExceptionContext contexto)
    {
        var pg = contexto.Exception as PostgresException
              ?? contexto.Exception.InnerException as PostgresException;

        if (pg is null) return;   // no es de PostgreSQL: que siga su curso

        var traceId = contexto.HttpContext.TraceIdentifier;

        // El texto del RAISE EXCEPTION ya viene util; los de las restricciones del sistema, no.
        var (estado, mensaje) = pg.SqlState switch
        {
            "23505" => (409, $"Ya existe un registro con esos valores. ({pg.ConstraintName})"),
            "23503" => (400, $"La referencia indicada no existe. ({pg.ConstraintName})"),
            "23502" => (400, $"Falta un dato obligatorio: {pg.ColumnName}."),
            "23514" => (422, TextoRegla(pg)),
            "P0002" => (404, "Registro no encontrado."),
            "22001" => (400, "Un valor excede la longitud permitida."),
            "23P01" => (409, $"El rango se solapa con otro existente. ({pg.ConstraintName})"),
            "42501" => (403, "El usuario de base de datos no tiene permiso para esta operacion."),
            _       => (0, string.Empty)
        };

        if (estado == 0)
        {
            _log.LogError(pg, "PostgresException no mapeada. SqlState={SqlState}", pg.SqlState);
            return;
        }

        // 4xx: es del cliente, se registra como aviso, no como error.
        _log.LogWarning("PostgreSQL {SqlState} -> HTTP {Estado}: {Mensaje}", pg.SqlState, estado, pg.MessageText);

        contexto.Result = new ObjectResult(new { mensaje, traceId, regla = pg.ConstraintName })
        {
            StatusCode = estado
        };
        contexto.ExceptionHandled = true;
    }

    /// <summary>
    /// Un CHECK puede venir de una restriccion declarativa o de un RAISE EXCEPTION de
    /// disparador. En el segundo caso el mensaje ya esta redactado: se devuelve entero.
    /// </summary>
    private static string TextoRegla(PostgresException pg)
    {
        var texto = pg.MessageText ?? string.Empty;

        // Los disparadores de esta base empiezan el mensaje con "RN-xx: ".
        if (texto.StartsWith("RN-", StringComparison.OrdinalIgnoreCase) ||
            texto.StartsWith("R29", StringComparison.OrdinalIgnoreCase))
            return texto;

        // Restriccion declarativa: el nombre dice mas que el mensaje generico del motor.
        return string.IsNullOrWhiteSpace(pg.ConstraintName)
            ? "La operacion incumple una regla de negocio."
            : $"La operacion incumple la regla '{pg.ConstraintName}'.";
    }
}
