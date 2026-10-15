using System.Data;
using System.Net;
using Dapper;

namespace ApiCatedrasUsbmed.Helpers;

/// <summary>
/// Las columnas inet (registro_asistencia.ip, clave_acceso.ip_solicitud) las entrega Npgsql
/// como IPAddress, que serializa a JSON como un objeto con propiedades internas del tipo.
/// Se exponen como string, que es lo que un cliente REST espera y sabe enviar.
///
/// No existe en la API de referencia: su esquema no tiene columnas inet.
/// </summary>
public class InetTypeHandler : SqlMapper.TypeHandler<string?>
{
    public override string? Parse(object value) => value switch
    {
        null          => null,
        IPAddress ip  => ip.ToString(),
        string s      => s,
        _             => value.ToString()
    };

    public override void SetValue(IDbDataParameter parameter, string? value)
    {
        if (string.IsNullOrWhiteSpace(value)) { parameter.Value = DBNull.Value; return; }
        if (!IPAddress.TryParse(value, out var ip))
            throw new ArgumentException($"Direccion IP invalida: '{value}'.");

        if (parameter is Npgsql.NpgsqlParameter np)
        {
            np.NpgsqlDbType = NpgsqlTypes.NpgsqlDbType.Inet;
            np.Value = ip;
        }
        else parameter.Value = ip;
    }
}
