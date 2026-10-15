using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class EstructuraRepositorio : IEstructuraRepositorio
{
    private readonly IFabricaConexion _cx;
    public EstructuraRepositorio(IFabricaConexion cx) => _cx = cx;

    public async Task<List<string>> ListarTablasAsync()
    {
        using var con = _cx.Crear();
        const string sql = @"SELECT table_name FROM information_schema.tables
                              WHERE table_schema = 'catedras'
                              ORDER BY table_type, table_name";
        return (await con.QueryAsync<string>(sql)).AsList();
    }

    public async Task<List<dynamic>> ObtenerColumnasAsync(string tabla)
    {
        using var con = _cx.Crear();
        const string sql = @"SELECT column_name, data_type, is_nullable,
                                    character_maximum_length, column_default,
                                    is_generated, identity_generation
                               FROM information_schema.columns
                              WHERE table_schema = 'catedras' AND table_name = @Tabla
                              ORDER BY ordinal_position";
        return (await con.QueryAsync(sql, new { Tabla = tabla })).AsList();
    }
}
