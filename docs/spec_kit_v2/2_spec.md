# Especificación — Versión 2: Relaciones Maestro-Detalle y Entidades Dependientes

> **Versión 2 / Segunda Entrega** · Especificación funcional y técnica exhaustiva del dominio de Cátedras Abiertas USBMed según la metodología oficial del curso (Prof. Carlos Castro).
> Documento complementario de gobernanza: [1_constitution.md](1_constitution.md).

---

## 1. Propósito y Alcance de la Versión 2

En la **Versión 1**, el alcance abarcó exclusivamente las tablas maestras independientes de catálogo (sin claves foráneas salientes obligatorias).
La **Versión 2** tiene como propósito gobernar las entidades relacionales que conforman el núcleo operativo del sistema: las relaciones **Maestro-Detalle (1:N)**, las **cadenas de tres niveles**, las **tablas puente (N:M)** y la ejecución controlada de operaciones transaccionales mediante **Procedimientos Almacenados (`CALL sp_...`)** y **Disparadores (Triggers)**.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           ALCANCE DE DOMINIO VERSIÓN 2 (CÁTEDRAS ABIERTAS USBMED)              │
├───────────────────────────────┬─────────────────────────────────────────────────────────────────┤
│ Módulo A: Estructura          │ facultad, dependencia, programa_academico,                      │
│ Académica Institucional       │ alias_programa (sinonimia trigramática con pg_trgm)             │
├───────────────────────────────┼─────────────────────────────────────────────────────────────────┤
│ Módulo B: Identidad y         │ asistente (padrón central), documento_asistente (multivaluado), │
│ Personas (Padrón Maestro)     │ vinculacion_asistente, programa_asistente,                      │
│                               │ consentimiento_datos (Habeas Data Ley 1581 de 2012)             │
├───────────────────────────────┼─────────────────────────────────────────────────────────────────┤
│ Módulo C: Cátedras,           │ catedra (código ASIS 9 dígitos, columna generada nombre_asis),  │
│ Sesiones y Ponencias          │ sesion (entidad débil de cátedra con consecutivo por trigger),  │
│                               │ ponencia (tabla puente N:M con rol)                             │
├───────────────────────────────┼─────────────────────────────────────────────────────────────────┤
│ Módulo D: Acceso,             │ enlace_registro (QR y URL con rango tstzrange no solapado),     │
│ Asistencia y Encuestas        │ clave_acceso (OTP antisuplantación), registro_asistencia (1:N)  │
│                               │ encuesta ──▶ pregunta ──▶ opcion_pregunta (cadena 3 niveles)    │
│                               │ registro_asistencia ──▶ respuesta_encuesta ──▶ respuesta_item   │
└───────────────────────────────┴─────────────────────────────────────────────────────────────────┘
```

---

## 2. Las 10 Relaciones Maestro-Detalle Oficiales del Dominio

De acuerdo con las reglas de modelado relacional del curso, una relación es formalmente **Maestro-Detalle (1:N)** cuando la entidad detalle depende conceptualmente de la existencia de la entidad maestra, hereda su contexto y no tiene razón de existir de forma huérfana en el sistema:

| # | Maestro (1) | Detalle (N) | Clave Foránea (`FK`) | Cascada en Borrado (`ON DELETE`) | Justificación de Dominio |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | `catedras.catedra` | `catedras.sesion` | `fk_catedra` | `RESTRICT` | **Núcleo del sistema.** Una reunión de cátedra es una entidad débil del evento académico matriz. |
| **2** | `catedras.sesion` | `catedras.enlace_registro` | `fk_sesion` | `CASCADE` | Los enlaces y códigos QR generados pertenecen a una única sesión y su ventana de tiempo. |
| **3** | `catedras.sesion` | `catedras.registro_asistencia` | `fk_sesion` | `RESTRICT` | La lista de asistencia firmada por los participantes corresponde a esa sesión específica. |
| **4** | `catedras.asistente` | `catedras.documento_asistente` | `fk_asistente` | `CASCADE` | Atributo multivaluado: un asistente puede tener cédula, pasaporte o TI registrados históricamente. |
| **5** | `catedras.asistente` | `catedras.consentimiento_datos` | `fk_asistente` | `RESTRICT` | Trazabilidad legal obligatoria de Habeas Data (Ley 1581) de cada persona en el padrón. |
| **6** | `catedras.encuesta` | `catedras.pregunta` | `fk_encuesta` | `CASCADE` | Cuestionario de evaluación docente/evento compuesto por un conjunto ordenado de preguntas. |
| **7** | `catedras.pregunta` | `catedras.opcion_pregunta` | `fk_pregunta` | `CASCADE` | Si la pregunta es de selección múltiple, sus opciones de respuesta dependen exclusivamente de ella. |
| **8** | `catedras.registro_asistencia` | `catedras.respuesta_encuesta` | `fk_registro` | `CASCADE` | La evaluación completada por el asistente al finalizar su registro en la sesión. |
| **9** | `catedras.respuesta_encuesta` | `catedras.respuesta_item` | `fk_respuesta` | `CASCADE` | Desglose atómico de respuestas (numérica, texto u opción) por cada pregunta del formulario. |
| **10** | `catedras.programa_academico` | `catedras.alias_programa` | `fk_programa` | `CASCADE` | Variantes ortográficas e informales de digitación asociadas a un programa académico formal. |

---

## 3. Las 2 Cadenas Jerárquicas de Tres Niveles

El dominio contiene **dos cadenas jerárquicas estrictas de 3 niveles** (Maestro ──▶ Detalle N1 ──▶ Detalle N2):

### Cadena 1: Jerarquía de Evaluación y Cuestionarios
```
[encuesta] (Nivel 1: Cuestionario versionado)
   │
   └──▶ [pregunta] (Nivel 2: Enunciado, tipo y orden)
           │
           └──▶ [opcion_pregunta] (Nivel 3: Opciones elegibles de respuesta)
```
- **Regla:** Al borrar o clonar una versión de la encuesta, sus preguntas y las opciones de cada pregunta conservan integridad estructural en cascada.

### Cadena 2: Jerarquía de Asistencia y Captura de Respuestas
```
[registro_asistencia] (Nivel 1: Asistencia confirmada a la sesión)
   │
   └──▶ [respuesta_encuesta] (Nivel 2: Encabezado de la evaluación diligenciada)
           │
           └──▶ [respuesta_item] (Nivel 3: Respuestas individuales por ítem)
```
- **Regla:** Ningún ítem de respuesta (`respuesta_item`) puede existir sin su respectiva encuesta diligenciada, la cual a su vez depende de la asistencia efectiva del usuario.

---

## 4. Distinción Rigurosa: Entidades que NO son Detalle

Durante la sustentación oral, se debe defender con precisión por qué ciertas relaciones **no** son Maestro-Detalle:

### A. La entidad `ponencia` es una Tabla Puente (N:M), NO un detalle puro
- **Estructura:** Su clave primaria es compuesta `(fk_sesion, fk_asistente, rol)`.
- **Justificación:** Conecta dos entidades independientes preexistentes (`sesion` y `asistente`). Un conferencista existe en `asistente` antes de la sesión y continuará existiendo después. En la interfaz gráfica, un ponente **se vincula o desvincula** de la sesión; no se crea ni se destruye como una fila dependiente huérfana.

### B. La relación `sesion` ──▶ `encuesta` es una Referencia Opcional
- **Estructura:** Columna `fk_encuesta` en `sesion`, anulable (`NULL`).
- **Justificación:** Una encuesta se diseña globalmente y es compartida por múltiples sesiones de diferentes cátedras. La sesión solo la referencia; borrar una sesión jamás debe eliminar la encuesta institucional.

---

## 5. Requerimientos Funcionales Específicos de la Versión 2

### 5.1 Reglas del Negocio Inviolables (RN)
1. **RN-01 / RN-06 (Resolución Universal de Asistente):** El asistente puede ingresar mediante código ASIS, cédula o correo electrónico. La rutina `fn_resolver_asistente(texto)` unifica la búsqueda en el padrón maestro.
2. **RN-09 (Código de Evento ASIS):** El campo `id_evento_asis` en `catedra` debe ser exactamente de 9 caracteres numéricos con ceros a la izquierda (ej. `000035392`).
3. **RN-10 (Consecutivo de Reunión Automático):** En `sesion`, el disparador `trg_sesion_consecutivo` propone automáticamente el número consecutivo dentro de la cátedra mediante `coalesce(max(numero_reunion), 0) + 1` si el usuario no lo ingresa.
4. **RN-13 (Modalidad vs Canal):** Una sesión presencial difunde exclusivamente código QR; una virtual difunde URL pública.
5. **RN-27 / RN-28 (Archivo Plano de Tres Columnas):** La función `fn_exportar_asis(p_id_sesion)` exporta única y exactamente las tres columnas requeridas por PeopleSoft ASIS: `reunion`, `id_asis`, `programa`.
6. **RN-36 (No Solapamiento de Ventanas):** Restricción `EXCLUDE USING gist (fk_sesion WITH =, ventana WITH &&)` para garantizar que dos enlaces de la misma sesión no se solapen temporalmente.

---

## 6. Criterios de Aceptación (Rubro de Evaluación)

| ID | Escenario de Prueba | Comportamiento Esperado | Criterio de Evaluación |
| :--- | :--- | :--- | :--- |
| **CA-01** | Crear sesión sin indicar `numero_reunion` | El disparador en PostgreSQL autocalcula el consecutivo exacto (ej. 1, 2, 3...) sin intervención de la API. | **Demostración de Disparadores en Vivo.** |
| **CA-02** | Pantalla única Maestro-Detalle de Cátedra | Al seleccionar una cátedra del maestro, el panel de sesiones hijas se actualiza dinámicamente en la misma pantalla. | **Frontend Maestro-Detalle.** |
| **CA-03** | Selección de Claves Foráneas | En los formularios, los campos `fk_tipo_evento`, `fk_dependencia`, `fk_modalidad` y `fk_sede` son desplegables poblados desde la BD; **nunca se digita un ID manual**. | **Usabilidad y FKs.** |
| **CA-04** | Creación vía Stored Procedure | La creación y operaciones críticas ejecutan `CALL sp_...` garantizando consistencia atómica y aislamiento transaccional. | **Procedimientos Almacenados.** |
| **CA-05** | Integridad Referencial al Eliminar | Intentar eliminar una cátedra con sesiones asociadas arroja error controlado `409 Conflict / 500` por `RESTRICT`. | **Integridad Referencial.** |
