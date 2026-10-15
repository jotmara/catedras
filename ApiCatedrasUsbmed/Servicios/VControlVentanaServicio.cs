using ApiCatedrasUsbmed.Modelos;
using ApiCatedrasUsbmed.Repositorios.Abstracciones;
using ApiCatedrasUsbmed.Servicios.Abstracciones;

namespace ApiCatedrasUsbmed.Servicios;

public class VControlVentanaServicio : IVControlVentanaServicio
{
    private readonly IVControlVentanaRepositorio _repo;
    public VControlVentanaServicio(IVControlVentanaRepositorio repo) => _repo = repo;
    public Task<List<VControlVentana>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
}
