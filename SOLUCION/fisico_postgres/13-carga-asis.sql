-- ============================================================================
--  13 · Carga de los datos REALES del ASIS
--
--  Requisito: haber ejecutado antes  python preparar-datos.py
--             que escribe datos/*.csv a partir de los dos Excel.
--
--  Volumenes esperados, medidos sobre los archivos reales:
--      catedras     5.496      programas       105
--      sesiones     5.711      personas     14.808
--      documentos  15.517      matriculas   15.349
--
--  Se carga a tablas de paso y de ahi al modelo. Nada entra por conversion
--  implicita: todo llega como texto y se convierte con evidencia.
-- ============================================================================

SET search_path TO catedras, public;

\echo '13 · Cargando datos reales del ASIS...'

-- ---------------------------------------------------------------------------
-- Tablas de paso
-- ---------------------------------------------------------------------------
CREATE TEMP TABLE stg_catedra   (id_evento_asis text, nombre text, tipo_evento text);
CREATE TEMP TABLE stg_sesion    (id_evento_asis text, numero_reunion text);
CREATE TEMP TABLE stg_programa  (codigo text, nombre text);
CREATE TEMP TABLE stg_asistente (id_asis text, nombres text, apellidos text,
                                 nombre_completo_asis text, correo_institucional text);
CREATE TEMP TABLE stg_documento (id_asis text, tipo text, numero text, vigente text);
CREATE TEMP TABLE stg_matricula (id_asis text, codigo text);
CREATE TEMP TABLE stg_novedad   (numero_fila text, contenido_crudo text, motivo text);

\copy stg_catedra   FROM 'datos/catedra.csv'   WITH (FORMAT csv, HEADER true)
\copy stg_sesion    FROM 'datos/sesion.csv'    WITH (FORMAT csv, HEADER true)
\copy stg_programa  FROM 'datos/programa.csv'  WITH (FORMAT csv, HEADER true)
\copy stg_asistente FROM 'datos/asistente.csv' WITH (FORMAT csv, HEADER true)
\copy stg_documento FROM 'datos/documento.csv' WITH (FORMAT csv, HEADER true)
\copy stg_matricula FROM 'datos/matricula.csv' WITH (FORMAT csv, HEADER true)
\copy stg_novedad   FROM 'datos/novedad.csv'   WITH (FORMAT csv, HEADER true)

-- ---------------------------------------------------------------------------
-- El lote, para que la carga deje evidencia
-- ---------------------------------------------------------------------------
INSERT INTO lote_carga_asistente (nombre_archivo, filas_leidas, observaciones)
SELECT 'USBME_EMPLID_CATED_V1_1504983333.xlsx',
       (SELECT count(*) FROM stg_asistente) + (SELECT count(*) FROM stg_novedad),
       'Carga inicial. Nombres y correos SINTETIZADOS: el informe actual del '
       'ASIS solo entrega tres columnas. Ver riesgo 1 del plan.';

-- ---------------------------------------------------------------------------
-- 1 · Programas
-- ---------------------------------------------------------------------------
INSERT INTO programa_academico (codigo, nombre, fk_facultad, nivel)
SELECT s.codigo, s.nombre, 'F_OTRA',
       CASE WHEN s.codigo ~ '^M0[0-4]' THEN 'PREGRADO' ELSE 'OTRO' END
  FROM stg_programa s
ON CONFLICT (codigo) DO NOTHING;

-- El unico programa cuyo nombre real conocemos: lo dijo el profesor Carlos
-- Castro en 49:55 y el profesor Hugo Nelson lo confirmo en 50:01.
UPDATE programa_academico
   SET nombre = 'Ingenieria de Datos y Software', fk_facultad = 'F_ING'
 WHERE codigo = 'M0286';

-- ---------------------------------------------------------------------------
-- 2 · Catedras · H8 · el id llega ya con ceros a la izquierda
-- ---------------------------------------------------------------------------
INSERT INTO catedra (id_evento_asis, nombre, fk_tipo_evento)
SELECT s.id_evento_asis, s.nombre,
       CASE WHEN EXISTS (SELECT 1 FROM tipo_evento t
                          WHERE t.id_tipo_evento = rpad(s.tipo_evento, 4))
            THEN rpad(s.tipo_evento, 4) ELSE 'CAAB' END
  FROM stg_catedra s
ON CONFLICT (id_evento_asis) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 3 · Sesiones · H12 · el numero llegaba como flotante y ya viene entero
--
-- Se cargan con fechas sinteticas derivadas del numero de reunion: el listado
-- del ASIS no trae fecha. Lo que importa aqui es el CONSECUTIVO, que es lo
-- que se va a comprobar.
-- ---------------------------------------------------------------------------
INSERT INTO sesion (fk_catedra, numero_reunion, inicio, fin,
                    fk_modalidad, fk_sede, fk_periodo, estado)
SELECT c.id_catedra,
       s.numero_reunion::smallint,
       timestamptz '2026-01-19 08:00-05' + (s.numero_reunion::int - 1) * interval '7 day',
       timestamptz '2026-01-19 10:00-05' + (s.numero_reunion::int - 1) * interval '7 day',
       'PRESENCIAL', 'SAN_BENITO', '2026-1', 'CERRADA'
  FROM stg_sesion s
  JOIN catedra c ON c.id_evento_asis = s.id_evento_asis
ON CONFLICT (fk_catedra, numero_reunion) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 4 · Asistentes
-- ---------------------------------------------------------------------------
INSERT INTO asistente (id_asis, nombres, apellidos, nombre_completo_asis,
                       correo_institucional, es_externo, fk_lote_carga)
SELECT s.id_asis, s.nombres, s.apellidos, s.nombre_completo_asis,
       s.correo_institucional::citext, false,
       (SELECT max(id_lote_carga) FROM lote_carga_asistente)
  FROM stg_asistente s
ON CONFLICT (id_asis) DO NOTHING;

-- Toda persona del maestro es interna, y su vinculacion por defecto es
-- estudiante. En produccion esto vendra en el informe ampliado.
INSERT INTO vinculacion_asistente (fk_asistente, fk_tipo_vinculacion, fecha_ini)
SELECT a.id_asistente, 'ESTUDIANTE', date '2026-01-19'
  FROM asistente a
 WHERE a.id_asis IS NOT NULL
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------------
-- 5 · Documentos · H10 · aqui se comprueban los 707 casos
-- ---------------------------------------------------------------------------
INSERT INTO documento_asistente (fk_asistente, fk_tipo_documento, numero, vigente)
SELECT a.id_asistente, s.tipo, s.numero, s.vigente::boolean
  FROM stg_documento s
  JOIN asistente a ON a.id_asis = s.id_asis
ON CONFLICT (fk_tipo_documento, numero) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 6 · Matriculas · H11 · los pares duplicados ya vienen deduplicados
-- ---------------------------------------------------------------------------
INSERT INTO programa_asistente (fk_asistente, fk_programa, fk_periodo, estado)
SELECT a.id_asistente, s.codigo, '2026-1', 'ACTIVO'
  FROM stg_matricula s
  JOIN asistente a ON a.id_asis = s.id_asis
  JOIN programa_academico p ON p.codigo = s.codigo
ON CONFLICT DO NOTHING;

-- ---------------------------------------------------------------------------
-- 7 · Novedades y cierre del lote
-- ---------------------------------------------------------------------------
INSERT INTO novedad_carga (fk_lote_carga, numero_fila, contenido_crudo, motivo)
SELECT (SELECT max(id_lote_carga) FROM lote_carga_asistente),
       s.numero_fila::int, s.contenido_crudo, s.motivo
  FROM stg_novedad s;

-- Se cuentan los asistentes de ESTE lote, no todos los de la tabla: si no,
-- una segunda carga violaria chk_lote_carga_filas al sumar los anteriores.
UPDATE lote_carga_asistente l
   SET filas_aceptadas  = (SELECT count(*) FROM asistente a WHERE a.fk_lote_carga = l.id_lote_carga),
       filas_rechazadas = (SELECT count(*) FROM stg_novedad)
 WHERE l.id_lote_carga = (SELECT max(id_lote_carga) FROM lote_carga_asistente);

-- ---------------------------------------------------------------------------
-- 8 · Alias de programa · lo que trae el formulario en texto libre
-- ---------------------------------------------------------------------------
INSERT INTO alias_programa (texto_normalizado, fk_programa, origen)
SELECT fn_normalizar(t.txt), 'M0286', 'FORMULARIO'
  FROM (VALUES ('Ingenieria de datos y software'),
               ('Ingenieria de Datos y Software'),
               ('ingenieria de datos'),
               ('Ing. datos y software')) AS t(txt)
ON CONFLICT (texto_normalizado) DO NOTHING;

-- ============================================================================
-- VERIFICACIONES · deben coincidir con los volumenes del encabezado
-- ============================================================================
\echo ''
\echo 'Verificacion de la carga:'

SELECT 'catedras'    AS objeto, count(*) AS filas, 5496 AS esperado FROM catedra
UNION ALL SELECT 'sesiones',   count(*), 5711  FROM sesion
UNION ALL SELECT 'programas',  count(*), 105   FROM programa_academico
UNION ALL SELECT 'asistentes', count(*), 14808 FROM asistente
UNION ALL SELECT 'documentos', count(*), 15517 FROM documento_asistente
UNION ALL SELECT 'matriculas', count(*), 15349 FROM programa_asistente;

\echo ''
\echo 'H10 · personas con mas de un documento (deben ser 707):'
SELECT count(*) AS personas_con_varios_documentos
  FROM (SELECT fk_asistente FROM documento_asistente
         GROUP BY fk_asistente HAVING count(*) > 1) q;

\echo ''
\echo 'H4 · el par (catedra, reunion) es unico - lo garantiza uq_sesion_reunion.'
\echo 'H2 · nombres truncados a 30 por el ASIS, recuperados en la columna nombre:'
SELECT nombre_asis, left(nombre, 45) AS nombre_completo
  FROM catedra
 WHERE length(nombre) >= 30
 LIMIT 3;

\echo '13 · Carga real terminada'
