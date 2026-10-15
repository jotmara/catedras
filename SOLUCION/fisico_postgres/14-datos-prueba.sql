-- ============================================================================
--  14 · Datos de prueba · el flujo completo, de punta a punta
--
--  Reconstruye la catedra "Pedagogia Electoral" que el profesor Hugo Nelson
--  mostro en la reunion (1:06:25) y que hoy se recoge con un formulario
--  anonimo de Microsoft Forms.
--
--  Los asistentes son SINTETICOS. Los 164 nombres y cedulas reales del
--  formulario NO se reproducen aqui: son datos personales y el modelo se
--  demuestra igual de bien sin ellos.
-- ============================================================================

SET search_path TO catedras, public;

\echo '14 · Datos de prueba - flujo completo...'

-- ---------------------------------------------------------------------------
-- 0 · Un administrador
-- ---------------------------------------------------------------------------
INSERT INTO asistente (id_asis, nombres, apellidos, correo_institucional, es_externo)
VALUES ('30016947', 'Administrador', 'Catedras', 'admin.catedras@usbmed.edu.co', false)
ON CONFLICT (id_asis) DO NOTHING;

INSERT INTO vinculacion_asistente (fk_asistente, fk_tipo_vinculacion, fecha_ini)
SELECT id_asistente, 'ADMINISTRATIVO', date '2026-01-01'
  FROM asistente WHERE id_asis = '30016947'
ON CONFLICT DO NOTHING;

INSERT INTO usuario (fk_asistente, usuario, clave_hash)
SELECT id_asistente, 'admin.catedras', '$2a$11$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy'
  FROM asistente WHERE id_asis = '30016947'
ON CONFLICT (usuario) DO NOTHING;

INSERT INTO rol_por_usuario (fk_usuario, fk_rol, fecha_ini)
SELECT id_usuario, 'ADMIN', date '2026-01-01' FROM usuario WHERE usuario = 'admin.catedras'
ON CONFLICT DO NOTHING;

-- RN-31 · el mismo usuario recupera un rol que ya tuvo.
-- Sin fecha_ini en la clave primaria, este INSERT se rechazaria.
INSERT INTO rol_por_usuario (fk_usuario, fk_rol, fecha_ini, fecha_fin)
SELECT id_usuario, 'CONSULTA', date '2025-01-01', date '2025-06-30'
  FROM usuario WHERE usuario = 'admin.catedras'
ON CONFLICT DO NOTHING;
INSERT INTO rol_por_usuario (fk_usuario, fk_rol, fecha_ini)
SELECT id_usuario, 'CONSULTA', date '2026-02-01'
  FROM usuario WHERE usuario = 'admin.catedras'
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------------
-- 1 · La encuesta de calidad
-- ---------------------------------------------------------------------------
INSERT INTO encuesta (nombre, version, vigente_desde)
VALUES ('Calidad de la catedra abierta', 1, date '2026-01-01')
ON CONFLICT (nombre, version) DO NOTHING;

INSERT INTO pregunta (fk_encuesta, enunciado, orden, fk_tipo_pregunta, obligatoria, valor_min, valor_max)
SELECT e.id_encuesta, t.enunciado, t.orden, t.tipo, t.oblig, t.vmin, t.vmax
  FROM encuesta e,
       (VALUES ('Como califica la calidad general de la catedra', 1, 'ESCALA_5', true,  1, 5),
               ('Como califica al ponente',                       2, 'ESCALA_5', true,  1, 5),
               ('La duracion fue adecuada',                       3, 'SI_NO',    false, 0, 1),
               ('Que sugerencia tiene para mejorar',              4, 'TEXTO_LIBRE', false, NULL, NULL)
       ) AS t(enunciado, orden, tipo, oblig, vmin, vmax)
 WHERE e.nombre = 'Calidad de la catedra abierta' AND e.version = 1
ON CONFLICT (fk_encuesta, orden) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 2 · La catedra y tres sesiones simultaneas en sedes distintas
--     "puede que una catedra este en San Benito, otra este virtual y otra
--      este en Bello" (1:03:33)
-- ---------------------------------------------------------------------------
INSERT INTO catedra (id_evento_asis, nombre, fk_tipo_evento, fk_dependencia)
VALUES ('000099001', 'Pedagogia Electoral y participacion ciudadana', 'CAAB', 'DESA_HUM')
ON CONFLICT (id_evento_asis) DO NOTHING;

-- numero_reunion NO se digita: lo pone el disparador (RN-10)
INSERT INTO sesion (fk_catedra, numero_reunion, titulo, inicio, fin,
                    fk_modalidad, fk_sede, fk_periodo, fk_encuesta, lugar, cupo)
-- La catedra real fue el 2026-03-06 16:00. La sesion de prueba se ancla a la
-- hora de ejecucion para que la VENTANA DEL ENLACE este vigente y el flujo
-- completo se pueda ejercitar de verdad: si se dejara la fecha historica,
-- sp_solicitar_clave la rechazaria por RN-15, que es justo lo que debe hacer.
SELECT c.id_catedra, 0, t.titulo,
       date_trunc('hour', now()), date_trunc('hour', now()) + interval '2 hour',
       t.modalidad, t.sede,
       (SELECT id_periodo FROM periodo_academico
         WHERE current_date BETWEEN fecha_ini AND fecha_fin
         ORDER BY id_periodo LIMIT 1),
       (SELECT id_encuesta FROM encuesta WHERE nombre = 'Calidad de la catedra abierta' AND version = 1),
       t.lugar, t.cupo
  FROM catedra c,
       (VALUES ('Sesion San Benito', 'PRESENCIAL', 'SAN_BENITO', 'Auditorio Bolivariano', 200),
               ('Sesion Bello',      'PRESENCIAL', 'BELLO',      'Auditorio Bello',       80),
               ('Sesion virtual',    'VIRTUAL',    'VIRTUAL',    NULL,                  NULL)
       ) AS t(titulo, modalidad, sede, lugar, cupo)
 WHERE c.id_evento_asis = '000099001';

-- ---------------------------------------------------------------------------
-- 3 · Los enlaces · el boton que genera QR y URL
-- ---------------------------------------------------------------------------
DO $$
DECLARE
    r record;
    v_enlace bigint;
    v_admin  bigint;
BEGIN
    SELECT id_usuario INTO v_admin FROM usuario WHERE usuario = 'admin.catedras';

    FOR r IN SELECT s.id_sesion
               FROM sesion s JOIN catedra c ON c.id_catedra = s.fk_catedra
              WHERE c.id_evento_asis = '000099001'
              ORDER BY s.numero_reunion
    LOOP
        CALL sp_emitir_enlace(r.id_sesion, 60, 60, v_admin, v_enlace);
    END LOOP;
END $$;

-- ---------------------------------------------------------------------------
-- 4 · Los asistentes de prueba, incluidos los casos dificiles
-- ---------------------------------------------------------------------------

-- 4a · Un participante de RUTAS DE PAZ: sin programa y sin correo institucional
INSERT INTO asistente (id_asis, nombres, apellidos, correo_personal, es_externo)
VALUES ('30099001', 'Participante', 'Rutas de Paz', 'participante.rutas@gmail.com', false)
ON CONFLICT (id_asis) DO NOTHING;

INSERT INTO vinculacion_asistente (fk_asistente, fk_tipo_vinculacion, fecha_ini)
SELECT id_asistente, 'RUTAS_PAZ', date '2026-01-19'
  FROM asistente WHERE id_asis = '30099001'
ON CONFLICT DO NOTHING;

-- 4b · Un EXTERNO: sin id_asis. Se cuenta, pero nunca migra (RN-08)
INSERT INTO asistente (id_asis, nombres, apellidos, correo_personal, es_externo)
VALUES (NULL, 'Publico', 'Externo', 'publico.externo@gmail.com', true);

INSERT INTO vinculacion_asistente (fk_asistente, fk_tipo_vinculacion, fecha_ini)
SELECT id_asistente, 'EXTERNO', date '2026-03-06'
  FROM asistente WHERE correo_personal = 'publico.externo@gmail.com'::citext
ON CONFLICT DO NOTHING;

-- 4c · Consentimiento de todos los de prueba (Ley 1581)
INSERT INTO consentimiento_datos (fk_asistente, version_politica, canal)
SELECT id_asistente, '2026.1', 'WEB'
  FROM asistente
 WHERE id_asis IN ('30099001', '30016947')
    OR correo_personal = 'publico.externo@gmail.com'::citext
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------------
-- 5 · 164 registros en la sesion de San Benito, con el flujo real:
--     solicitar clave -> validar clave -> registrar
--
--     Son 164 porque es el numero exacto de respuestas que trajo el
--     formulario de Pedagogia Electoral.
-- ---------------------------------------------------------------------------
DO $$
DECLARE
    v_sesion   bigint;
    v_token    uuid;
    v_clave_id bigint;
    v_clave    text;
    v_correo   text;
    v_reg      bigint;
    r          record;
    n          integer := 0;
BEGIN
    SELECT s.id_sesion INTO v_sesion
      FROM sesion s JOIN catedra c ON c.id_catedra = s.fk_catedra
     WHERE c.id_evento_asis = '000099001' AND s.fk_sede = 'SAN_BENITO';

    SELECT token INTO v_token FROM enlace_registro
     WHERE fk_sesion = v_sesion AND revocado_en IS NULL;

    -- DISTINCT porque una persona puede tener VARIOS programas (H12, el N:M).
    -- Sin el, el mismo asistente entraria dos veces y uq_registro_sesion_asis
    -- lo rechazaria - que es exactamente lo que debe hacer (RN-21).
    FOR r IN SELECT DISTINCT a.id_asis
               FROM asistente a
               JOIN programa_asistente pa ON pa.fk_asistente = a.id_asistente
              WHERE a.id_asis IS NOT NULL
              ORDER BY a.id_asis
              LIMIT 164
    LOOP
        CALL sp_solicitar_clave(r.id_asis, v_token, '10.0.0.1'::inet,
                                v_clave_id, v_clave, v_correo);
        CALL sp_validar_clave_y_registrar(v_clave_id, v_clave, '10.0.0.1'::inet,
                                          'Mozilla/5.0 (prueba)', v_reg);
        n := n + 1;
    END LOOP;

    RAISE NOTICE '% registros creados con el flujo completo', n;
END $$;

-- 5b · El de Rutas de Paz: se registra SIN programa (RN-07)
DO $$
DECLARE
    v_sesion bigint; v_token uuid; v_cid bigint; v_cl text; v_co text; v_reg bigint;
BEGIN
    SELECT s.id_sesion INTO v_sesion
      FROM sesion s JOIN catedra c ON c.id_catedra = s.fk_catedra
     WHERE c.id_evento_asis = '000099001' AND s.fk_sede = 'SAN_BENITO';
    SELECT token INTO v_token FROM enlace_registro
     WHERE fk_sesion = v_sesion AND revocado_en IS NULL;

    CALL sp_solicitar_clave('30099001', v_token, NULL, v_cid, v_cl, v_co);
    CALL sp_validar_clave_y_registrar(v_cid, v_cl, NULL, NULL, v_reg);
    RAISE NOTICE 'Rutas de Paz registrado sin programa. Correo destino: %', v_co;
END $$;

-- 5c · El externo, por la via manual (no esta en el maestro del ASIS)
INSERT INTO registro_asistencia (fk_sesion, fk_asistente, fk_vinculacion_snapshot, origen)
SELECT s.id_sesion, a.id_asistente, 'EXTERNO', 'MANUAL'
  FROM sesion s
  JOIN catedra c ON c.id_catedra = s.fk_catedra
  CROSS JOIN asistente a
 WHERE c.id_evento_asis = '000099001' AND s.fk_sede = 'SAN_BENITO'
   AND a.correo_personal = 'publico.externo@gmail.com'::citext
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------------
-- 6 · Encuestas respondidas · 60 de los 164
-- ---------------------------------------------------------------------------
DO $$
DECLARE
    r    record;
    v_rp bigint;
    p1 bigint; p2 bigint; p3 bigint; p4 bigint;
    n integer := 0;
BEGIN
    SELECT max(CASE WHEN orden=1 THEN id_pregunta END),
           max(CASE WHEN orden=2 THEN id_pregunta END),
           max(CASE WHEN orden=3 THEN id_pregunta END),
           max(CASE WHEN orden=4 THEN id_pregunta END)
      INTO p1, p2, p3, p4
      FROM pregunta p JOIN encuesta e ON e.id_encuesta = p.fk_encuesta
     WHERE e.nombre = 'Calidad de la catedra abierta';

    FOR r IN SELECT ra.id_registro, row_number() OVER (ORDER BY ra.id_registro) AS i
               FROM registro_asistencia ra
               JOIN sesion s ON s.id_sesion = ra.fk_sesion
               JOIN catedra c ON c.id_catedra = s.fk_catedra
              WHERE c.id_evento_asis = '000099001'
              ORDER BY ra.id_registro
              LIMIT 60
    LOOP
        CALL sp_responder_encuesta(r.id_registro,
             jsonb_build_array(
                jsonb_build_object('pregunta', p1, 'numero', 3 + (r.i % 3)),
                jsonb_build_object('pregunta', p2, 'numero', 4 + (r.i % 2)),
                jsonb_build_object('pregunta', p3, 'numero', r.i % 2),
                jsonb_build_object('pregunta', p4, 'texto',
                                   CASE WHEN r.i % 10 = 0
                                        THEN 'Mas tiempo para preguntas'
                                        ELSE 'Todo bien' END)),
             v_rp);
        n := n + 1;
    END LOOP;
    RAISE NOTICE '% encuestas respondidas', n;
END $$;

-- ---------------------------------------------------------------------------
-- 7 · El lote de migracion al ASIS
-- ---------------------------------------------------------------------------
DO $$
DECLARE
    v_sesion bigint; v_lote bigint;
BEGIN
    SELECT s.id_sesion INTO v_sesion
      FROM sesion s JOIN catedra c ON c.id_catedra = s.fk_catedra
     WHERE c.id_evento_asis = '000099001' AND s.fk_sede = 'SAN_BENITO';

    CALL sp_generar_lote_migracion(v_sesion, NULL, v_lote);

    UPDATE lote_migracion
       SET fk_estado_proceso = 'CORRECTO', instancia_proceso_asis = '9284471'
     WHERE id_lote_migracion = v_lote;

    UPDATE detalle_migracion SET resultado = 'ACEPTADO'
     WHERE fk_lote_migracion = v_lote;

    RAISE NOTICE 'Lote % generado y aceptado', v_lote;
END $$;

\echo '14 · Datos de prueba creados'
