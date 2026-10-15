# Especificación — Sistema Cátedras Abiertas USBMed (37 Tablas)

> **Especificación Funcional y Técnica** del sistema completo de registro y control de asistencia a cátedras abiertas para la Universidad de San Buenaventura, Medellín.
> Rige la constitución permanente del proyecto: [1_constitution.md](1_constitution.md).
>
> | Documento | Contenido |
> |---|---|
> | **2_spec.md** (este) | QUÉ construir en el ecosistema de 37 tablas, arquitectura y criterios de aceptación |
> | [3_plan.md](3_plan.md) | CÓMO: arquitectura en 4 capas, tipado C# .NET 10, Dapper y SQL parametrizado |
> | [4_research.md](4_research.md) | Decisiones técnicas, justificación de las 37 tablas y alternativas descartadas |
> | [5_data_model.md](5_data_model.md) | Diccionario de datos, clasificación de las 37 tablas (10 sin FK + 27 con FK) |
> | [6_contracts.md](6_contracts.md) | Contratos HTTP completos para las 37 tablas, 6 vistas y procesos de negocio |
> | [7_quickstart.md](7_quickstart.md) | Guía de arranque con Docker, verificación SQL y smoke test global |
> | [8_tasks.md](8_tasks.md) | Plan de tareas por fases ordenadas para el desarrollo integral del sistema |

---

## 1. Propósito del Sistema

Construir una **Web API REST tipada y de alto rendimiento en C# / ASP.NET Core** que gobierne el ecosistema completo de **Cátedras Abiertas de la USBMed**, reemplazando los formularios anónimos y la manipulación manual de hojas de cálculo por una plataforma automatizada con:
1. **Identidad validada:** Validación estricta contra el maestro de personas del sistema ASIS (PeopleSoft) mediante código, documento o correo institucional/personal.
2. **Control de Acceso Seguro (OTP):** Emisión de claves temporales de un solo uso enviadas por correo para evitar la suplantación de identidad entre asistentes.
3. **Control de Apertura y Canales:** Apertura de sesiones presenciales vía código QR proyectado y sesiones virtuales mediante enlace, delimitadas por ventanas de tiempo estrictas (`tstzrange`).
4. **Encuestas de Calidad Parametrizables:** Captura de satisfacción inmediata tras el registro de asistencia.
5. **Generación Automática del Archivo Plano:** Exportación directa del archivo inmutable de exactamente 3 columnas (`Reunión, ID_ASIS, Código_Programa`) requerido por la Dirección de Registro Académico.

---

## 2. Alcance por Módulos y Familias de Tablas (37 Tablas)

El sistema opera sobre las **37 tablas** del esquema `catedras`, agrupadas en 7 módulos interconectados:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        ARQUITECTURA DE DOMINIOS — CÁTEDRAS ABIERTAS                    │
├────────────────────────────────┬───────────────────────────────────────────────────────┤
│ Módulo 1: Catálogos Raíz       │ sede, modalidad, tipo_documento, tipo_vinculacion,    │
│ (10 Tablas independientes)     │ tipo_evento, tipo_pregunta, estado_proceso, rol,      │
│                                │ periodo_academico, encuesta                           │
├────────────────────────────────┼───────────────────────────────────────────────────────┤
│ Módulo 2: Estructura Académica │ facultad, dependencia, programa_academico,            │
│ (5 Tablas)                     │ alias_programa (sinonimia con pg_trgm)                │
├────────────────────────────────┼───────────────────────────────────────────────────────┤
│ Módulo 3: Identidad y Personas │ asistente, documento_asistente, vinculacion_asistente,│
│ (5 Tablas)                     │ programa_asistente, consentimiento_datos (Ley 1581)   │
├────────────────────────────────┼───────────────────────────────────────────────────────┤
│ Módulo 4: Cátedras y Sesiones  │ catedra (ID evento ASIS de 9 dígitos), sesion,        │
│ (3 Tablas)                     │ ponencia (asignación de ponentes por sesión)          │
├────────────────────────────────┼───────────────────────────────────────────────────────┤
│ Módulo 5: Acceso y Asistencia  │ enlace_registro (QR/Token), clave_acceso (OTP hash),  │
│ (3 Tablas — Núcleo)            │ registro_asistencia (snapshots de programa y vínculo) │
├────────────────────────────────┼───────────────────────────────────────────────────────┤
│ Módulo 6: Encuesta de Calidad  │ pregunta, opcion_pregunta, respuesta_encuesta,        │
│ (4 Tablas)                     │ respuesta_item (validación CHECK condicional)         │
├────────────────────────────────┼───────────────────────────────────────────────────────┤
│ Módulo 7: Integración y ASIS   │ lote_carga_asistente, novedad_carga, lote_migracion,  │
│ (7 Tablas)                     │ detalle_migracion, usuario, rol_por_usuario, parametro│
└────────────────────────────────┴───────────────────────────────────────────────────────┘
```

---

## 3. Requisitos Funcionales del Sistema

> **Nota de Alcance por Entregas:** La **Primera Entrega** comprende la implementación exclusiva de las **10 tablas sin claves foráneas (tablas independientes / catálogos maestros)**: `sede`, `modalidad`, `tipo_documento`, `tipo_vinculacion`, `tipo_evento`, `tipo_pregunta`, `estado_proceso`, `rol`, `periodo_academico`, `encuesta`. Las 27 tablas restantes que poseen **claves foráneas (FKs)** pertenecen a las entregas subsecuentes (Entregas 2 y 3).

### RF1 — Gestión de Catálogos y Entidades Maestras (Tablas Independientes / Primera Entrega)
- CRUD tipado para las 10 tablas independientes: `sede`, `modalidad`, `tipo_documento`, `tipo_vinculacion`, `tipo_evento`, `tipo_pregunta`, `estado_proceso`, `rol`, `periodo_academico`, `encuesta`.
- Validación estricta con DataAnnotations: códigos únicos en mayúsculas, nombres no vacíos y flags booleanos.

### RF2 — Estructura Organizacional y Jerarquía Académica
- Soporte de facultades y dependencias recursivas (`fk_facultad_padre`, `fk_dependencia_padre`) para reportes consolidados y matriciales.
- Catálogo oficial de 105 programas académicos con código natural de 5 caracteres (`M0221`, `MCCP`).
- Resolución inteligente de texto libre hacia código de programa (`alias_programa` con similitud trigramática `pg_trgm`).

### RF3 — Maestro de Asistentes y Prevención de Suplantación
- Resolución unificada de identidad: el asistente se autentica digitando indistintamente su **código estudiantil**, su **número de documento** o su **correo electrónico** (`fn_resolver_asistente`).
- Manejo de multivinculación histórica (ej. estudiante que a la vez es docente o egresado) y soporte de casos especiales como "Rutas de Paz" (vinculaciones que no exigen programa académico).
- Registro de consentimiento informado de tratamiento de datos personales conforme a la Ley Estatutaria 1581 de 2012.

### RF4 — Planificación de Cátedras, Sesiones y Ponentes
- Creación de cátedras con código de evento ASIS de 9 dígitos numéricos rellenados con ceros a la izquierda (`char(9)`), derivando automáticamente el nombre corto a 30 caracteres.
- Programación de sesiones individuales con cálculo automático del número consecutivo de reunión (`fn_siguiente_reunion`) garantizando la restricción `UNIQUE (fk_catedra, numero_reunion)`.
- Asignación de ponentes y expositores a sesiones específicas mediante la tabla `ponencia` con roles diferenciados.

### RF5 — Flujo Dinámico de Registro de Asistencia (QR y OTP)
- Generación de enlaces y códigos QR asociados a tokens criptográficos seguros (`enlace_registro`), restringidos por una ventana horaria estricta (`ventana tstzrange`).
- Emisión de código OTP seguro al correo (`clave_acceso`), almacenado en hash (`bytea`/SHA-256), con expiración parametrizable y límite de intentos fallidos.
- Creación del registro de asistencia capturando la instantánea fija (*snapshot*) del programa y vínculo activo del asistente en la fecha exacta del evento, garantizando imputación fidedigna.

### RF6 — Encuestas de Calidad Integradas
- Administración de cuestionarios con preguntas obligatorias u opcionales, tipos de respuesta variados (escalas 1-5, selección con opciones predefinidas, campos abiertos).
- Registro de respuestas vinculado biyectivamente al comprobante de asistencia (`UNIQUE (fk_registro)`).

### RF7 — Integración y Migración hacia PeopleSoft / ASIS
- Ingesta masiva de personas desde archivos externos con bitácora detallada de filas aceptadas y novedades/rechazos (`lote_carga_asistente`, `novedad_carga`).
- Generación auditada de lotes de migración con el archivo plano exacto de 3 columnas (`Reunion, ID, Programa`).
- Almacenamiento histórico de cada fila enviada en `detalle_migracion` con respuesta del monitor de procesos.

---

## 4. Requisitos No Funcionales

- **RNF1 — Arquitectura Limpia en 4 Capas:** Desacoplamiento total: `Controllers` → `Servicios` → `Repositorios` → `PostgreSQL`. Interfaces de C# para cada componente.
- **RNF2 — Cero ORM Pesado:** Todo el acceso a datos se realiza con **Dapper** y **Npgsql**, con sentencias SQL visibles y parametrizadas al 100% (`@parametro`), previniendo ataques de inyección SQL.
- **RNF3 — Integridad Referencial Nativa:** El motor PostgreSQL gestiona 52 claves foráneas, restricciones de exclusión GiST y disparadores de auditoría.
- **RNF4 — Operaciones Asíncronas de Extremo a Extremo:** Uso riguroso de `Task`, `async` y `await` en todo el flujo I/O.
- **RNF5 — Respuestas de Error Estandarizadas:** Formato uniforme `{estado, mensaje, detalle}`. Validación de peticiones con código **422 Unprocessable Entity** detallando la lista de atributos inválidos.

---

## 5. Criterios de Aceptación Globales

1. **Infraestructura Completa Levantada:** `docker compose up -d` despliega PostgreSQL con la base `catedras` conteniendo las **37 tablas base** y **6 vistas** bajo el esquema `catedras`.
2. **Endpoints Tipados Operativos:** La API compila sin errores y expone los contratos REST para todas las tablas maestras y dependientes, accesible en `http://localhost:7045/swagger`.
3. **Validación de Integridad Referencial:** Intentos de borrado sobre entidades referenciadas (por ejemplo, una sede o una cátedra con sesiones activas) son rechazados por PostgreSQL retornando error 500 con el detalle de violación de FK.
4. **Validación de Frontera (422):** Toda petición con atributos faltantes o longitudes no válidas es interceptada retornando código HTTP 422 con arreglo de errores.
5. **Pruebas de Capas Desacopladas:** La suite de pruebas de capas ejecuta contra mocks en memoria sin requerir conexión a base de datos externa.


---

## 9. Requerimientos Oficiales CIDEH (Integración ASIS/Oracle y Geolocalización)

Con base en el Plan de Desarrollo formal del **Centro de Investigación y Desarrollo de Estudios Humanísticos (CIDEH)**, se integran los siguientes requerimientos mandatorios:

### 9.1 Control de Presencia y Geolocalización
- **RF-CIDEH-01 (Geolocalización Confiable):** El formulario de registro captura obligatoriamente las coordenadas (latitud, longitud, precision_gps) del dispositivo del asistente para validar que se encuentre en las inmediaciones físicas de la sede o campus donde se imparte la cátedra.
- En caso de no disponibilidad de GPS (bloqueo por navegador), el sistema registra la dirección IP y el User-Agent para fines de auditoría.

### 9.2 Emisión Dinámica de QR y Enlace
- **RF-CIDEH-02 (Proyección en Sala):** Los administradores pueden emitir códigos QR dinámicos (/api/enlace/emitir y /api/enlace/{id}/qr) asociados a una sesión con una ventana temporal de validez estricta (ej. 60 min antes y 120 min después).
- El enlace dirige al asistente al formulario adaptativo de registro.

### 9.3 Formulario Adaptativo de Registro
- **RF-CIDEH-03 (Bifurcación Estudiante / Externo):**
  - **Estudiante USB:** Ingresa su código estudiantil o documento de identidad registrado en el maestro ASIS (14.808 registros) para certificación automática.
  - **Participante Externo / Visitante:** Completa el cuestionario de caracterización (tipo de documento, número, nombres, apellidos, correo institucional/personal y entidad de procedencia).
  - Ambos perfiles deben aceptar explícitamente la cláusula de tratamiento de datos personales (Habeas Data - Ley 1581 de 2012).

### 9.4 Optimización de Exportación a ASIS / Oracle
- **RF-CIDEH-04 (Archivo CSV Delimitado):** Generación de archivo plano CSV con estructura exacta de 3 columnas (Reunión, ID_ASIS, Programa) sin encabezados, preservando formato alfanumérico estricto y eliminando errores de importación en Oracle.
- **RF-CIDEH-05 (Depósito en Carpeta Compartida / SFTP):** Endpoint automatizado (POST /api/migracion/sesion/{id}/transferir-carpeta) para depositar el archivo directamente en la carpeta de intercambio del servidor ASIS sin necesidad de manipulación manual.
