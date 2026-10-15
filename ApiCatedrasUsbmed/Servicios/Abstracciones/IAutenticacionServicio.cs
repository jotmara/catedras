namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IAutenticacionServicio
{
    Task<int> ValidarCredencialesAsync(string usuario, string contrasena);
    Task<(string token, DateTime expiracion, List<string> roles)> GenerarTokenAsync(string usuario);
}
