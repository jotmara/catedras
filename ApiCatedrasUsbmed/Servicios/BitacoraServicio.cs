using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class BitacoraServicio : IBitacoraServicio
{
    private readonly IBitacoraRepositorio _repo;
    public BitacoraServicio(IBitacoraRepositorio repo) => _repo = repo;

    public Task<List<Bitacora>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<Bitacora?> ObtenerPorIdAsync(long idBitacora) => _repo.ObtenerPorIdAsync(idBitacora);
    public Task<bool> CrearAsync(Bitacora entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync(Bitacora entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync(long idBitacora) => _repo.EliminarAsync(idBitacora);
    public Task<List<Bitacora>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<Bitacora> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<Bitacora> entidades) => _repo.ActualizarLoteAsync(entidades);
}
