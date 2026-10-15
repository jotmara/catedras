using QRCoder;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class ProcesoEnlaceServicio : IProcesoEnlaceServicio
{
    private readonly IProcesoEnlaceRepositorio _repo;
    public ProcesoEnlaceServicio(IProcesoEnlaceRepositorio repo) => _repo = repo;

    public Task<long> EmitirAsync(long idSesion, int? antes, int? despues, long? idUsuario) =>
        _repo.EmitirAsync(idSesion, antes, despues, idUsuario);

    public Task<short> SiguienteReunionAsync(string idEventoAsis) =>
        _repo.SiguienteReunionAsync(idEventoAsis);

    /// <summary>
    /// El PNG del QR lo genera la API, no la base. La base solo guarda la RUTA RELATIVA,
    /// y la restriccion chk_enlace_ruta_qr rechaza rutas absolutas.
    /// </summary>
    public async Task<byte[]?> GenerarQrAsync(long idEnlace)
    {
        var datos = await _repo.ObtenerUrlAsync(idEnlace);
        if (datos is null) return null;

        using var generador = new QRCodeGenerator();
        using var info = generador.CreateQrCode(datos.Value.url, QRCodeGenerator.ECCLevel.Q);
        var png = new PngByteQRCode(info);
        return png.GetGraphic(20);
    }
}
