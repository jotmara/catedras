# Modelo de Datos — Versión 2: Entidades Relacionales y Esquema Físico

> **Versión 2 / Segunda Entrega** · Diccionario de datos, diagrama entidad-relación y definición de restricciones foráneas para Cátedras Abiertas USBMed.
> Esquema: `catedras` · Motor: PostgreSQL 16.

---

## 1. Diagrama de Relaciones Maestro-Detalle y Dependencias

```
                        [tipo_evento] (v1)
                              │
                              ▼
   [facultad] ◄──┐        [catedra] (9 dígitos ASIS, nombre_asis derivado)
       │         │            │ (1:N Maestro-Detalle #1)
       ▼         │            ▼
  [dependencia]──┘         [sesion] ◄── [modalidad] (v1)
       │                      │     ◄── [sede] (v1)
       ▼                      │     ◄── [periodo_academico] (v1)
 [programa_academico]         │
       │                      ├──▶ [enlace_registro] (1:N M-D #2, QR/URL con tstzrange)
       │ (1:N M-D #10)        │
       ├──▶ [alias_programa]  ├──▶ [registro_asistencia] (1:N M-D #3, firma de asistencia)
       │                      │          │
       ▼                      ▼          ▼ (1:N M-D #8)
 [programa_asistente]     [ponencia]   [respuesta_encuesta] ◄── [encuesta] (v2)
       ▲                      │ (Puente) │ (1:N M-D #9)            │ (1:N M-D #6)
       │                      ▼          ▼                         ▼
       │                  [asistente] [respuesta_item]          [pregunta]
       │                      ▲                                    │ (1:N M-D #7)
       │                      ├──▶ [documento_asistente] (1:N M-D #4)▼
       │                      ├──▶ [vinculacion_asistente]      [opcion_pregunta]
       │                      └──▶ [consentimiento_datos] (1:N M-D #5)
       └──────────────────────────────┘
```

---

## 2. Especificación Detallada de Tablas Maestro-Detalle

### 2.1 Módulo Cátedras y Sesiones (Núcleo)

#### Tabla `catedras.catedra` (Maestro)
- **PK:** `id_catedra` (BIGINT GENERATED ALWAYS AS IDENTITY)
- **Columnas:**
  - `id_evento_asis` CHAR(9) NOT NULL UNIQUE (Restricción: `CHECK (id_evento_asis ~ '^[0-9]{9}$')`).
  - `nombre` VARCHAR(200) NOT NULL.
  - `nombre_asis` VARCHAR(30) **GENERATED ALWAYS AS (left(nombre, 30)) STORED**.
  - `fk_tipo_evento` CHAR(4) NOT NULL REFERENCES `catedras.tipo_evento(id_tipo_evento)`.
  - `fk_dependencia` VARCHAR(15) REFERENCES `catedras.dependencia(id_dependencia)`.
  - `activo` BOOLEAN NOT NULL DEFAULT true.
  - `creado_en` TIMESTAMPTZ NOT NULL DEFAULT now().

#### Tabla `catedras.sesion` (Detalle de `catedra`)
- **PK:** `id_sesion` (BIGINT GENERATED ALWAYS AS IDENTITY)
- **Columnas:**
  - `fk_catedra` BIGINT NOT NULL REFERENCES `catedras.catedra(id_catedra)` ON DELETE RESTRICT.
  - `numero_reunion` SMALLINT NOT NULL (Autogenerado por `trg_sesion_consecutivo`).
  - `numero_reunion_asis` SMALLINT (Valor oficial en PeopleSoft ASIS si ya existía).
  - `titulo` VARCHAR(200).
  - `inicio` TIMESTAMPTZ NOT NULL.
  - `fin` TIMESTAMPTZ NOT NULL (Restricción: `CHECK (fin > inicio)`).
  - `fk_modalidad` VARCHAR(15) NOT NULL REFERENCES `catedras.modalidad(id_modalidad)`.
  - `fk_sede` VARCHAR(15) NOT NULL REFERENCES `catedras.sede(id_sede)`.
  - `fk_periodo` CHAR(6) NOT NULL REFERENCES `catedras.periodo_academico(id_periodo)`.
  - `fk_encuesta` BIGINT REFERENCES `catedras.encuesta(id_encuesta)`.
  - `lugar` VARCHAR(200).
  - `cupo` INTEGER CHECK (cupo IS NULL OR cupo > 0).
  - `estado` VARCHAR(15) NOT NULL DEFAULT 'PROGRAMADA'.
- **Restricción Única:** `UNIQUE (fk_catedra, numero_reunion)`.

---

### 2.2 Módulo de Acceso, Asistencia y Encuestas

#### Tabla `catedras.enlace_registro` (Detalle de `sesion`)
- **PK:** `id_enlace` (BIGINT GENERATED ALWAYS AS IDENTITY)
- **Columnas:**
  - `fk_sesion` BIGINT NOT NULL REFERENCES `catedras.sesion(id_sesion)` ON DELETE CASCADE.
  - `token` UUID NOT NULL DEFAULT gen_random_uuid() UNIQUE.
  - `url_publica` VARCHAR(300) NOT NULL.
  - `ruta_imagen_qr` VARCHAR(300).
  - `canal` VARCHAR(10) NOT NULL CHECK (canal IN ('QR', 'ENLACE')).
  - `ventana` TSTZRANGE NOT NULL (Rango de validez).
- **Restricción de Exclusión:** `EXCLUDE USING gist (fk_sesion WITH =, ventana WITH &&) WHERE (revocado_en IS NULL)`.

#### Tabla `catedras.registro_asistencia` (Detalle de `sesion`)
- **PK:** `id_registro` (BIGINT GENERATED ALWAYS AS IDENTITY)
- **Columnas:**
  - `fk_sesion` BIGINT NOT NULL REFERENCES `catedras.sesion(id_sesion)` ON DELETE RESTRICT.
  - `fk_asistente` BIGINT NOT NULL REFERENCES `catedras.asistente(id_asistente)` ON DELETE RESTRICT.
  - `fk_programa_snapshot` VARCHAR(5) (Instantánea del programa académico en el momento de asistir).
  - `registrado_en` TIMESTAMPTZ NOT NULL DEFAULT now().
- **Restricción Única:** `UNIQUE (fk_sesion, fk_asistente)`.

---

### 2.3 Cadenas Jerárquicas de Evaluación

#### Cadena 1: `encuesta` ──▶ `pregunta` ──▶ `opcion_pregunta`
- `encuesta`: PK `id_encuesta`, `nombre`, `version`, `activa`.
- `pregunta`: PK `id_pregunta`, `fk_encuesta` REFERENCES `encuesta` ON DELETE CASCADE, `enunciado`, `orden`, `fk_tipo_pregunta`.
- `opcion_pregunta`: PK `id_opcion`, `fk_pregunta` REFERENCES `pregunta` ON DELETE CASCADE, `etiqueta`, `valor`, `orden`.

#### Cadena 2: `registro_asistencia` ──▶ `respuesta_encuesta` ──▶ `respuesta_item`
- `respuesta_encuesta`: PK `id_respuesta`, `fk_registro` REFERENCES `registro_asistencia` ON DELETE CASCADE, `fk_encuesta`, `completa`.
- `respuesta_item`: PK `id_item`, `fk_respuesta` REFERENCES `respuesta_encuesta` ON DELETE CASCADE, `fk_pregunta`, `valor_numerico`, `valor_texto`, `fk_opcion`.
  - **Restricción Condicional:** `CHECK ((valor_numerico IS NOT NULL)::int + (valor_texto IS NOT NULL)::int + (fk_opcion IS NOT NULL)::int = 1)`.

---

### 2.4 Tabla Puente (N:M con Atributo)

#### Tabla `catedras.ponencia`
- **PK Compuesta:** `(fk_sesion, fk_asistente, rol)`
- **Columnas:**
  - `fk_sesion` BIGINT NOT NULL REFERENCES `catedras.sesion(id_sesion)` ON DELETE CASCADE.
  - `fk_asistente` BIGINT NOT NULL REFERENCES `catedras.asistente(id_asistente)` ON DELETE RESTRICT.
  - `rol` VARCHAR(15) NOT NULL DEFAULT 'PONENTE' CHECK (rol IN ('PONENTE', 'MODERADOR', 'INVITADO', 'ORGANIZADOR')).
- **Justificación:** Relaciona ponentes preexistentes con las sesiones sin duplicar registros personales.
