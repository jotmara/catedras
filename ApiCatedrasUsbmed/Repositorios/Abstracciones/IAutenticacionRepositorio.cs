namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IAutenticacionRepositorio
{
    /// <summary>Hash BCrypt del usuario, o null si no existe o esta inactivo.</summary>
    Task<string?> ObtenerHashContrasenaAsync(string usuario);

    /// <summary>Roles VIGENTES del usuario (fecha_fin IS NULL).</summary>
    Task<List<string>> ObtenerRolesVigentesAsync(string usuario);

    Task RegistrarAccesoAsync(string usuario);
}
