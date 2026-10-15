# Constitución del proyecto — Cátedras Abiertas USBMed (Versión 2)

> **Documento permanente.** Estas reglas rigen TODAS las versiones del proyecto (v1, v2 y subsecuentes). Ante cualquier conflicto, la constitución prevalece.
> Específica a la Versión 2: Incorporación de **entidades relacionales con Claves Foráneas (FKs)**, integridad referencial y capas desacopladas.

---

## Artículo 1 — El desarrollo es POR VERSIONES y la especificación manda

- El sistema se construye por **versiones incrementales** (v1, v2, …), cada una con su spec kit propio (documentos 2 a 8).
- **Alcance de la Versión 2:** Entidades de **Estructura Académica** (`facultad`, `dependencia`, `programa_academico`, `alias_programa`), **Identidad y Personas** (`asistente`, `documento_asistente`, `vinculacion_asistente`, `programa_asistente`, `consentimiento_datos`) y **Cátedras y Sesiones** (`catedra`, `sesion`, `ponencia`).
- Una versión está TERMINADA solo cuando aprueba sus criterios de aceptación, pruebas de contrato y validación de integridad referencial; entonces se hace commit y tag (`v2`).

## Artículo 2 — Stack tecnológico: C# y ASP.NET Core (.NET 10 / .NET 8)

- Lenguaje **C#** sobre **ASP.NET Core**: controladores tipados con atributos (`[HttpGet]`, `[HttpPost]`, `[HttpPut]`, `[HttpPatch]`, `[HttpDelete]`), inyección de dependencias nativa, `async/await` en toda la cadena de llamadas.
- **Acceso a datos con Micro-ORM:** Uso estricto de **ADO.NET / Dapper** (`Npgsql`, `Dapper`). **Sin Entity Framework ni ORMs pesados**. El SQL debe ser explícito, visible y 100% parametrizado (`@parametro`).
- **Manejo de columnas generadas y disparadores:** Para entidades como `catedra` (columna generada `nombre_asis`) y `sesion` (disparador de `numero_reunion`), el SQL no inserta manualmente valores calculados por PostgreSQL.

## Artículo 3 — Arquitectura en 4 capas con interfaces desde el día 1

```
HTTP Request 
   ├──► Controller           (Validación DataAnnotations → 422 automático, enrutamiento, try/catch)
   ├──► IServicioDominio     (Reglas de negocio, validación semántica de FKs, excepciones de dominio)
   ├──► IRepositorioDominio  (Contrato desacoplado de persistencia sin acoplamiento a HTTP)
   └──► RepositorioPostgres  (Sentencias SQL parametrizadas ejecutadas con Dapper sobre schema 'catedras')
```

- El controlador no ejecuta SQL ni contiene lógica de negocio.
- El servicio no conoce objetos HTTP (`HttpRequest`, `HttpContext`, `StatusCodes`).
- El repositorio no conoce capas superiores y devuelve exclusivamente modelos o tuplas tipadas.
- Los errores de negocio se propagan mediante excepciones controladas:
  - `ArgumentException` → **400 Bad Request**
  - `NoEncontradoExcepcion` → **404 Not Found**
  - Validación de anotaciones → **422 Unprocessable Entity**
  - Restricción de base de datos (FK / UQ) → **409 Conflict** o **500** controlado.

## Artículo 4 — Despliegue en un solo comando

`docker compose up -d --build` levanta todo el ecosistema de la versión (PostgreSQL 16 en puerto `5432` y Web API en puerto `7045`). El código fuente va montado en volumen con `dotnet watch` para recarga en caliente instantánea.

## Artículo 5 — Base de datos completa e integridad referencial estricta

- La base de datos opera sobre las **37 tablas** del esquema `catedras`.
- En la Versión 2 se activan y prueban formalmente las **claves foráneas salientes y entrantes** entre las entidades académicas, los asistentes y las cátedras programadas.
- Queda terminantemente prohibido deshabilitar restricciones de FKs (`DISABLE TRIGGER ALL` o eliminación de constraints) para forzar inserciones de datos huérfanos.
