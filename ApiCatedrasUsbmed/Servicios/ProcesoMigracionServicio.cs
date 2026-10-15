using System.Text;
using ClosedXML.Excel;
using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class ProcesoMigracionServicio : IProcesoMigracionServicio
{
    private readonly IProcesoMigracionRepositorio _repo;
    private readonly IConfiguration _cfg;
    private readonly ILogger<ProcesoMigracionServicio> _log;

    public ProcesoMigracionServicio(
        IProcesoMigracionRepositorio repo,
        IConfiguration cfg,
        ILogger<ProcesoMigracionServicio> log)
    {
        _repo = repo;
        _cfg = cfg;
        _log = log;
    }

    public Task<List<FilaArchivoAsis>> ExportarAsync(long idSesion) => _repo.ExportarAsync(idSesion);
    public Task<long> GenerarLoteAsync(long idSesion, long? idUsuario) => _repo.GenerarLoteAsync(idSesion, idUsuario);
    public Task<bool> RegistrarResultadoAsync(long idLote, ResultadoLote r) => _repo.RegistrarResultadoAsync(idLote, r);

    /// <summary>
    /// Generación del archivo plano en formato Excel (XLSX).
    /// </summary>
    public async Task<(byte[] contenido, string nombre)?> GenerarArchivoAsync(long idSesion)
    {
        var filas = await _repo.ExportarAsync(idSesion);
        if (filas.Count == 0) return null;

        var nombre = await _repo.NombreArchivoAsync(idSesion) ?? $"ME_CATEDRA_{idSesion}.xlsx";

        using var libro = new XLWorkbook();
        var hoja = libro.AddWorksheet("Hoja1");

        for (var i = 0; i < filas.Count; i++)
        {
            var f = filas[i];
            hoja.Cell(i + 1, 1).SetValue(f.Reunion);
            hoja.Cell(i + 1, 2).SetValue(f.IdAsis.Trim());
            hoja.Cell(i + 1, 2).Style.NumberFormat.Format = "@";
            hoja.Cell(i + 1, 3).SetValue(f.Programa.Trim());
            hoja.Cell(i + 1, 3).Style.NumberFormat.Format = "@";
        }

        using var ms = new MemoryStream();
        libro.SaveAs(ms);
        return (ms.ToArray(), nombre);
    }

    /// <summary>
    /// Requerimiento CIDEH: Generación de archivo plano delimitado en CSV limpio para ASIS/Oracle.
    /// Tres columnas exactas sin encabezado para ingesta directa por el motor.
    /// </summary>
    public async Task<(byte[] contenido, string nombre)?> GenerarCsvAsync(long idSesion)
    {
        var filas = await _repo.ExportarAsync(idSesion);
        if (filas.Count == 0) return null;

        var nombreBase = await _repo.NombreArchivoAsync(idSesion) ?? $"ME_CATEDRA_{idSesion}";
        var nombreCsv = Path.ChangeExtension(nombreBase, ".csv");

        var sb = new StringBuilder();
        foreach (var f in filas)
        {
            // Formato estándar ASIS delimitado por comas: Reunion,IdAsis,Programa
            sb.AppendLine($"{f.Reunion},{f.IdAsis.Trim()},{f.Programa.Trim()}");
        }

        var bytes = Encoding.UTF8.GetBytes(sb.ToString());
        return (bytes, nombreCsv);
    }

    /// <summary>
    /// Requerimiento CIDEH: Deposita automáticamente el archivo CSV en la carpeta compartida / SFTP para Oracle.
    /// </summary>
    public async Task<(bool exito, string ruta, int filas)> ExportarACarpetaAsync(long idSesion, string? rutaDestino)
    {
        var csv = await GenerarCsvAsync(idSesion);
        if (csv is null) return (false, "No hay registros disponibles para exportar.", 0);

        var carpeta = rutaDestino 
            ?? _cfg["Asis:CarpetaDestino"] 
            ?? Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "exportaciones_asis");

        if (!Directory.Exists(carpeta))
        {
            Directory.CreateDirectory(carpeta);
        }

        var rutaCompleta = Path.Combine(carpeta, csv.Value.nombre);
        await File.WriteAllBytesAsync(rutaCompleta, csv.Value.contenido);

        _log.LogInformation("Archivo CSV exportado exitosamente a la carpeta compartida: {Ruta}", rutaCompleta);

        var filas = await _repo.ExportarAsync(idSesion);
        return (true, rutaCompleta, filas.Count);
    }
}
