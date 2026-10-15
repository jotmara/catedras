using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class ConsentimientoDatosServicio : IConsentimientoDatosServicio
{
    private readonly IConsentimientoDatosRepositorio _repo;
    public ConsentimientoDatosServicio(IConsentimientoDatosRepositorio repo) => _repo = repo;

    public Task<List<ConsentimientoDatos>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<ConsentimientoDatos?> ObtenerPorIdAsync(long idConsentimiento) => _repo.ObtenerPorIdAsync(idConsentimiento);
    public Task<bool> CrearAsync(ConsentimientoDatos entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(ConsentimientoDatos entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idConsentimiento) => _repo.EliminarAsync(idConsentimiento);
    public Task<List<ConsentimientoDatos>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<ConsentimientoDatos> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<ConsentimientoDatos> entidades) => _repo.ActualizarLoteAsync(entidades);
}
