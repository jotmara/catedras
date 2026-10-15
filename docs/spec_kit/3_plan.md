# Plan técnico — Versión 1: `sede` + PostgreSQL Completo (37 Tablas)

> **Versión 1** · CÓMO construir lo especificado en [2_spec.md](2_spec.md).
> El porqué de cada decisión: [4_research.md](4_research.md) · modelo de 37 tablas: [5_data_model.md](5_data_model.md)
> contratos exactos: [6_contracts.md](6_contracts.md) · orden: [8_tasks.md](8_tasks.md).

---

## 1. Stack

| Pieza | Elección | Por qué |
|---|---|---|
| Lenguaje / framework | **C# sobre ASP.NET Core (.NET 10 / .NET 8)** | Controladores tipados con atributos, DI integrada, async nativo |
| Acceso a datos | **ADO.NET / Dapper** (`Npgsql`, `Dapper`) con SQL parametrizado | SQL visible, alto desempeño y sin sobrecarga de ORM |
| Validación | **Peticiones por verbo (DTOs)** con DataAnnotations (`[Required]`, `[StringLength]`…) | El framework valida el body contra la petición y responde 422 automático |
| Motor de Base de Datos | **PostgreSQL 16** (contenedor oficial Alpine, puerto 5432) | Motor relacional con las 37 tablas, 52 FKs y datos reales provistos |
| Contenedor de la API | `mcr.microsoft.com/dotnet/sdk:8.0` + `dotnet watch` | Hot-reload durante el desarrollo continuo |

## 2. Estructura del proyecto

```
(raíz del proyecto)
├── docker-compose.yml                # UN comando: postgres (5432) + api-catedras (7045)
├── db/
│   └── bdcatedras_postgres.sql       # Script oficial completo: 37 tablas, 52 FKs y datos semilla
└── api_catedras/
    ├── ApiCatedras.csproj            # Proyecto .NET (Npgsql, Dapper, Swashbuckle)
    ├── Program.cs                    # DI + pipeline HTTP + 422 factory + Swagger
    ├── appsettings.json              # Cadena de conexión a postgres
    ├── Dockerfile                    # sdk + dotnet watch (puerto 7045)
    ├── Modelos/
    │   └── Sede.cs                   # Entidad Sede mapeada a la tabla sede
    ├── Peticiones/
    │   ├── SedeCrear.cs              # Petición POST (campos obligatorios)
    │   ├── SedeReemplazo.cs          # Petición PUT (reemplazo completo)
    │   └── SedeActualizar.cs         # Petición PATCH (campos opcionales)
    ├── Controllers/
    │   └── SedeController.cs         # Controlador REST para /api/sede (5 verbos)
    ├── Servicios/
    │   ├── IServicioSede.cs          # Interfaz de lógica de negocio
    │   └── ServicioSede.cs           # Reglas de negocio y validación
    ├── Repositorios/
    │   ├── IRepositorioSede.cs       # Interfaz de persistencia
    │   └── RepositorioSedePostgres.cs # Sentencias SQL parametrizadas
    ├── Excepciones/
    │   └── NoEncontradoExcepcion.cs  # Excepción mapeada a HTTP 404
    └── pruebas/
        ├── PruebaCapas.csproj        # Proyecto consola de pruebas
        └── Programa.cs               # Prueba de capas con Mock en memoria
```

## 3. Arquitectura en capas (flujo de una petición)

```
HTTP → ASP.NET routing        (atributos [HttpGet]/[HttpPost]…)
     → validación de la PETICIÓN (anotaciones → 422 automático)
     → SedeController         (manejo de status codes y try/catch)
     → IServicioSede          (reglas de negocio y validaciones semánticas)
     → IRepositorioSede       (contrato de persistencia)
     → RepositorioSedePostgres (SQL parametrizado con Dapper/Npgsql)
     → PostgreSQL (catedras: tabla sede dentro del esquema de 37 tablas)
```

## 4. Decisiones de diseño clave

### 4.1 Interface del Repositorio
```csharp
public interface IRepositorioSede
{
    Task<List<Sede>> ObtenerTodosAsync(int limite);
    Task<Sede?> ObtenerPorCodigoAsync(string codigo);
    Task CrearAsync(Sede sede);
    Task<int> ActualizarAsync(string codigo, Dictionary<string, object> datos);
    Task<int> EliminarAsync(string codigo);
}
```

### 4.2 SQL del repositorio (PostgreSQL)
```sql
SELECT id_sede AS IdSede, codigo, nombre, direccion, telefono, activo 
FROM catedras.sede ORDER BY codigo LIMIT @limite;

SELECT id_sede AS IdSede, codigo, nombre, direccion, telefono, activo 
FROM catedras.sede WHERE codigo = @codigo;

INSERT INTO catedras.sede (codigo, nombre, direccion, telefono, activo) 
VALUES (@Codigo, @Nombre, @Direccion, @Telefono, true);

UPDATE catedras.sede SET ... WHERE codigo = @codigo_clave;

DELETE FROM catedras.sede WHERE codigo = @codigo;
```

### 4.3 Manejo de Errores y Excepciones
| Escenario | HTTP Status |
|---|---|
| Error de validación en DataAnnotations | 422 Unprocessable Entity (`errores: [...]`) |
| ArgumentException (regla de negocio / body vacío en PATCH) | 400 Bad Request |
| NoEncontradoExcepcion | 404 Not Found |
| Violación de FK (ej. borrar sede con sesiones activas) o error BD | 500 Internal Server Error |
