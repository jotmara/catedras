namespace ApiCatedrasUsbmed.Servicios.Abstracciones;

public interface IEstructuraServicio
{
    Task<List<dynamic>> ObtenerColumnasAsync(string tabla);
    Task<List<string>> ListarTablasAsync();
}
