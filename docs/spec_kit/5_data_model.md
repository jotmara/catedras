# Modelo de Datos - Estructura de Tablas por Entregas

> **Base de Datos:** dcatedras_postgres_local / Esquema catedras (37 Tablas en Total).

---

## 1. PRIMERA ENTREGA: Tablas Sin Claves Foraneas (Tablas Independientes / Maestras)

En la **Primera Entrega**, el alcance tecnico comprende exclusivamente las **10 tablas independientes (sin llaves foraneas salientes hacia otras tablas)**. Estas entidades constituyen la base de catalogos maestros y parametrizacion del sistema.

### Lista de las 10 Tablas de la Primera Entrega (Sin FKs):

1. **catedras.sede**: Sedes y campus de la Universidad (Codigo, nombre, direccion, telefono, activo).
2. **catedras.modalidad**: Modalidades de eventos (Presencial, Virtual, Hibrido).
3. **catedras.tipo_documento**: Tipos de documento de identidad (CC, TI, CE, Pasaporte, etc.).
4. **catedras.tipo_vinculacion**: Tipos de vinculacion universitaria (Estudiante, Docente, Egresado, Externo).
5. **catedras.tipo_evento**: Clasificacion de tipos de evento academico (Catedra Abierta, Conversatorio, Taller).
6. **catedras.tipo_pregunta**: Tipos de pregunta para encuestas (Abierta, Escala, Seleccion Unica, Seleccion Multiple).
7. **catedras.estado_proceso**: Catalogo de estados de proceso (Pendiente, En Proceso, Finalizado, Cancelado).
8. **catedras.rol**: Roles de usuario del sistema (Administrador, Ponente, Asistente, Auditor).
9. **catedras.periodo_academico**: Periodos academicos institucionales (ej. 2026-1, 2026-2).
10. **catedras.encuesta**: Cabecera maestra de cuestionarios y encuestas de calidad.

---

## 2. ENTREGAS POSTERIORES (Entregas 2 y 3): Tablas Con Claves Foraneas

Las siguientes 27 tablas contienen **llaves foraneas (FKs)** y relaciones complejas. **No corresponden a la Primera Entrega**, sino a las fases subsecuentes del proyecto.

### A. Estructura Academica e Identidad (Entrega 2):
- **catedras.facultad**: Facultades universitarias (FK a acultad padre).
- **catedras.dependencia**: Unidades y departamentos academicos (FK a acultad y dependencia padre).
- **catedras.programa_academico**: Programas academicos oficiales (FK a dependencia).
- **catedras.alias_programa**: Tabla de sinonimia trigramatica para programas (FK a programa_academico).
- **catedras.asistente**: Padron maestro de asistentes (FK a 	ipo_documento).
- **catedras.documento_asistente**: Documentos de identidad asociados al asistente (FK a sistente, 	ipo_documento).
- **catedras.vinculacion_asistente**: Vinculaciones activas e historicas del asistente (FK a sistente, 	ipo_vinculacion).
- **catedras.programa_asistente**: Programas academicos en los que esta matriculado el participante (FK a sistente, programa_academico, periodo_academico).
- **catedras.consentimiento_datos**: Registro de aceptacion de Habeas Data - Ley 1581 (FK a sistente).

### B. Catedras, Sesiones y Ponencias (Entrega 2 / 3):
- **catedras.catedra**: Catedras abiertas con codigo ASIS de 9 digitos (FK a 	ipo_evento, dependencia).
- **catedras.sesion**: Sesiones y reuniones programadas por catedra (FK a catedra, modalidad, sede, periodo_academico, estado_proceso).
- **catedras.ponencia**: Asignacion y autogestion autonoma de ponentes por sesion (FK a sesion, sistente).

### C. Control de Acceso, QR y Registro de Asistencia (Entrega 3):
- **catedras.enlace_registro**: Emision dinamica de tokens QR con ventanas de tiempo (FK a sesion, sede).
- **catedras.clave_acceso**: Claves OTP hashed enviadas al correo (FK a enlace_registro, sistente).
- **catedras.registro_asistencia**: Comprobantes de asistencia con snapshots de programa y geolocalizacion (FK a sesion, sistente, inculacion_asistente, programa_asistente, enlace_registro, clave_acceso).

### D. Encuestas de Calidad e Integracion ASIS / PeopleSoft (Entrega 3):
- **catedras.pregunta**: Preguntas asociadas a encuestas (FK a encuesta, 	ipo_pregunta).
- **catedras.opcion_pregunta**: Opciones de respuesta prestablecidas (FK a pregunta).
- **catedras.respuesta_encuesta**: Cabecera de respuesta a encuesta (FK a 
egistro_asistencia, encuesta).
- **catedras.respuesta_item**: Detalle de respuestas ingresadas por el asistente (FK a 
espuesta_encuesta, pregunta, opcion_pregunta).
- **catedras.lote_carga_asistente**: Lotes de carga masiva de personas (FK a usuario).
- **catedras.novedad_carga**: Novedades y rechazos en la carga masiva (FK a lote_carga_asistente).
- **catedras.lote_migracion**: Lotes de exportacion hacia Oracle / ASIS (FK a sesion, usuario, estado_proceso).
- **catedras.detalle_migracion**: Filas individuales enviadas al servidor ASIS (FK a lote_migracion, 
egistro_asistencia).
- **catedras.usuario**: Usuarios administrativos de la API (FK a sistente / persona).
- **catedras.rol_por_usuario**: Asignacion de roles a usuarios (FK a usuario, 
ol).
- **catedras.parametro**: Configuracion global y parametros de sistema (FK a usuario).
- **catedras.bitacora**: Logs de auditoria y trazabilidad (FK a usuario).

---

## 3. Resumen de la Estructuracion por Entregas

| Fase / Entrega | Tipo de Tablas | Cantidad | Descripcion / Alcance |
|:---|:---|:---:|:---|
| **Primera Entrega** | **Sin Claves Foraneas (Independientes)** | **10 tablas** | Catalogos maestros y entidades raiz (sede, modalidad, 	ipo_documento, 	ipo_vinculacion, 	ipo_evento, 	ipo_pregunta, estado_proceso, 
ol, periodo_academico, encuesta). |
| **Entregas Posteriores** | **Con Claves Foraneas (Dependientes)** | **27 tablas** | Entidades relacionales, programas, personas, catedras, sesiones, asistencia QR, encuestas y migracion Oracle/ASIS. |
| **Total Modelo** | **Esquema Completo catedras** | **37 tablas** | Modelo fisico PostgreSQL unificado. |
