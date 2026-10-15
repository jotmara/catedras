# Contratos HTTP — API Cátedras USBMed (37 Tablas + Vistas + Procesos)

> **Contratos REST Oficiales** · Base URL: `http://localhost:7045`.
> Especificación exhaustiva de endpoints, cuerpos de petición, códigos de estado y respuestas JSON para todas las entidades y módulos del sistema.

---

## 0. Convenciones y Formatos Globales

### Envoltorios de Respuesta:
- **Consultas múltiples (GET colecciones):**
  ```json
  {
    "tabla": "nombre_tabla",
    "limite": 100,
    "total": 12,
    "datos": [ ... ]
  }
  ```
- **Operaciones de mutación exitosa (POST, PUT, PATCH, DELETE):**
  ```json
  {
    "estado": 200,
    "mensaje": "Operación ejecutada exitosamente.",
    "identificador": "VALOR_O_ID",
    "filasAfectadas": 1
  }
  ```
- **Estructura uniforme de error:**
  ```json
  {
    "estado": 422,
    "mensaje": "Error de validación en los datos enviados.",
    "errores": [
      "El campo 'nombre' es obligatorio.",
      "El código debe tener entre 1 y 10 caracteres."
    ],
    "detalle": "Validación fallida en capa de frontera (DataAnnotations)."
  }
  ```

| Código HTTP | Significado y Contexto de Uso |
|---|---|
| **200 OK** | Solicitud procesada correctamente con retorno de datos o confirmación. |
| **204 No Content** | Consulta válida sobre una tabla o filtro que no contiene registros. |
| **400 Bad Request** | Regla de negocio rota (límite negativo, cuerpo de actualización vacío). |
| **404 Not Found** | Recurso o identificador no localizado en la base de datos. |
| **422 Unprocessable Entity** | Fallo en validación de contrato de entrada (campos obligatorios omitidos). |
| **500 Internal Server Error** | Restricción de base de datos violada (clave foránea, duplicidad no controlada). |

---

## 1. Contratos del Módulo 1: Catálogos Independientes (10 Tablas)

Aplica el estándar CRUD para cada una de las 10 tablas raíz sin claves foráneas:
`sede`, `modalidad`, `tipo_documento`, `tipo_vinculacion`, `tipo_evento`, `tipo_pregunta`, `estado_proceso`, `rol`, `periodo_academico`, `encuesta`.

### 1.1 `GET /api/{catalogo}[?limite=N]`
- **Rutas soportadas:** `/api/sede`, `/api/modalidad`, `/api/tipo_documento`, `/api/tipo_vinculacion`, `/api/tipo_evento`, `/api/tipo_pregunta`, `/api/estado_proceso`, `/api/rol`, `/api/periodo_academico`, `/api/encuesta`.
- **Respuesta 200:** Envoltorio estándar con array de objetos.

### 1.2 `GET /api/{catalogo}/{id}`
- **Ejemplo Sede:** `GET /api/sede/SAN_BENITO`
  ```json
  {
    "id_sede": "SAN_BENITO",
    "nombre": "Campus San Benito",
    "direccion": "Carrera 56C 51-110, Medellín",
    "es_virtual": false,
    "activo": true
  }
  ```

### 1.3 `POST /api/{catalogo}`
- **Ejemplo Sede (Creación):**
  ```json
  // POST /api/sede
  {
    "id_sede": "POBLADO",
    "nombre": "Campus El Poblado",
    "direccion": "Calle 10 # 43A-25",
    "es_virtual": false
  }
  ```
- **Respuesta 200:** `{"estado": 200, "mensaje": "Sede creada exitosamente.", "identificador": "POBLADO"}`.
- **Respuesta 422:** Si falta `id_sede` o `nombre`.

### 1.4 `PUT /api/{catalogo}/{id}` (Reemplazo completo)
- Todos los campos obligatorios del modelo son requeridos. La omisión de uno responde 422.

### 1.5 `PATCH /api/{catalogo}/{id}` (Actualización parcial)
- Campos opcionales. Actualiza únicamente los atributos suministrados.

### 1.6 `DELETE /api/{catalogo}/{id}`
- Elimina el registro maestro. Si existen registros dependientes (ej. una sesión asociada a esa sede), PostgreSQL rechaza la eliminación con código 500 informando violación de clave foránea.

---

## 2. Contratos del Módulo 2: Estructura Académica (5 Tablas)

- **`facultad`** (`/api/facultad`): PK `id_facultad`, campos `nombre`, `fk_facultad_padre`.
- **`dependencia`** (`/api/dependencia`): PK `id_dependencia`, campos `nombre`, `fk_dependencia_padre`.
- **`programa_academico`** (`/api/programa_academico`): PK `codigo` (`char(5)` natural, ej. `M0221`), `nombre`, `fk_facultad`.
- **`alias_programa`** (`/api/alias_programa`): PK `id_alias`, `texto_variacion`, `fk_programa`. Permite resolver variaciones tipográficas hacia el código oficial.

---

## 3. Contratos del Módulo 3: Identidad y Personas (5 Tablas)

- **`asistente`** (`/api/asistente`): PK `id_asistente`, `id_asis` (código PeopleSoft único), `nombres`, `apellidos`, `correo_institucional`, `correo_personal`, `celular`, `es_externo`, `activo`.
- **`documento_asistente`** (`/api/documento_asistente`): PK `id_documento`, `fk_asistente`, `fk_tipo_documento`, `numero_documento`, `vigente`.
- **`vinculacion_asistente`** (`/api/vinculacion_asistente`): Clave compuesta `(fk_asistente, fk_tipo_vinculacion, fecha_ini)`.
- **`programa_asistente`** (`/api/programa_asistente`): Clave compuesta `(fk_asistente, fk_programa, fk_periodo)`.
- **`consentimiento_datos`** (`/api/consentimiento_datos`): PK `id_consentimiento`, `fk_asistente`, `version_politica`, `aceptado_en`, `ip_registro`.

---

## 4. Contratos del Módulo 4: Cátedras, Sesiones y Ponentes (3 Tablas)

### 4.1 Cátedra Marco (`/api/catedra`)
- **`POST /api/catedra`**
  ```json
  {
    "id_evento_asis": "000035392",
    "nombre": "Cátedra Abierta de Pedagogía Electoral y Ciudadana",
    "fk_tipo_evento": "CAAB",
    "fk_dependencia": 1,
    "descripcion": "Espacio formativo institucional"
  }
  ```
  *Nota técnica:* La base de datos deriva automáticamente `nombre_asis` truncado a 30 caracteres.

### 4.2 Sesión de Cátedra (`/api/sesion`)
- **`POST /api/sesion`**
  ```json
  {
    "fk_catedra": 1,
    "titulo": "Sesión Inaugural: Mecanismos de Participación",
    "fecha_inicio": "2026-09-10T14:00:00-05:00",
    "fecha_fin": "2026-09-10T16:00:00-05:00",
    "fk_modalidad": "PRESENCIAL",
    "fk_sede": "SAN_BENITO",
    "lugar_o_enlace": "Auditorio San Francisco",
    "cupo_maximo": 150,
    "fk_periodo": "2026-2",
    "fk_encuesta": 1
  }
  ```
  *El número de reunión consecutivo se autocalcula garantizando la restricción de negocio.*

### 4.3 Ponencia (`/api/ponencia`)
- Clave compuesta `(fk_sesion, fk_asistente, rol)` para vincular conferencistas y docentes invitados.

---

## 5. Contratos del Módulo 5: Acceso y Registro de Asistencia (Núcleo)

### 5.1 Generación de QR y Enlace (`POST /api/enlace_registro`)
```json
{
  "fk_sesion": 1,
  "canal": "QR",
  "ventana_inicio": "2026-09-10T13:45:00-05:00",
  "ventana_fin": "2026-09-10T14:30:00-05:00",
  "usos_maximos": 200
}
```
**Respuesta 200:** Retorna el `token` único (`Guid`), la URL pública y la ruta para renderizar el código QR.

### 5.2 Solicitud de Clave OTP (`POST /api/proceso/solicitar_clave`)
```json
{
  "token_enlace": "d3b07384-d113-4632-bf72-88682a20b080",
  "identificador": "30000141979" // Puede ser código, cédula o correo
}
```
**Respuesta 200:**
```json
{
  "estado": 200,
  "mensaje": "Clave temporal de acceso generada y enviada al correo del asistente.",
  "correo_enmascarado": "h***@usbmed.edu.co",
  "expira_en": "2026-09-10T14:15:00-05:00"
}
```

### 5.3 Validación de Clave y Confirmación de Asistencia (`POST /api/proceso/registrar_asistencia`)
```json
{
  "token_enlace": "d3b07384-d113-4632-bf72-88682a20b080",
  "identificador": "30000141979",
  "clave_otp": "748291"
}
```
**Respuesta 200:**
```json
{
  "estado": 200,
  "mensaje": "Asistencia registrada exitosamente.",
  "id_registro": 1045,
  "asistente": "Hugo Nelson Castañeda Ruiz",
  "programa_imputado": "M0221",
  "vinculacion_imputada": "DOCENTE",
  "requiere_encuesta": true
}
```

---

## 6. Contratos del Módulo 6: Encuesta de Calidad

- **`POST /api/proceso/responder_encuesta`**
  ```json
  {
    "id_registro": 1045,
    "respuestas": [
      { "id_pregunta": 1, "valor_numerico": 5 },
      { "id_pregunta": 2, "id_opcion": 3 },
      { "id_pregunta": 3, "valor_texto": "Excelente cátedra, temas muy claros." }
    ]
  }
  ```
- Cumple la regla de negocio: exactamente una encuesta por registro confirmado (`uq_respuesta_registro`).

---

## 7. Contratos del Módulo 7: Integración y Exportación a ASIS

### 7.1 Generar Lote de Migración (`POST /api/proceso/exportar_asis/{id_sesion}`)
Genera el lote auditado y produce el archivo plano de tres columnas exactas:
```json
{
  "estado": 200,
  "mensaje": "Lote de migración generado exitosamente.",
  "id_lote_migracion": 42,
  "nombre_archivo": "MIGRACION_CATEDRA_SESION_1.txt",
  "total_asistentes_migrables": 85,
  "externos_excluidos": 12,
  "url_descarga": "/api/migracion/archivo/42"
}
```

### 7.2 Formato Físico del Archivo Plano (PeopleSoft):
```text
1	30000141979	M0221
1	30000184721	M0286
1	30000095812	M0115
```

---

## 8. Contratos de Vistas de Reporte (Solo Lectura)

1. `GET /api/vista/asistencia_completa`: Información unificada de asistencia, estudiante, programa y evento.
2. `GET /api/vista/asistente_vigente`: Documento y vínculo oficial activo por cada persona.
3. `GET /api/vista/control_ventana`: Monitoreo en tiempo real de apertura y cierre de cátedras activas.
4. `GET /api/vista/embudo_registro`: Auditoría del embudo (enlaces emitidos → claves pedidas → asistencias confirmadas).
5. `GET /api/vista/evaluacion_sesion`: Consolidado de métricas de calidad y satisfacción por cátedra.
6. `GET /api/vista/pendiente_migracion`: Registros pendientes por ser exportados hacia ASIS.

---

## 7. Extensión de Contratos CIDEH (CSV y Transferencia a Carpeta)

### 7.1 Descarga de Archivo Plano CSV para ASIS
```http
GET /api/migracion/sesion/{idSesion}/csv
Authorization: Bearer {token_jwt}
```
**Respuesta (200 OK - text/csv):**
```csv
1,1000513,INGSO
1,1020304,DEREC
```

### 7.2 Depósito Automatizado en Carpeta Destino / SFTP
```http
POST /api/migracion/sesion/{idSesion}/transferir-carpeta?rutaDestino={ruta_opcional}
Authorization: Bearer {token_jwt}
```
**Respuesta (200 OK - application/json):**
```json
{
  "mensaje": "Archivo CSV transferido exitosamente a la carpeta compartida.",
  "ruta_archivo": "C:\\exportaciones_asis\\ME_CATEDRA_1.csv",
  "total_filas": 45
}
```
