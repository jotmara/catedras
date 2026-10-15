using Dapper;
using ApiCatedrasUsbmed.Helpers;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;

namespace ApiCatedrasUsbmed.Repositorios;

public class ProcesoEnlaceRepositorio : IProcesoEnlaceRepositorio
{
    private readonly IFabricaConexion _cx;
    public ProcesoEnlaceRepositorio(IFabricaConexion cx) => _cx = cx;

    /// <summary>
    /// Llama a fn_emitir_enlace_api, que envuelve sp_emitir_enlace: revoca el enlace
    /// vigente anterior (RN-14), calcula la ventana con los parametros configurables y
    /// genera el token. Es "el boton" del documento de requisitos.
    /// </summary>
    public async Task<long> EmitirAsync(long idSesion, int? minutosAntes, int? minutosDespues, long? idUsuario)
    {
        using var con = _cx.Crear();
        const string sql = @"SELECT catedras.fn_emitir_enlace_api(@IdSesion, @Antes, @Despues, @Usuario)";
        return await con.ExecuteScalarAsync<long>(sql, new
        {
            IdSesion = idSesion, Antes = minutosAntes, Despues = minutosDespues, Usuario = idUsuario
        });
    }

    public async Task<short> SiguienteReunionAsync(string idEventoAsis)
    {
        using var con = _cx.Crear();
        return await con.ExecuteScalarAsync<short>(
            "SELECT catedras.fn_siguiente_reunion(CAST(@Ev AS char(9)))", new { Ev = idEventoAsis });
    }

    public async Task<(string url, string? rutaQr)?> ObtenerUrlAsync(long idEnlace)
    {
        using var con = _cx.Crear();
        var r = await con.QueryFirstOrDefaultAsync<(string, string?)>(
            "SELECT url_publica, ruta_imagen_qr FROM catedras.enlace_registro WHERE id_enlace = @Id",
            new { Id = idEnlace });
        return r.Item1 is null ? null : r;
    }
}
