using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.IdentityModel.Tokens;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class AutenticacionServicio : IAutenticacionServicio
{
    private readonly IAutenticacionRepositorio _repo;
    private readonly IConfiguration _cfg;

    public AutenticacionServicio(IAutenticacionRepositorio repo, IConfiguration cfg)
    { _repo = repo; _cfg = cfg; }

    public async Task<int> ValidarCredencialesAsync(string usuario, string contrasena)
    {
        var hash = await _repo.ObtenerHashContrasenaAsync(usuario);
        if (hash is null) return 404;
        try { return BCrypt.Net.BCrypt.Verify(contrasena, hash) ? 200 : 401; }
        catch (Exception) { return 401; }   // hash con formato invalido o excepcion al verificar
    }

    /// <summary>
    /// El token lleva los roles VIGENTES como claims, para que [Authorize(Roles="ADMIN")]
    /// funcione sin volver a la base en cada peticion.
    /// </summary>
    public async Task<(string token, DateTime expiracion, List<string> roles)> GenerarTokenAsync(string usuario)
    {
        var roles = await _repo.ObtenerRolesVigentesAsync(usuario);

        var clave = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_cfg["Jwt:Key"]!));
        var firma = new SigningCredentials(clave, SecurityAlgorithms.HmacSha256);
        var duracion = _cfg.GetValue<int?>("Jwt:DuracionMinutos") ?? 480;

        var claims = new List<Claim> { new(ClaimTypes.Name, usuario) };
        claims.AddRange(roles.Select(r => new Claim(ClaimTypes.Role, r)));

        var token = new JwtSecurityToken(
            issuer: _cfg["Jwt:Issuer"],
            audience: _cfg["Jwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(duracion),
            signingCredentials: firma);

        await _repo.RegistrarAccesoAsync(usuario);
        return (new JwtSecurityTokenHandler().WriteToken(token), token.ValidTo, roles);
    }
}
