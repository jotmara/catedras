using System.Data;
using Dapper;

namespace ApiCatedrasUsbmed.Helpers;

/// <summary>
/// Convierte entre las columnas date (que el driver entrega como DateTime)
/// y las propiedades DateOnly de los modelos.
/// </summary>
public class DateOnlyTypeHandler : SqlMapper.TypeHandler<DateOnly>
{
    public override DateOnly Parse(object value) => value switch
    {
        DateOnly d  => d,
        DateTime dt => DateOnly.FromDateTime(dt),
        string s    => DateOnly.Parse(s),
        _ => throw new InvalidCastException($"No se puede convertir {value.GetType()} a DateOnly")
    };

    public override void SetValue(IDbDataParameter parameter, DateOnly value)
    {
        parameter.DbType = DbType.Date;
        parameter.Value  = value.ToDateTime(TimeOnly.MinValue);
    }
}

/// <summary>Igual, para las columnas date nulables.</summary>
public class DateOnlyNullableTypeHandler : SqlMapper.TypeHandler<DateOnly?>
{
    public override DateOnly? Parse(object value) => value switch
    {
        null        => null,
        DateOnly d  => d,
        DateTime dt => DateOnly.FromDateTime(dt),
        string s    => DateOnly.Parse(s),
        _ => throw new InvalidCastException($"No se puede convertir {value.GetType()} a DateOnly?")
    };

    public override void SetValue(IDbDataParameter parameter, DateOnly? value)
    {
        parameter.DbType = DbType.Date;
        parameter.Value  = value.HasValue ? value.Value.ToDateTime(TimeOnly.MinValue) : DBNull.Value;
    }
}
