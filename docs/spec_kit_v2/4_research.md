# Investigación y Decisiones Técnicas — Versión 2

> **Versión 2 / Segunda Entrega** · Justificación conceptual y arquitectónica de las decisiones técnicas adoptadas en las entidades dependientes, relaciones Maestro-Detalle y rutinas de base de datos.
> Referencia complementaria: [2_spec.md](2_spec.md), [3_plan.md](3_plan.md) y [5_data_model.md](5_data_model.md).

---

## 1. El Test de las Tres Preguntas para Identificar Maestro-Detalle

Para catalogar rigurosamente cada relación 1:N del sistema como **Maestro-Detalle**, se aplicó el test metodológico de tres preguntas:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        TEST METODOLÓGICO DE TRES PREGUNTAS                            │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. ¿Tiene la entidad hija una clave primaria independiente?                            │
│ 2. ¿Puede existir la fila hija de manera lógica sin un padre asignado?                 │
│ 3. ¿Qué debe ocurrir con las filas hijas si la fila padre es eliminada?                │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Aplicación sobre los Casos Clave del Sistema:

#### Caso 1: `catedra` (Maestro) ──▶ `sesion` (Detalle)
1. *¿Tiene PK propia?* Sí, `id_sesion` (identificador sintético para navegación eficiente). Sin embargo, su identidad de negocio real es compuesta: `(fk_catedra, numero_reunion)`.
2. *¿Puede existir sin padre?* **No.** Una "Reunión #2" no tiene significado semántico alguno si no pertenece a una Cátedra específica.
3. *¿Qué ocurre si se elimina el padre?* La base de datos aplica `ON DELETE RESTRICT` para impedir la pérdida accidental de historial académico. Una cátedra no puede destruirse si tiene reuniones y registros históricos.
- **Veredicto:** **Relación Maestro-Detalle pura.**

#### Caso 2: `sesion` ──▶ `ponencia` ──▶ `asistente`
1. *¿Tiene PK propia `ponencia`?* **No.** Su PK es compuesta: `(fk_sesion, fk_asistente, rol)`.
2. *¿Puede existir sin padre?* No, la participación como ponente sólo existe en el marco de la reunión. Pero el conferencista (`asistente`) es una entidad independiente que preexiste.
3. *¿Qué ocurre en la interfaz de usuario?* El usuario no edita los datos personales del ponente desde esta relación; simplemente **asocia** o **desasocia** al asistente existente con un rol específico.
- **Veredicto:** **Tabla Puente (N:M con atributos)**, NO un detalle puro.

#### Caso 3: `encuesta` ──▶ `pregunta` ──▶ `opcion_pregunta`
1. *¿Tienen PK propia?* Sí (`id_pregunta`, `id_opcion`), pero su existencia está estrictamente acoplada a la encuesta.
2. *¿Pueden existir sin padre?* **No.** Una opción "Totalmente de acuerdo" o una pregunta "Evalúe la claridad del expositor" carece de validez sin el cuestionario formal que la alberga.
3. *¿Qué ocurre al eliminar la encuesta?* Se aplica `ON DELETE CASCADE`: si se retira un cuestionario borrador, se destruyen todas sus preguntas y opciones en cascada.
- **Veredicto:** **Cadena Jerárquica Maestro-Detalle de Tres Niveles.**

---

## 2. Decisiones Técnicas Fundamentales (D1 a D5)

### D1 — Asignación de Consecutivo: Trigger en PostgreSQL vs. Código en Backend
- **Alternativa descartada:** Consultar `SELECT MAX(numero_reunion) + 1` desde el controlador de C# o la vista de Python antes de ejecutar el `INSERT`.
- **Decisión:** Disparador `trg_sesion_consecutivo` ejecutado en fase `BEFORE INSERT` con bloqueo pesimista `PERFORM 1 FROM catedra WHERE id_catedra = NEW.fk_catedra FOR UPDATE`.
- **Por qué:** Si dos usuarios crean sesiones concurrentes para la misma cátedra al mismo milisegundo, la consulta desde la API generaría una condición de carrera (*race condition*), asignando el mismo número a ambas y violando la restricción única `uq_sesion_reunion`. El trigger con bloqueo a nivel de cátedra serializa la transacción de forma infalible directamente en el motor.

### D2 — Truncamiento de `nombre_asis` mediante Columna Generada Almacenada
- **Alternativa descartada:** Obligar a la API o al usuario en el formulario a ingresar un nombre secundario recortado a 30 caracteres.
- **Decisión:** Uso de `GENERATED ALWAYS AS (left(nombre, 30)) STORED` en la tabla `catedra`.
- **Por qué:** PeopleSoft ASIS solo acepta nombres de 30 caracteres en su archivo plano. Truncar en la aplicación provocaría inconsistencias si se insertan cátedras mediante scripts SQL, cargas masivas o endpoints futuros. La columna generada garantiza conformidad inmutable con cero líneas de código en backend.

### D3 — Búsqueda y Normalización Difusa mediante Extensión `pg_trgm`
- **Alternativa descartada:** Comparación estricta con `LIKE '%texto%'` o búsquedas sensibles a mayúsculas/tildes.
- **Decisión:** Uso del operador `%` de similitud trigramática de PostgreSQL (`pg_trgm`) indexado con GiST sobre `alias_programa`.
- **Por qué:** En el formulario público, los estudiantes digitan libremente *"Ingeniería de Sistemas"*, *"Sistemas"*, *"Ing. Software"* o *"Derecho Diurno"*. La función `fn_resolver_programa(texto, 0.45)` empareja automáticamente el texto libre contra el código formal de 5 caracteres requerido por ASIS.

### D4 — Ventanas de Enlace con Rangos `tstzrange` y Restricción `EXCLUDE`
- **Alternativa descartada:** Dos columnas independientes `fecha_inicio` y `fecha_fin` validadas por código en backend.
- **Decisión:** Columna de rango nativo `ventana tstzrange` combinada con `EXCLUDE USING gist (fk_sesion WITH =, ventana WITH &&) WHERE (revocado_en IS NULL)`.
- **Por qué:** Impide matemáticamente que se generen dos códigos QR activos simultáneos para la misma sesión que confundan a los asistentes o permitan registros en horarios cruzados.

### D5 — Operaciones Transaccionales mediante Procedimientos (`CALL sp_...`)
- **Alternativa descartada:** Sentencias `INSERT / UPDATE` distribuidas en el código de la aplicación.
- **Decisión:** Procedimientos almacenados PL/pgSQL (`sp_solicitar_clave`, `sp_validar_clave_y_registrar`, `sp_cerrar_encuesta`, `sp_generar_lote_migracion`).
- **Por qué:** Centraliza la lógica transaccional sensible, evita ataques de inyección SQL, reduce la latencia de red al ejecutar múltiples pasos en un solo viaje y garantiza que las reglas de negocio (como el hashing de la OTP y la verificación de preguntas obligatorias) se apliquen de forma inviolable.
