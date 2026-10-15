-- ============================================================================
--  09 · Indices
--
--  Cada indice esta justificado por un informe o por una regla. No hay ninguno
--  "por si acaso": un indice que nadie usa cuesta escritura y espacio.
--
--  Las claves primarias y las restricciones UNIQUE ya crean su indice; aqui
--  solo van los que faltan.
-- ============================================================================

SET search_path TO catedras, public;

-- ============================================================================
-- A · Los tres indices del acceso (RN-06)
--
-- "Pongamosle 3 opciones, o sea, tiene que entrar por una de las 3" (57:27):
-- codigo, documento o correo. Los tres tienen que resolver igual de rapido,
-- porque los tres son la misma pantalla.
-- ============================================================================

-- 1 · por codigo ASIS  -> ya lo da uq_asistente_asis
-- 2 · por correo       -> ya lo dan uq_asistente_corinst y el indice de abajo
CREATE INDEX ix_asistente_correo_personal
    ON asistente (correo_personal)
    WHERE correo_personal IS NOT NULL;

-- 3 · por numero de documento -> ya lo da uq_documento_numero, pero la
--     pantalla busca SOLO por numero, sin saber el tipo
CREATE INDEX ix_documento_numero
    ON documento_asistente (numero);

COMMENT ON INDEX ix_documento_numero IS
    'La persona digita su cedula sin decir que tipo de documento es. Sin este '
    'indice, uq_documento_numero no sirve porque su primera columna es el tipo.';

-- RN-05 · un solo documento VIGENTE por asistente. Indice unico PARCIAL:
-- en MySQL no existen y habria que emularlo con una columna generada.
CREATE UNIQUE INDEX ux_documento_vigente
    ON documento_asistente (fk_asistente)
    WHERE vigente;

-- ============================================================================
-- B · Vinculacion y programas
-- ============================================================================

-- La vinculacion VIGENTE de una persona: la busca el disparador de instantanea
-- en cada registro, que es la operacion mas frecuente del sistema.
CREATE INDEX ix_vinculacion_vigente
    ON vinculacion_asistente (fk_asistente, fecha_ini DESC)
    WHERE fecha_fin IS NULL;

CREATE INDEX ix_progasi_programa  ON programa_asistente (fk_programa);
CREATE INDEX ix_progasi_periodo   ON programa_asistente (fk_periodo);

-- I2 e I3 · estadisticas por programa y por facultad
CREATE INDEX ix_programa_facultad ON programa_academico (fk_facultad);

-- ============================================================================
-- C · Catedras y sesiones
-- ============================================================================

-- I8 · siguiente numero de reunion -> lo resuelve uq_sesion_reunion
-- Agenda del dia y control de ventana
CREATE INDEX ix_sesion_inicio   ON sesion (inicio DESC);
CREATE INDEX ix_sesion_periodo  ON sesion (fk_periodo);

-- I14 · asistencia por sede y por modalidad
CREATE INDEX ix_sesion_sede      ON sesion (fk_sede);
CREATE INDEX ix_sesion_modalidad ON sesion (fk_modalidad);

CREATE INDEX ix_catedra_tipo   ON catedra (fk_tipo_evento);
CREATE INDEX ix_catedra_depend ON catedra (fk_dependencia)
    WHERE fk_dependencia IS NOT NULL;

-- ============================================================================
-- D · Acceso y registro - los mas criticos
-- ============================================================================

-- RN-14 · a lo sumo UN enlace vigente por sesion. Indice unico parcial.
CREATE UNIQUE INDEX ux_enlace_vigente
    ON enlace_registro (fk_sesion)
    WHERE revocado_en IS NULL;

-- RN-15 · resolver "este instante esta dentro de la ventana" con el indice
CREATE INDEX ix_enlace_ventana
    ON enlace_registro USING gist (ventana);

CREATE INDEX ix_clave_asistente ON clave_acceso (fk_asistente, generado_en DESC);
CREATE INDEX ix_clave_enlace    ON clave_acceso (fk_enlace);

-- I18 · claves enviadas a correo NO institucional. Parcial: es el caso raro,
-- y justamente por eso el indice es pequeno y muy selectivo.
CREATE INDEX ix_clave_no_institucional
    ON clave_acceso (generado_en DESC)
    WHERE NOT es_correo_institucional;

COMMENT ON INDEX ix_clave_no_institucional IS
    'I18. Alimenta la decision que el profesor Carlos Castro dejo pendiente en '
    '55:32 sobre los correos no institucionales.';

-- I19 · intentos fallidos, para vigilancia
CREATE INDEX ix_clave_intentos
    ON clave_acceso (fk_asistente, intentos)
    WHERE intentos > 0;

-- I1 · asistentes de una sesion. Es LA consulta de la pantalla del dia.
CREATE INDEX ix_registro_sesion    ON registro_asistencia (fk_sesion, registrado_en);
CREATE INDEX ix_registro_asistente ON registro_asistencia (fk_asistente);

-- I2 · estadisticas por programa, sobre la INSTANTANEA
CREATE INDEX ix_registro_programa_snap
    ON registro_asistencia (fk_programa_snapshot)
    WHERE fk_programa_snapshot IS NOT NULL;

-- I4 e I5 · internos contra externos, por vinculacion
CREATE INDEX ix_registro_vinc_snap ON registro_asistencia (fk_vinculacion_snapshot);

-- H18 · 164 personas registrandose en 60 segundos. La consulta de control de
-- concurrencia y el embudo I13 filtran por instante.
CREATE INDEX ix_registro_fecha ON registro_asistencia (registrado_en DESC);

-- ============================================================================
-- E · Encuesta
-- ============================================================================
CREATE INDEX ix_pregunta_encuesta  ON pregunta (fk_encuesta, orden);
CREATE INDEX ix_respitem_pregunta  ON respuesta_item (fk_pregunta);
CREATE INDEX ix_respenc_encuesta   ON respuesta_encuesta (fk_encuesta);

-- ============================================================================
-- F · Integracion
-- ============================================================================

-- H17 · emparejamiento DIFUSO del texto libre de los formularios contra el
-- catalogo de programas. Es lo que permite migrar lo historico.
CREATE INDEX ix_alias_trgm
    ON alias_programa USING gin (texto_normalizado gin_trgm_ops);

COMMENT ON INDEX ix_alias_trgm IS
    'Indice de trigramas. Permite resolver "Psicologica" -> PSICOLOGIA y '
    '"Ingenieria de datos y software" -> M0286 por similitud, no por igualdad. '
    'En otro motor esto exigiria una tabla de equivalencias exactas o trabajo '
    'manual sobre cada fila.';

CREATE INDEX ix_novedad_lote     ON novedad_carga (fk_lote_carga);
CREATE INDEX ix_lotemig_sesion   ON lote_migracion (fk_sesion, generado_en DESC);
CREATE INDEX ix_detmig_registro  ON detalle_migracion (fk_registro);

-- RN-29 · un registro solo puede quedar ACEPTADO en UN lote.
-- Indice unico parcial: los intentos rechazados pueden repetirse.
CREATE UNIQUE INDEX ux_detmig_aceptado
    ON detalle_migracion (fk_registro)
    WHERE resultado = 'ACEPTADO';

COMMENT ON INDEX ux_detmig_aceptado IS
    'RN-29. Permite reintentar cuantas veces haga falta y garantiza que la '
    'asistencia no se cargue dos veces en el ASIS.';

-- ============================================================================
-- G · Seguridad
-- ============================================================================
CREATE INDEX ix_bitacora_tabla  ON bitacora (nombre_tabla, ocurrido_en DESC);
CREATE INDEX ix_bitacora_fecha  ON bitacora (ocurrido_en DESC);

-- Rol vigente de un usuario
CREATE INDEX ix_rolusr_vigente
    ON rol_por_usuario (fk_usuario)
    WHERE fecha_fin IS NULL;

\echo '09 · Indices creados'
