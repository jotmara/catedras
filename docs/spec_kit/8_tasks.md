# Tareas — Versión 1: api_catedras con sede + PostgreSQL (C#/ASP.NET Core)

> **Versión 1** · Orden de construcción paso a paso para la entidad Sede.

---

## Fase 0 — Base de datos y entorno Docker

- [X] Crear el script SQL `db/bdcatedras_postgres.sql` con la definición de la tabla `sede` y los datos semilla iniciales.
- [X] Configurar `docker-compose.yml` con el servicio `postgres` (PostgreSQL 16 Alpine, mapeo al puerto 5432, script montado en `/docker-entrypoint-initdb.d/`).
- [X] Estructurar las carpetas del proyecto .NET en `api_catedras/` (`Modelos/`, `Peticiones/`, `Controllers/`, `Servicios/`, `Repositorios/`, `Excepciones/`, `pruebas/`).

**Verificación:** `docker compose up -d` levanta `postgres (healthy)` y la base `catedras` contiene la tabla `sede` con sus registros iniciales.

## Fase 1 — Modelo Entidad Sede y Proyecto Base

- [X] Configurar `ApiCatedras.csproj` (.NET Web, paquetes `Npgsql`, `Dapper`, `Swashbuckle.AspNetCore`).
- [X] Configurar `appsettings.json` con la cadena de conexión a PostgreSQL.
- [X] Crear `Modelos/Sede.cs` con propiedades tipadas (`Codigo`, `Nombre`, `Direccion`, `Telefono`).

**Verificación:** `dotnet build` compila correctamente.

## Fase 2 — DTOs de Petición y Excepciones

- [X] Crear `Peticiones/SedeCrear.cs` (POST: todos los campos requeridos).
- [X] Crear `Peticiones/SedeReemplazo.cs` (PUT: nombre, direccion y telefono requeridos).
- [X] Crear `Peticiones/SedeActualizar.cs` (PATCH: todos los campos opcionales).
- [X] Crear `Excepciones/NoEncontradoExcepcion.cs` para el mapeo a error 404.


**Verificación:** `dotnet build` sin errores.

## Fase 3 — Capa de Repositorio (Acceso a Datos)

- [X] Crear interfaz `Repositorios/IRepositorioSede.cs` con métodos asíncronos (`ObtenerTodosAsync`, `ObtenerPorCodigoAsync`, `CrearAsync`, `ActualizarAsync`, `EliminarAsync`).
- [X] Implementar `Repositorios/RepositorioSedePostgres.cs` usando SQL parametrizado (`LIMIT @limite`, `@Codigo`, `@Nombre`, etc.).

**Verificación:** `dotnet build` compila sin errores.

## Fase 4 — Capa de Servicio y Pruebas Desacopladas

- [X] Crear interfaz `Servicios/IServicioSede.cs`.
- [X] Implementar `Servicios/ServicioSede.cs` inyectando `IRepositorioSede`, con validaciones de negocio (límite > 0, PATCH no vacío, excepciones `ArgumentException` y `NoEncontradoExcepcion`).
- [X] Implementar prueba de capas en `pruebas/Programa.cs` con un repositorio falso en memoria (Mock).

**Verificación:** `dotnet run --project api_catedras/pruebas` ejecuta y confirma el criterio de capas.

## Fase 5 — Capa de Controladores y Pipeline ASP.NET Core

- [X] Implementar `Controllers/SedeController.cs` con rutas REST `/api/sede` y los 5 verbos HTTP.
- [X] Configurar `Program.cs`: Inyección de dependencias (`AddScoped`), fábrica de respuesta 422 (`InvalidModelStateResponseFactory`), configuración Swagger y endpoint `/` de diagnóstico.

**Verificación:** Ejecutar la API y probar endpoints mediante Swagger en `http://localhost:7045/swagger`.

## Fase 6 — Docker Compose y Smoke Test Completo

- [X] Configurar `api_catedras/Dockerfile` con hot-reload (`dotnet watch`).
- [X] Completar `docker-compose.yml` integrando el servicio `api-catedras` y `postgres`.
- [ ] Ejecutar el Smoke Test detallado en [7_quickstart.md](7_quickstart.md).
