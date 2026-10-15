using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class AutenticacionRepositorio : IAutenticacionRepositorio
{
    private readonly IFabricaConexion _cx;
    public AutenticacionRepositorio(IFabricaConexion cx) => _cx = cx;

    /// <summary>
    /// Resuelve al usuario por CORREO, igual que ApiEvalFormativaUsbmed.
    ///
    /// El correo NO esta en la tabla usuario: esta en asistente, porque un administrador
    /// ES una persona del ASIS y no se duplican sus datos. De ahi la reunion.
    /// Se aceptan tambien el correo personal y el login de usuario, para no dejar fuera
    /// a quien no tenga correo institucional (el caso de Rutas de Paz).
    /// </summary>
    private const string PorCorreo = @"
          FROM catedras.usuario u
          JOIN catedras.asistente a ON a.id_asistente = u.fk_asistente
         WHERE u.activo
           AND (a.correo_institucional = @Login::citext
             OR a.correo_personal      = @Login::citext
             OR u.usuario              = @Login)";

    public async Task<string?> ObtenerHashContrasenaAsync(string login)
    {
        using var con = _cx.Crear();
        return await con.QueryFirstOrDefaultAsync<string?>(
            "SELECT u.clave_hash " + PorCorreo, new { Login = login });
    }

    /// <summary>
    /// Solo los roles VIGENTES. rol_por_usuario es historico -lleva fecha_ini en la clave
    /// primaria para que alguien pueda recuperar un rol que ya tuvo-, asi que sin el filtro
    /// por fecha_fin un administrador destituido seguiria siendo administrador.
    /// </summary>
    public async Task<List<string>> ObtenerRolesVigentesAsync(string login)
    {
        using var con = _cx.Crear();
        var sql = @"SELECT ru.fk_rol
                      FROM catedras.rol_por_usuario ru
                     WHERE ru.fk_usuario = (SELECT u.id_usuario " + PorCorreo + @")
                       AND ru.fecha_ini <= current_date
                       AND (ru.fecha_fin IS NULL OR ru.fecha_fin >= current_date)";
        return (await con.QueryAsync<string>(sql, new { Login = login })).AsList();
    }

    public async Task RegistrarAccesoAsync(string login)
    {
        using var con = _cx.Crear();
        var sql = @"UPDATE catedras.usuario SET ultimo_acceso = now()
                     WHERE id_usuario = (SELECT u.id_usuario " + PorCorreo + ")";
        await con.ExecuteAsync(sql, new { Login = login });
    }
}
