using System.Data;
using Npgsql;

namespace ApiCatedrasUsbmed.Helpers;

public interface IFabricaConexion
{
    /// <summary>Conexion administrativa (rol con permisos de gestion).</summary>
    IDbConnection Crear();

    /// <summary>
    /// Conexion de la APLICACION PUBLICA, con el rol minimo. Se usa en el camino
    /// de acceso del asistente.
    /// </summary>
    IDbConnection CrearApp();
}

/// <summary>
/// Unico proveedor: PostgreSQL.
///
/// DESVIACION DELIBERADA respecto de ApiEvalFormativaUsbmed, que trae un switch
/// multi-proveedor (SqlServer, MySQL, Oracle, SQLite). Aqui seria codigo que MIENTE:
/// el esquema usa citext, inet, jsonb, uuid, tstzrange, EXCLUDE USING gist e indices
/// parciales. Ninguno de esos motores puede sostener este modelo, asi que anunciar
/// soporte para ellos seria un contrato falso.
///
/// Dos cadenas, para no perder el diseno de permisos de 17-usuarios-permisos.sql:
/// si la API se conectara siempre como superusuario, los cuatro roles comprobados
/// alli no servirian de nada.
/// </summary>
public class FabricaConexion : IFabricaConexion
{
    private readonly string _admin;
    private readonly string _app;

    public FabricaConexion(IConfiguration cfg)
    {
        var admin = cfg.GetConnectionString("Postgres");
        if (string.IsNullOrWhiteSpace(admin))
            throw new InvalidOperationException("ConnectionStrings:Postgres no esta configurada.");

        // OJO: appsettings.json trae "PostgresApp": "" a proposito (fail-fast), y la cadena
        // VACIA no es null. Con `?? _admin` la cadena vacia se colaba y Npgsql fallaba con
        // "The ConnectionString property has not been initialized".
        var app = cfg.GetConnectionString("PostgresApp");

        _admin = ConSearchPath(admin);
        _app   = ConSearchPath(string.IsNullOrWhiteSpace(app) ? admin : app);
    }

    /// <summary>
    /// Fija el search_path en la propia cadena de conexion.
    ///
    /// Es imprescindible: varias rutinas del modelo (fn_exportar_asis,
    /// sp_validar_clave_y_registrar y demas) referencian las tablas SIN calificar y se
    /// crearon bajo un `SET search_path` de SCRIPT, que no queda horneado en la funcion.
    /// Llamadas desde una sesion que no lo fija, PostgreSQL responde
    /// "no existe la relacion registro_asistencia" aunque exista.
    ///
    /// El arreglo de fondo esta en sql/19-funciones-api.sql, que ademas hace
    /// ALTER FUNCTION ... SET search_path sobre las rutinas de la base. Esto es el
    /// cinturon: aunque alguien despliegue sin ese script, la API sigue funcionando.
    /// </summary>
    private static string ConSearchPath(string cs)
    {
        if (cs.Contains("Search Path", StringComparison.OrdinalIgnoreCase) ||
            cs.Contains("SearchPath",  StringComparison.OrdinalIgnoreCase))
            return cs;

        var sep = cs.TrimEnd().EndsWith(';') ? string.Empty : ";";
        return $"{cs}{sep}Search Path=catedras,public";
    }

    public IDbConnection Crear()    => new NpgsqlConnection(_admin);
    public IDbConnection CrearApp() => new NpgsqlConnection(_app);
}
