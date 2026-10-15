using System.Reflection;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace ApiCatedrasUsbmed.Helpers;

/// <summary>
/// Genera el SQL de INSERT y UPDATE leyendo los atributos del modelo.
/// La reflexion ocurre al CONSTRUIR el SQL, no en cada request.
/// </summary>
public static class ConexionHelper
{
    // Nombre REAL de columna: honra [Column("...")]; si no esta, usa el nombre de la propiedad.
    // Clave para columnas snake_case (id_sesion, fecha_ini): la propiedad es PascalCase (IdSesion)
    // pero la columna lleva guion bajo, asi que NO se puede derivar con p.Name.ToLower().
    private static string Col(PropertyInfo p) =>
        p.GetCustomAttribute<ColumnAttribute>()?.Name ?? p.Name;

    /// <summary>
    /// Columna calculada por la base de datos. PostgreSQL RECHAZA cualquier INSERT o UPDATE
    /// que la mencione.
    ///
    /// Esta comprobacion NO esta en la API de referencia (ApiEvalFormativaUsbmed) porque su
    /// esquema no tiene columnas generadas. Aqui es obligatoria: catedra.nombre_asis es
    /// GENERATED ALWAYS AS (left(nombre,30)) STORED, y sin esto TODO POST /api/catedra
    /// fallaria con el error 42601 de PostgreSQL.
    /// </summary>
    private static bool EsGenerada(PropertyInfo p) =>
        p.GetCustomAttribute<DatabaseGeneratedAttribute>()?.DatabaseGeneratedOption
            == DatabaseGeneratedOption.Computed;

    /// <summary>
    /// pkAutogenerada=true: la base asigna la PK (identity) y se excluye del INSERT.
    /// pkAutogenerada=false: PK natural (ej. codigo varchar) - el valor viene en la entidad.
    /// </summary>
    public static string GenerarInsertSQL<T>(string tabla, bool pkAutogenerada = true) where T : class
    {
        var todas = typeof(T).GetProperties(BindingFlags.Public | BindingFlags.Instance);
        var props = todas
            .Where(p => !EsGenerada(p))
            .Where(p => !pkAutogenerada || !p.IsDefined(typeof(KeyAttribute), true))
            .ToArray();

        if (props.Length == 0)
            throw new InvalidOperationException($"La tabla '{tabla}' no tiene columnas insertables.");

        var cols = string.Join(", ", props.Select(Col));
        var pars = string.Join(", ", props.Select(p => "@" + p.Name));
        return $"INSERT INTO {tabla} ({cols}) VALUES ({pars})";
    }

    /// <summary>
    /// pk = nombre REAL de la columna PK (ej. id_sesion). Admite clave compuesta.
    /// El parametro Dapper usa el nombre de la PROPIEDAD.
    /// </summary>
    public static string GenerarUpdateSQL<T>(string tabla, params string[] pk) where T : class
    {
        if (pk is null || pk.Length == 0)
            throw new ArgumentException("Hay que indicar al menos una columna de clave primaria.", nameof(pk));

        var todas = typeof(T).GetProperties(BindingFlags.Public | BindingFlags.Instance);

        // Del SET se excluyen las columnas de la PK y las generadas por la base.
        var props = todas
            .Where(p => !EsGenerada(p))
            .Where(p => !pk.Any(k => Col(p).Equals(k, StringComparison.OrdinalIgnoreCase)))
            .ToArray();

        if (props.Length == 0)
            throw new InvalidOperationException($"La tabla '{tabla}' no tiene columnas para actualizar.");

        var sets = string.Join(", ", props.Select(p => $"{Col(p)} = @{p.Name}"));

        var where = string.Join(" AND ", pk.Select(k =>
        {
            var prop = todas.FirstOrDefault(p => Col(p).Equals(k, StringComparison.OrdinalIgnoreCase));
            var param = prop?.Name ?? (char.ToUpper(k[0]) + k[1..]);
            return $"{k} = @{param}";
        }));

        return $"UPDATE {tabla} SET {sets} WHERE {where}";
    }
}
