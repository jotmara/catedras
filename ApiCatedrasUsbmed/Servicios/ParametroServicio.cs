using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class ParametroServicio : IParametroServicio
{
    private readonly IParametroRepositorio _repo;
    public ParametroServicio(IParametroRepositorio repo) => _repo = repo;

    public Task<List<Parametro>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<Parametro?> ObtenerPorIdAsync(string clave) => _repo.ObtenerPorIdAsync(clave);
    public Task<bool> CrearAsync(Parametro entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(Parametro entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(string clave) => _repo.EliminarAsync(clave);
    public Task<List<Parametro>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<Parametro> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<Parametro> entidades) => _repo.ActualizarLoteAsync(entidades);
}
