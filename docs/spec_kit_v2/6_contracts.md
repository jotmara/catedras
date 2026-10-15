# Contratos de Integración y API — Versión 2

> **Versión 2 / Segunda Entrega** · Especificación de contratos HTTP, respuestas de error estandarizadas y llamadas a Procedimientos Almacenados (`sp_...`).
> Base URL Backend: `http://localhost:7045/api` · Swagger UI: `http://localhost:7045/swagger`.

---

## 1. Convenciones REST y Manejo de Errores PostgreSQL

El middleware `FiltroExcepcionPostgres` captura los códigos de error SQLSTATE de PostgreSQL y los traduce a respuestas HTTP legibles:

| Código SQLSTATE | Significado en PostgreSQL | Código HTTP | Mensaje Estandarizado de la API |
| :--- | :--- | :---: | :--- |
| `23503` | `foreign_key_violation` | **422 Unprocessable** | `"Violación de clave foránea: El registro padre referenciado no existe o no está disponible."` |
| `23505` | `unique_violation` | **409 Conflict** | `"Conflicto de unicidad: Ya existe un registro con el mismo identificador o clave de negocio."` |
| `23P01` | `exclusion_violation` | **409 Conflict** | `"Conflicto de exclusión: Se solapa temporalmente con una ventana de enlace existente."` |
| `23514` | `check_violation` | **400 Bad Request** | `"Violación de regla de chequeo: Uno de los valores no cumple con el dominio permitido."` |

---

## 2. Contratos HTTP para Cátedras y Sesiones (Maestro-Detalle)

### 2.1 Cátedras (Maestro)

#### `GET /api/catedra`
Retorna el listado de cátedras con soporte de paginación.
- **Respuesta 200 OK:**
  ```json
  [
    {
      "idCatedra": 1,
      "idEventoAsis": "000035392",
      "nombre": "Cátedra Abierta de Innovación Tecnológica y Sociedad",
      "nombreAsis": "Cátedra Abierta de Innovació",
      "fkTipoEvento": "CAAB",
      "fkDependencia": "DEP-ING",
      "activo": true,
      "creadoEn": "2026-10-14T20:30:00Z"
    }
  ]
  ```

#### `POST /api/catedra`
Crea una nueva cátedra oficial. **Nota:** `nombreAsis` no se envía en el cuerpo; el motor de base de datos lo genera en la inserción.
- **Cuerpo de Petición:**
  ```json
  {
    "idEventoAsis": "000035400",
    "nombre": "Cátedra de Ética, Ciudadanía y Transformación Digital",
    "fkTipoEvento": "CAAB",
    "fkDependencia": "DEP-HUM",
    "activo": true
  }
  ```
- **Respuesta 201 Created:**
  ```json
  {
    "idCatedra": 25,
    "idEventoAsis": "000035400",
    "nombre": "Cátedra de Ética, Ciudadanía y Transformación Digital",
    "nombreAsis": "Cátedra de Ética, Ciudadanía",
    "mensaje": "Cátedra registrada exitosamente."
  }
  ```

---

### 2.2 Sesiones (Detalle) con Disparador Demostrable

#### `POST /api/sesion`
Crea una sesión dentro de una cátedra.
- **Caso A (Demostración de Trigger):** El cliente NO envía `numeroReunion` (o envía `0` o `null`). El disparador `trg_sesion_consecutivo` asigna el número consecutivo correspondiente dentro de la cátedra.
- **Cuerpo de Petición:**
  ```json
  {
    "fkCatedra": 1,
    "titulo": "Sesión Inaugural: Retos de la Inteligencia Artificial",
    "inicio": "2026-11-04T10:00:00Z",
    "fin": "2026-11-04T12:00:00Z",
    "fkModalidad": "PRESENCIAL",
    "fkSede": "SAN_BENITO",
    "fkPeriodo": "2026-2",
    "lugar": "Auditorio San Buenaventura",
    "cupo": 150
  }
  ```
- **Respuesta 201 Created:**
  ```json
  {
    "idSesion": 102,
    "fkCatedra": 1,
    "numeroReunion": 1,
    "titulo": "Sesión Inaugural: Retos de la Inteligencia Artificial",
    "estado": "PROGRAMADA",
    "mensaje": "Sesión programada exitosamente. Consecutivo #1 asignado por disparador."
  }
  ```

---

## 3. Contratos de Procedimientos Almacenados de Flujo (`CALL sp_...`)

### 3.1 Emisión de Enlace y Código QR
- **Invocación:** `CALL catedras.sp_emitir_enlace(p_id_sesion, p_min_antes, p_min_despues, p_usuario, p_id_enlace);`
- **Efecto:** Genera el token UUID no adivinable, la URL pública y el registro de la ventana horaria `tstzrange`.

### 3.2 Solicitud de Clave de Acceso (OTP Antisuplantación)
- **Invocación:** `CALL catedras.sp_solicitar_clave(p_identificador, p_token, p_ip, p_id_clave, p_clave, p_enviado_a);`
- **Efecto:** Resuelve el asistente mediante `fn_resolver_asistente`, genera el código OTP de 6 dígitos, almacena el hash con sal `digest(clave || correo, 'sha256')` y retorna la clave en claro únicamente para el envío por correo electrónico.

### 3.3 Exportación Oficial PeopleSoft ASIS
- **Función:** `SELECT * FROM catedras.fn_exportar_asis(p_id_sesion);`
- **Contrato de Salida:** Exactamente tres columnas (`reunion`, `id_asis`, `programa`), ordenadas por código ASIS, sin filas de usuarios externos.
