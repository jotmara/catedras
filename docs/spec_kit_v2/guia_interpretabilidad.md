# Guía de Interpretabilidad del Código y Defensa Oral — Versión 2

> **Versión 2 / Segunda Entrega** · Respuestas fundamentadas a las cuatro preguntas críticas de la rúbrica oficial (Ponderación: 4.0 / 20 puntos - 20%).
> Para sustentar oralmente frente al docente la arquitectura, decisiones de diseño y tolerancia a fallos.

---

## 1. Archivo 1: `SOLUCION/fisico_postgres/10-triggers.sql` (`fn_trg_sesion_consecutivo`)

### 1. ¿Qué hace exactamente este código?
Gestiona la numeración secuencial de reuniones (`numero_reunion`) para cada cátedra en la tabla `catedras.sesion`. Cuando se inserta una nueva sesión y el cliente no proporciona el número de reunión (o envía `0` o `null`), el trigger consulta el valor máximo actual para esa cátedra específica y le suma 1 (`coalesce(max(numero_reunion), 0) + 1`).

### 2. ¿Por qué se tomó esta decisión de diseño?
- **Para eliminar condiciones de carrera (*Race Conditions*):** Si dos administradores crean una reunión simultáneamente para la misma cátedra, calcular el consecutivo en C# o Python requeriría un `SELECT` previo que, en concurrencia, devolvería el mismo número a ambos, provocando un error de llave duplicada (`uq_sesion_reunion`).
- **Bloqueo Pesimista:** El trigger ejecuta `PERFORM 1 FROM catedra WHERE id_catedra = NEW.fk_catedra FOR UPDATE`, serializando las inserciones a nivel de base de datos de forma infalible.

### 3. ¿Qué modos de fallo existen y cómo reacciona el sistema?
- **Fallo:** Si el ID de cátedra (`NEW.fk_catedra`) no existe, PostgreSQL aborta la transacción inmediatamente con error de clave foránea `23503` antes de intentar bloquear la fila.
- **Fallo de concurrencia:** Si una transacción retiene el bloqueo durante mucho tiempo, la segunda transacción esperará de forma transparente hasta que la primera complete el `COMMIT`.

### 4. ¿Qué cambiarías en una siguiente versión?
Para eventos con miles de reuniones masivas concurrentes, se podría utilizar una secuencia particionada por año o un generador de numeración con tablas de contadores (*advisory locks*), aunque para el volumen universitario actual (5.711 reuniones históricas), el bloqueo pesimista por cátedra es la solución óptima y más limpia.

---

## 2. Archivo 2: `ApiCatedrasUsbmed/Controllers/CatedraController.cs`

### 1. ¿Qué hace exactamente este código?
Expone los puntos de entrada HTTP REST (`GET`, `POST`, `PUT`, `DELETE`) para la entidad matriz `catedra`. Aplica validación sintáctica de los DTOs de entrada, coordina con la capa de persistencia mediante Dapper y formatea respuestas JSON estandarizadas.

### 2. ¿Por qué se tomó esta decisión de diseño?
- **Separación de Responsabilidades:** El controlador no contiene sentencias SQL crudas ni lógica de acceso a datos directa; delega a `IRepositorioCatedra`.
- **Exclusión de `nombre_asis`:** En el DTO `CatedraCrear`, no existe el campo `nombre_asis`. Esto garantiza que la regla de truncamiento de PeopleSoft ASIS (30 caracteres) la gobierne exclusivamente la columna generada de PostgreSQL, impidiendo que la API manipule o envíe datos redundantes.

### 3. ¿Qué modos de fallo existen y cómo reacciona el sistema?
- **Violación de Clave Foránea (`fk_dependencia` no existe):** El repositorio lanza `PostgresException` con código `23503`. El middleware `FiltroExcepcionPostgres` intercepta este error y devuelve un HTTP `422 Unprocessable Entity` con un mensaje amigable al cliente en lugar de un `500 Internal Server Error`.
- **Código de Evento ASIS Duplicado:** Si se intenta registrar un `id_evento_asis` repetido, el motor arroja `23505` (`unique_violation`) y el filtro lo traduce a HTTP `409 Conflict`.

### 4. ¿Qué cambiarías en una siguiente versión?
Implementar el patrón CQRS (Command Query Responsibility Segregation) con MediatR para desacoplar aún más los casos de uso complejos y agregar almacenamiento en caché distribuido (Redis) para las consultas de cátedras frecuentes.

---

## 3. Archivo 3: `ApiCatedrasUsbmed/Modelos/Sesion.cs`

### 1. ¿Qué hace exactamente este código?
Modela la entidad dependiente (detalle) de una reunión de cátedra en C#, definiendo sus tipos de datos, propiedades anulables y mapeo con la tabla `catedras.sesion`.

### 2. ¿Por qué se tomó esta decisión de diseño?
- **Propiedad `NumeroReunion` Anulable (`short?`):** Se definió como nullable para reflejar con fidelidad la regla de negocio: al crearse una sesión, el número de reunión no es obligatorio en el payload porque el disparador de base de datos se encarga de calcularlo.
- **Tipado Fuerte de Rangos:** Las fechas de inicio y fin se mapean a `DateTimeOffset` para preservar la zona horaria institucional de Colombia (`UTC-5`), evitando desincronizaciones entre el servidor web y la base de datos.

### 3. ¿Qué modos de fallo existen y cómo reacciona el sistema?
- **Desincronización de Tipos:** Si en base de datos `numero_reunion` es `smallint` y en C# se mapeara a `int` sin conversión en Dapper, podría generar advertencias de casting; al estar declarado como `short` (int16), el mapeo en memoria es directo y de alto rendimiento.

### 4. ¿Qué cambiarías en una siguiente versión?
Encapsular la entidad convirtiendo las propiedades públicas en campos inmutables con métodos de fábrica (*Rich Domain Model* en lugar de un modelo anémico), asegurando invariantes como `Fin > Inicio` directamente en el constructor de C#.

---

## 4. Archivo 4: `app.py` (Módulo Web Frontend Flask)

### 1. ¿Qué hace exactamente este código?
Gestiona la interfaz de usuario web institucional para estudiantes, docentes y administradores. Orquesta las vistas, renderiza plantillas HTML5 con el manual de marca corporativo de la USBMed y comunica con la API de base de datos.

### 2. ¿Por qué se tomó esta decisión de diseño?
- **Pantalla Única Maestro-Detalle:** En la ruta `/catedras`, se presentan las cátedras y, al seleccionar una fila, se listan sus sesiones en el mismo plano visual. Esto optimiza el flujo de trabajo del administrador académico al evitar cambios constantes de ventana.
- **Dropdowns Dinámicos:** Los formularios consumen los catálogos foráneos (`tipo_evento`, `dependencia`, `modalidad`, `sede`) para alimentar etiquetas `<select>`. El usuario nunca escribe a mano una clave foránea, garantizando usabilidad y reduciendo a cero los errores tipográficos.

### 3. ¿Qué modos de fallo existen y cómo reacciona el sistema?
- **Caída del Backend .NET o BD:** Si la API no responde, el bloque `try/except requests.RequestException` captura la excepción, registra la bitácora y muestra un mensaje de alerta flash estilizado en la interfaz (`"Aviso del sistema: Comunicación temporalmente no disponible"`), evitando pantallas blancas de caída.

### 4. ¿Qué cambiarías en una siguiente versión?
Migrar la capa de presentación a un framework SPA reactivo como React o Vue con Tailwind/Vanilla CSS, manteniendo la arquitectura desacoplada mediante llamadas AJAX asíncronas con Axios.
