-- ============================================================================
--  15 · Vistas
--
--  Seis vistas. Tres resuelven consultas que se repiten en varios informes,
--  y tres son CONTROLES: consultas que deben devolver cero.
-- ============================================================================

SET search_path TO catedras, public;

-- ---------------------------------------------------------------------------
-- v_asistente_vigente · la foto actual de una persona
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_asistente_vigente AS
SELECT a.id_asistente,
       a.id_asis,
       a.nombres || ' ' || a.apellidos          AS nombre_completo,
       a.es_externo,
       coalesce(a.correo_institucional, a.correo_personal) AS correo_contacto,
       (a.correo_institucional IS NOT NULL)     AS tiene_correo_institucional,
       d.numero                                  AS documento_vigente,
       d.fk_tipo_documento                       AS tipo_documento,
       v.fk_tipo_vinculacion                     AS vinculacion,
       tv.nombre                                 AS vinculacion_nombre,
       tv.es_interno,
       tv.exige_programa,
       a.activo
  FROM asistente a
  LEFT JOIN documento_asistente d
         ON d.fk_asistente = a.id_asistente AND d.vigente
  LEFT JOIN LATERAL (
        SELECT va.fk_tipo_vinculacion
          FROM vinculacion_asistente va
         WHERE va.fk_asistente = a.id_asistente AND va.fecha_fin IS NULL
         ORDER BY va.fecha_ini DESC LIMIT 1
       ) v ON true
  LEFT JOIN tipo_vinculacion tv ON tv.id_tipo_vinculacion = v.fk_tipo_vinculacion;

COMMENT ON VIEW v_asistente_vigente IS
    'La foto ACTUAL de una persona: su documento vigente y su vinculacion '
    'vigente. Ojo: para los informes de asistencia NO se usa esta vista, sino '
    'las instantaneas del registro. Aqui esta el hoy; alli, el dia de la '
    'catedra.';

-- ---------------------------------------------------------------------------
-- v_asistencia_completa · la union que necesitan casi todos los informes
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_asistencia_completa AS
SELECT r.id_registro,
       r.registrado_en,
       r.origen,
       c.id_evento_asis,
       c.nombre                AS catedra,
       s.id_sesion,
       s.numero_reunion,
       s.titulo                AS sesion,
       s.inicio,
       s.fk_periodo            AS periodo,
       se.nombre               AS sede,
       m.nombre                AS modalidad,
       a.id_asistente,
       a.id_asis,
       a.nombres || ' ' || a.apellidos AS asistente,
       a.es_externo,
       r.fk_programa_snapshot  AS programa,
       p.nombre                AS programa_nombre,
       p.fk_facultad           AS facultad,
       r.fk_vinculacion_snapshot AS vinculacion,
       tv.es_interno,
       (re.id_respuesta IS NOT NULL) AS respondio_encuesta
  FROM registro_asistencia r
  JOIN sesion   s  ON s.id_sesion    = r.fk_sesion
  JOIN catedra  c  ON c.id_catedra   = s.fk_catedra
  JOIN sede     se ON se.id_sede     = s.fk_sede
  JOIN modalidad m ON m.id_modalidad = s.fk_modalidad
  JOIN asistente a ON a.id_asistente = r.fk_asistente
  JOIN tipo_vinculacion tv ON tv.id_tipo_vinculacion = r.fk_vinculacion_snapshot
  LEFT JOIN programa_academico p ON p.codigo = r.fk_programa_snapshot
  LEFT JOIN respuesta_encuesta re ON re.fk_registro = r.id_registro;

COMMENT ON VIEW v_asistencia_completa IS
    'Base de los informes I1 a I5 y I14. Usa las INSTANTANEAS del registro, no '
    'el programa ni la vinculacion vigentes: es lo que hace que un informe de '
    'un periodo cerrado siga dando lo mismo dentro de un ano.';

-- ---------------------------------------------------------------------------
-- v_pendiente_migracion · la cola de trabajo del gestor
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_pendiente_migracion AS
SELECT s.id_sesion,
       c.id_evento_asis,
       c.nombre                    AS catedra,
       s.numero_reunion,
       s.inicio,
       count(*)                    AS registros,
       count(*) FILTER (WHERE a.id_asis IS NULL)              AS sin_id_asis,
       count(*) FILTER (WHERE r.fk_programa_snapshot IS NULL) AS sin_programa,
       count(*) FILTER (WHERE a.es_externo)                   AS externos,
       count(*) FILTER (WHERE a.id_asis IS NOT NULL
                          AND r.fk_programa_snapshot IS NOT NULL
                          AND NOT a.es_externo)               AS migrables
  FROM registro_asistencia r
  JOIN sesion    s ON s.id_sesion    = r.fk_sesion
  JOIN catedra   c ON c.id_catedra   = s.fk_catedra
  JOIN asistente a ON a.id_asistente = r.fk_asistente
 WHERE NOT EXISTS (SELECT 1 FROM lote_migracion lm
                    WHERE lm.fk_sesion = s.id_sesion
                      AND lm.fk_estado_proceso = 'CORRECTO')
 GROUP BY s.id_sesion, c.id_evento_asis, c.nombre, s.numero_reunion, s.inicio;

-- ---------------------------------------------------------------------------
-- v_evaluacion_sesion · el informe 3 del enunciado
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_evaluacion_sesion AS
SELECT s.id_sesion,
       c.nombre                       AS catedra,
       s.numero_reunion,
       p.orden,
       p.enunciado,
       tp.id_tipo_pregunta            AS tipo,
       count(ri.id_item)              AS respuestas,
       round(avg(ri.valor_numerico), 2) AS promedio,
       min(ri.valor_numerico)         AS minimo,
       max(ri.valor_numerico)         AS maximo
  FROM respuesta_item ri
  JOIN respuesta_encuesta re ON re.id_respuesta = ri.fk_respuesta
  JOIN registro_asistencia r ON r.id_registro   = re.fk_registro
  JOIN sesion  s ON s.id_sesion  = r.fk_sesion
  JOIN catedra c ON c.id_catedra = s.fk_catedra
  JOIN pregunta p ON p.id_pregunta = ri.fk_pregunta
  JOIN tipo_pregunta tp ON tp.id_tipo_pregunta = p.fk_tipo_pregunta
 WHERE tp.guarda_numero
 GROUP BY s.id_sesion, c.nombre, s.numero_reunion, p.orden, p.enunciado, tp.id_tipo_pregunta;

-- ---------------------------------------------------------------------------
-- v_embudo_registro · donde se cae la gente
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_embudo_registro AS
SELECT s.id_sesion,
       c.nombre AS catedra,
       s.numero_reunion,
       (SELECT count(*) FROM enlace_registro e WHERE e.fk_sesion = s.id_sesion)  AS enlaces,
       (SELECT count(*) FROM clave_acceso k
          JOIN enlace_registro e ON e.id_enlace = k.fk_enlace
         WHERE e.fk_sesion = s.id_sesion)                                        AS claves_enviadas,
       (SELECT count(*) FROM clave_acceso k
          JOIN enlace_registro e ON e.id_enlace = k.fk_enlace
         WHERE e.fk_sesion = s.id_sesion AND k.usado_en IS NOT NULL)             AS claves_usadas,
       (SELECT count(*) FROM registro_asistencia r WHERE r.fk_sesion = s.id_sesion) AS registros,
       (SELECT count(*) FROM respuesta_encuesta re
          JOIN registro_asistencia r ON r.id_registro = re.fk_registro
         WHERE r.fk_sesion = s.id_sesion)                                        AS encuestas
  FROM sesion s
  JOIN catedra c ON c.id_catedra = s.fk_catedra;

-- ---------------------------------------------------------------------------
-- v_control_ventana · CONTROL · debe devolver CERO filas
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_control_ventana AS
SELECT r.id_registro, r.registrado_en, e.ventana, r.origen
  FROM registro_asistencia r
  JOIN enlace_registro e ON e.id_enlace = r.fk_enlace
 WHERE r.origen NOT IN ('MANUAL', 'IMPORTADO')
   AND NOT (e.ventana @> r.registrado_en);

COMMENT ON VIEW v_control_ventana IS
    'CONTROL de RN-15. Debe devolver CERO filas siempre. Si alguna vez devuelve '
    'algo, es que se desactivo el disparador o que alguien inserto por detras.';

\echo '15 · Vistas creadas - 6'
