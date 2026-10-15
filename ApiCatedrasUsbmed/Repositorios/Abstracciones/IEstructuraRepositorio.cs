namespace ApiCatedrasUsbmed.Repositorios.Abstracciones;

public interface IEstructuraRepositorio
{
    Task<List<dynamic>> ObtenerColumnasAsync(string tabla);
    Task<List<string>> ListarTablasAsync();
}
