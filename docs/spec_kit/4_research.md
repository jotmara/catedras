# Investigación y decisiones — Versión 1: Tablas Sin Claves Foráneas (10 Tablas Maestras) + PostgreSQL Completo (37 Tablas)

> **Versión 1 / Primera Entrega** · **Lectura de Arquitectura y Decisiones** (el porqué de las decisiones del plan,
> con las alternativas que se evaluaron y descartaron). Complementa a
> [2_spec.md](2_spec.md), [3_plan.md](3_plan.md) y [5_data_model.md](5_data_model.md); el orden de trabajo está en [8_tasks.md](8_tasks.md).

---

## D1 — Alcance de la Versión 1: Las 10 Tablas Sin Claves Foráneas (Tablas Maestras)

**Alternativa descartada:** Crear un esquema fragmentado de base de datos tabla por tabla o implementar tablas dependientes con relaciones complejas antes de consolidar los catálogos base.
**Decisión:** El alcance aplicativo de la **Primera Entrega / Versión 1** abarca el conjunto completo de las **10 tablas independientes (sin claves foráneas salientes)**, mientras que el contenedor PostgreSQL despliega la base de datos con las **37 tablas** (10 independientes y 27 dependientes con sus 52 FKs) e índices desde el día 1.

### Lista de las 10 Tablas Sin Claves Foráneas de la Primera Entrega:
1. **`catedras.sede`**: Catálogo de sedes y campus físicos/virtuales (tomada como entidad piloto de referencia para contratos de capas).
2. **`catedras.modalidad`**: Modalidades de impartición (`PRESENCIAL`, `VIRTUAL`, `HÍBRIDO`).
3. **`catedras.tipo_documento`**: Tipos de documento de identidad oficial (`CC`, `TI`, `CE`, `PASAPORTE`).
4. **`catedras.tipo_vinculacion`**: Clasificación institucional (`ESTUDIANTE`, `DOCENTE`, `EGRESADO`, `EXTERNO`).
5. **`catedras.tipo_evento`**: Tipos de evento académico (`CÁTEDRA ABIERTA`, `TALLER`, `CONVERSATORIO`).
6. **`catedras.tipo_pregunta`**: Tipos de reactivo para formularios y encuestas (`ABIERTA`, `ESCALA 1-5`, `SELECCIÓN ÚNICA`).
7. **`catedras.estado_proceso`**: Catálogo de estados de ciclo de vida (`PROGRAMADA`, `ACTIVA`, `CERRADA`, `MIGRADA`).
8. **`catedras.rol`**: Roles de usuario y perfiles de seguridad (`ADMINISTRADOR`, `DOCENTE`, `ESTUDIANTE`, `AUDITOR`).
9. **`catedras.periodo_academico`**: Períodos y calendarios académicos institucionales (`2026-1`, `2026-2`).
10. **`catedras.encuesta`**: Cabecera maestra y definición base de encuestas de satisfacción.

**Por qué:** 
1. **Fundamento Relacional:** Estas 10 tablas no dependen de ninguna otra entidad y son la base indispensable para alimentar las 27 tablas relacionales restantes en entregas posteriores.
2. **Infraestructura Provista:** El script `db/bdcatedras_postgres.sql` crea la infraestructura completa en Docker para validar desde el primer día la integridad referencial y el comportamiento del motor ante restricciones relacionales.
3. **Desarrollo Incremental:** Lo que evoluciona incrementalmente es el software aplicativo (la API, los controladores y servicios), iniciando con las entidades maestras independientes antes de añadir las dependencias y claves foráneas de las entregas 2 y 3.

## D2 — SQL explícito y parametrizado con Dapper / Npgsql

**Alternativa descartada:** Entity Framework Core con migraciones automáticas.
**Decisión:** Uso de `NpgsqlConnection` con `Dapper` ejecutando sentencias SQL fijas y parametrizadas (`@parametro`).
**Por qué:** Cumple el mandamiento de "SQL a la vista" de la constitución, elimina la sobrecarga de consultas generadas en tiempo de ejecución por ORMs pesados y brinda control total sobre las consultas que viajan a PostgreSQL.

## D3 — Arquitectura en capas limpia con Interfaces desde el inicio

**Alternativa descartada:** Minimal APIs concentradas en un solo archivo plano o controladores monolíticos con SQL directo.
**Decisión:** Separación estricta de 4 niveles: `Controller` → `Servicio` → `Repositorio` → `Base de Datos`, comunicados por interfaces de C#.
**Por qué:** Permite pruebas unitarias y de capas sin necesidad de tener PostgreSQL encendido (mediante mocks o repositorios en memoria), garantiza que la lógica de negocio esté aislada de HTTP y facilita el crecimiento ordenado hacia los módulos de cátedras, ponentes y asistencia.

## D4 — Validación en Peticiones (DTOs) por verbo HTTP

**Alternativa descartada:** Validación manual mediante condicionales `if/else` dentro del controlador.
**Decisión:** Clases DTO especializadas (`SedeCrear`, `SedeReemplazo`, `SedeActualizar`, etc.) decoradas con `System.ComponentModel.DataAnnotations`.
**Por qué:** Implementa fielmente la semántica REST: POST y PUT exigen integridad total del contrato, mientras que PATCH gestiona actualizaciones parciales. El framework intercepta y retorna un error estándar **422 Unprocessable Entity** con el listado de fallos antes de ejecutar código de negocio.
