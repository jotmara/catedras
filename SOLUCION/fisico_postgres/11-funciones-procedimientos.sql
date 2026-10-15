-- ============================================================================
--  11 · Funciones y procedimientos
--
--  Aqui estan las tres participaciones minimas de uno que ninguna clave
--  foranea puede garantizar, y las tres operaciones del flujo de registro.
-- ============================================================================

SET search_path TO catedras, public;

-- ============================================================================
-- fn_siguiente_reunion · el numero que hoy se busca a mano (I8)
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_siguiente_reunion(p_id_evento_asis char(9))
RETURNS smallint
LANGUAGE sql STABLE
AS $$
    SELECT coalesce(max(s.numero_reunion), 0)::smallint + 1
      FROM catedra c
      LEFT JOIN sesion s ON s.fk_catedra = c.id_catedra
     WHERE c.id_evento_asis = p_id_evento_asis;
$$;

COMMENT ON FUNCTION fn_siguiente_reunion(char) IS
    'I8. Sustituye el paso 2 del manual de migracion: la busqueda manual de la '
    'ultima reunion en un listado de 5.711 filas.';

-- ============================================================================
-- fn_resolver_asistente · RN-06, las tres puertas de entrada
--
-- "Tiene que entrar por una de las 3" (57:27): codigo, documento o correo.
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_resolver_asistente(p_identificador text)
RETURNS bigint
LANGUAGE plpgsql STABLE
AS $$
DECLARE
    v_id  bigint;
    v_txt text := trim(p_identificador);
BEGIN
    IF v_txt IS NULL OR v_txt = '' THEN
        RETURN NULL;
    END IF;

    -- El formulario actual trae valores como 'ID:30000141979'
    v_txt := regexp_replace(v_txt, '^\s*(ID|Id|id)\s*[:.-]\s*', '');

    -- 1 · por codigo ASIS
    SELECT a.id_asistente INTO v_id
      FROM asistente a
     WHERE a.id_asis = v_txt AND a.activo;
    IF v_id IS NOT NULL THEN RETURN v_id; END IF;

    -- 2 · por correo, institucional o personal
    IF v_txt LIKE '%@%' THEN
        SELECT a.id_asistente INTO v_id
          FROM asistente a
         WHERE (a.correo_institucional = v_txt::citext
             OR a.correo_personal      = v_txt::citext)
           AND a.activo
         LIMIT 1;
        IF v_id IS NOT NULL THEN RETURN v_id; END IF;
    END IF;

    -- 3 · por numero de documento, VIGENTE O NO
    SELECT d.fk_asistente INTO v_id
      FROM documento_asistente d
      JOIN asistente a ON a.id_asistente = d.fk_asistente
     WHERE d.numero = v_txt AND a.activo
     ORDER BY d.vigente DESC
     LIMIT 1;

    RETURN v_id;
END;
$$;

COMMENT ON FUNCTION fn_resolver_asistente(text) IS
    'RN-06. Busca por las tres vias y devuelve el asistente, o NULL. Busca en '
    'documentos VIGENTES Y NO VIGENTES a proposito: los 707 casos de personas '
    'con varios documentos son justamente quienes digitan el antiguo. Elimina '
    'el trabajo manual que describio el profesor Hugo Nelson en 42:01.';

-- ============================================================================
-- fn_resolver_programa · H17, el texto libre de los formularios
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_resolver_programa(p_texto text,
                                                p_umbral real DEFAULT 0.45)
RETURNS varchar(5)
LANGUAGE plpgsql STABLE
AS $$
DECLARE
    v_norm   text := fn_normalizar(p_texto);
    v_codigo varchar(5);
BEGIN
    IF v_norm IS NULL OR v_norm = '' THEN RETURN NULL; END IF;

    -- 1 · el codigo ya viene bien escrito
    SELECT codigo INTO v_codigo FROM programa_academico
     WHERE upper(trim(p_texto)) = codigo;
    IF v_codigo IS NOT NULL THEN RETURN v_codigo; END IF;

    -- 2 · alias exacto ya conocido
    SELECT fk_programa INTO v_codigo FROM alias_programa
     WHERE texto_normalizado = v_norm;
    IF v_codigo IS NOT NULL THEN RETURN v_codigo; END IF;

    -- 3 · nombre exacto del programa
    SELECT codigo INTO v_codigo FROM programa_academico
     WHERE fn_normalizar(nombre) = v_norm;
    IF v_codigo IS NOT NULL THEN RETURN v_codigo; END IF;

    -- 4 · similitud por trigramas, con umbral
    SELECT codigo INTO v_codigo
      FROM programa_academico
     WHERE similarity(fn_normalizar(nombre), v_norm) >= p_umbral
     ORDER BY similarity(fn_normalizar(nombre), v_norm) DESC
     LIMIT 1;

    RETURN v_codigo;
END;
$$;

COMMENT ON FUNCTION fn_resolver_programa(text, real) IS
    'Resuelve el texto libre del formulario contra el catalogo. Cuatro pasos, '
    'del mas seguro al mas arriesgado. El paso 4 puede equivocarse: por eso '
    'devuelve NULL antes que adivinar por debajo del umbral, y lo que quede sin '
    'resolver se cuenta y se revisa a mano.';

-- ============================================================================
-- sp_emitir_enlace · el boton que genera el QR y la URL
-- ============================================================================
CREATE OR REPLACE PROCEDURE sp_emitir_enlace(
    p_id_sesion       bigint,
    p_minutos_antes   integer DEFAULT NULL,
    p_minutos_despues integer DEFAULT NULL,
    p_usuario         bigint  DEFAULT NULL,
    INOUT p_id_enlace bigint  DEFAULT NULL)
LANGUAGE plpgsql
AS $$
DECLARE
    v_ini    timestamptz;
    v_fin    timestamptz;
    v_canal  varchar(10);
    v_antes  integer;
    v_desp   integer;
    v_token  uuid := gen_random_uuid();
    v_base   text;
BEGIN
    SELECT s.inicio, s.fin, m.canal_difusion
      INTO v_ini, v_fin, v_canal
      FROM sesion s
      JOIN modalidad m ON m.id_modalidad = s.fk_modalidad
     WHERE s.id_sesion = p_id_sesion;

    IF v_ini IS NULL THEN
        RAISE EXCEPTION 'No existe la sesion %', p_id_sesion;
    END IF;

    v_antes := coalesce(p_minutos_antes,
                        (SELECT valor::int FROM parametro WHERE clave = 'VENTANA_MINUTOS_ANTES'), 30);
    v_desp  := coalesce(p_minutos_despues,
                        (SELECT valor::int FROM parametro WHERE clave = 'VENTANA_MINUTOS_DESPUES'), 30);
    v_base  := coalesce((SELECT valor FROM parametro WHERE clave = 'URL_BASE'),
                        'https://catedras.usbmed.edu.co/r/');

    IF v_canal = 'AMBOS' THEN v_canal := 'QR'; END IF;

    -- RN-14 · se revoca el enlace vigente anterior, si lo hay
    UPDATE enlace_registro
       SET revocado_en = now()
     WHERE fk_sesion = p_id_sesion AND revocado_en IS NULL;

    INSERT INTO enlace_registro (fk_sesion, token, url_publica, ruta_imagen_qr,
                                 canal, ventana, fk_usuario_crea)
    VALUES (p_id_sesion, v_token, v_base || v_token::text,
            'qr/' || v_token::text || '.png', v_canal,
            tstzrange(v_ini - make_interval(mins => v_antes),
                      v_fin + make_interval(mins => v_desp), '[)'),
            p_usuario)
    RETURNING id_enlace INTO p_id_enlace;
END;
$$;

COMMENT ON PROCEDURE sp_emitir_enlace(bigint, integer, integer, bigint, bigint) IS
    'El boton del .docx: "el administrador toca un boton y genera el QR y URL '
    'del registro de la catedra especifica". La ventana sale de los parametros, '
    'que es lo que pide "el administrador configura hora de inicio y hora de fin".';

-- ============================================================================
-- sp_solicitar_clave · RN-17, RN-18, RN-19
-- ============================================================================
CREATE OR REPLACE PROCEDURE sp_solicitar_clave(
    p_identificador  text,
    p_token          uuid,
    p_ip             inet    DEFAULT NULL,
    INOUT p_id_clave bigint  DEFAULT NULL,
    INOUT p_clave    text    DEFAULT NULL,
    INOUT p_enviado_a text   DEFAULT NULL)
LANGUAGE plpgsql
AS $$
DECLARE
    v_asistente bigint;
    v_enlace    bigint;
    v_vigencia  integer;
    v_longitud  integer;
BEGIN
    -- RN-01 y RN-06 · solo entra quien esta en la tabla
    v_asistente := fn_resolver_asistente(p_identificador);
    IF v_asistente IS NULL THEN
        RAISE EXCEPTION
            'RN-01: no hay ningun asistente registrado con el identificador %', p_identificador
            USING ERRCODE = 'no_data_found';
    END IF;

    SELECT id_enlace INTO v_enlace
      FROM enlace_registro
     WHERE token = p_token AND revocado_en IS NULL AND ventana @> now();

    IF v_enlace IS NULL THEN
        RAISE EXCEPTION 'RN-15: el enlace no existe, esta revocado o esta fuera de su ventana'
            USING ERRCODE = 'check_violation';
    END IF;

    v_vigencia := coalesce((SELECT valor::int FROM parametro WHERE clave = 'CLAVE_VIGENCIA_MINUTOS'), 10);
    v_longitud := coalesce((SELECT valor::int FROM parametro WHERE clave = 'CLAVE_LONGITUD'), 6);

    -- La clave en claro se devuelve para enviarla por correo y NO se guarda
    p_clave := lpad((floor(random() * (10::numeric ^ v_longitud)))::bigint::text, v_longitud, '0');

    -- RN-19 · a que correo: institucional si existe, si no el personal
    SELECT coalesce(correo_institucional, correo_personal)::text
      INTO p_enviado_a
      FROM asistente WHERE id_asistente = v_asistente;

    INSERT INTO clave_acceso (fk_asistente, fk_enlace, clave_hash, enviado_a,
                              es_correo_institucional, expira_en, ip_solicitud)
    VALUES (v_asistente, v_enlace,
            digest(p_clave || p_enviado_a, 'sha256'),   -- RN-34, con sal
            p_enviado_a::citext,
            false,                                       -- lo deriva el disparador
            now() + make_interval(mins => v_vigencia),
            p_ip)
    RETURNING id_clave INTO p_id_clave;
END;
$$;

COMMENT ON PROCEDURE sp_solicitar_clave(text, uuid, inet, bigint, text, text) IS
    'RN-17. La razon de existir de esta clave no es autenticar, es impedir que '
    'uno registre a otro: "yo me puedo registrar por cualquier persona, por eso '
    'tiene que ser con el correo" (1:04:51). La clave en claro se DEVUELVE para '
    'que la aplicacion la envie, y nunca se almacena.';

-- ============================================================================
-- sp_validar_clave_y_registrar · el acto de registrarse
-- ============================================================================
CREATE OR REPLACE PROCEDURE sp_validar_clave_y_registrar(
    p_id_clave          bigint,
    p_clave             text,
    p_ip                inet   DEFAULT NULL,
    p_user_agent        text   DEFAULT NULL,
    INOUT p_id_registro bigint DEFAULT NULL)
LANGUAGE plpgsql
AS $$
DECLARE
    c              record;
    v_max_intentos integer;
    v_sesion       bigint;
    v_canal        varchar(10);
BEGIN
    SELECT * INTO c FROM clave_acceso WHERE id_clave = p_id_clave FOR UPDATE;

    IF c IS NULL THEN
        RAISE EXCEPTION 'No existe la clave %', p_id_clave USING ERRCODE = 'no_data_found';
    END IF;

    -- RN-20 · una clave usada no se reutiliza
    IF c.usado_en IS NOT NULL THEN
        RAISE EXCEPTION 'RN-20: esa clave ya se uso el %', c.usado_en
            USING ERRCODE = 'check_violation';
    END IF;

    IF now() > c.expira_en THEN
        RAISE EXCEPTION 'RN-18: la clave expiro el %', c.expira_en
            USING ERRCODE = 'check_violation';
    END IF;

    v_max_intentos := coalesce((SELECT valor::int FROM parametro WHERE clave = 'CLAVE_MAX_INTENTOS'), 3);

    IF c.clave_hash IS DISTINCT FROM digest(p_clave || c.enviado_a::text, 'sha256') THEN
        UPDATE clave_acceso SET intentos = intentos + 1 WHERE id_clave = p_id_clave;
        IF c.intentos + 1 >= v_max_intentos THEN
            UPDATE clave_acceso SET expira_en = now() WHERE id_clave = p_id_clave;
            RAISE EXCEPTION 'RN-18: se agotaron los % intentos; la clave queda anulada', v_max_intentos
                USING ERRCODE = 'check_violation';
        END IF;
        RAISE EXCEPTION 'Clave incorrecta. Intento % de %', c.intentos + 1, v_max_intentos
            USING ERRCODE = 'check_violation';
    END IF;

    SELECT e.fk_sesion, e.canal INTO v_sesion, v_canal
      FROM enlace_registro e WHERE e.id_enlace = c.fk_enlace;

    -- El disparador de registro hace el resto: ventana, instantaneas y cupo
    INSERT INTO registro_asistencia (fk_sesion, fk_asistente, fk_enlace, fk_clave,
                                     fk_vinculacion_snapshot, origen, ip, user_agent)
    VALUES (v_sesion, c.fk_asistente, c.fk_enlace, p_id_clave,
            NULL, v_canal, p_ip, left(p_user_agent, 300))
    RETURNING id_registro INTO p_id_registro;

    UPDATE clave_acceso SET usado_en = now() WHERE id_clave = p_id_clave;
END;
$$;

-- ============================================================================
-- sp_responder_encuesta · la PARTICIPACION MINIMA DE UNO
--
-- "Una clave foranea garantiza que lo que se inserte exista, no que se
--  inserte algo." Cabecera e items se crean JUNTOS, en una transaccion.
-- ============================================================================
CREATE OR REPLACE PROCEDURE sp_responder_encuesta(
    p_id_registro        bigint,
    p_respuestas         jsonb,
    INOUT p_id_respuesta bigint DEFAULT NULL)
LANGUAGE plpgsql
AS $$
DECLARE
    v_encuesta bigint;
    v_items    integer;
BEGIN
    SELECT s.fk_encuesta INTO v_encuesta
      FROM registro_asistencia r
      JOIN sesion s ON s.id_sesion = r.fk_sesion
     WHERE r.id_registro = p_id_registro;

    IF v_encuesta IS NULL THEN
        RAISE EXCEPTION 'La sesion de ese registro no tiene encuesta asignada'
            USING ERRCODE = 'check_violation';
    END IF;

    IF jsonb_array_length(p_respuestas) = 0 THEN
        RAISE EXCEPTION 'R29: una encuesta respondida debe tener al menos un item'
            USING ERRCODE = 'check_violation';
    END IF;

    INSERT INTO respuesta_encuesta (fk_registro, fk_encuesta)
    VALUES (p_id_registro, v_encuesta)
    RETURNING id_respuesta INTO p_id_respuesta;

    INSERT INTO respuesta_item (fk_respuesta, fk_pregunta, valor_numerico, valor_texto, fk_opcion)
    SELECT p_id_respuesta,
           (e ->> 'pregunta')::bigint,
           (e ->> 'numero')::smallint,
            e ->> 'texto',
           (e ->> 'opcion')::bigint
      FROM jsonb_array_elements(p_respuestas) AS e;

    GET DIAGNOSTICS v_items = ROW_COUNT;

    CALL sp_cerrar_encuesta(p_id_respuesta);
END;
$$;

-- ============================================================================
-- sp_cerrar_encuesta · RN-26, las preguntas OBLIGATORIAS
-- ============================================================================
CREATE OR REPLACE PROCEDURE sp_cerrar_encuesta(p_id_respuesta bigint)
LANGUAGE plpgsql
AS $$
DECLARE
    v_faltan text;
BEGIN
    SELECT string_agg(p.orden::text, ', ' ORDER BY p.orden)
      INTO v_faltan
      FROM respuesta_encuesta re
      JOIN pregunta p ON p.fk_encuesta = re.fk_encuesta AND p.obligatoria
     WHERE re.id_respuesta = p_id_respuesta
       AND NOT EXISTS (SELECT 1 FROM respuesta_item ri
                        WHERE ri.fk_respuesta = re.id_respuesta
                          AND ri.fk_pregunta  = p.id_pregunta);

    IF v_faltan IS NOT NULL THEN
        RAISE EXCEPTION 'RN-26: faltan por responder las preguntas obligatorias %', v_faltan
            USING ERRCODE = 'check_violation';
    END IF;

    UPDATE respuesta_encuesta SET completa = true WHERE id_respuesta = p_id_respuesta;
END;
$$;

COMMENT ON PROCEDURE sp_cerrar_encuesta(bigint) IS
    'RN-26. No es "al menos uno": es "uno por cada pregunta marcada obligatoria", '
    'y eso depende del contenido de otra tabla que ademas cambia con cada version '
    'de la encuesta. Ninguna restriccion declarativa puede expresarlo.';

-- ============================================================================
-- fn_exportar_asis · RN-27 y RN-28, el archivo plano de TRES columnas
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_exportar_asis(p_id_sesion bigint)
RETURNS TABLE (reunion smallint, id_asis varchar(15), programa varchar(5))
LANGUAGE sql STABLE
AS $$
    SELECT s.numero_reunion, a.id_asis, r.fk_programa_snapshot
      FROM registro_asistencia r
      JOIN sesion    s ON s.id_sesion    = r.fk_sesion
      JOIN asistente a ON a.id_asistente = r.fk_asistente
     WHERE r.fk_sesion = p_id_sesion
       -- RN-28 · solo se migra quien tiene ID y programa
       AND a.id_asis IS NOT NULL
       AND r.fk_programa_snapshot IS NOT NULL
       -- RN-08 · el externo se cuenta, pero NUNCA entra al archivo
       AND a.es_externo = false
     ORDER BY a.id_asis;
$$;

COMMENT ON FUNCTION fn_exportar_asis(bigint) IS
    'RN-27. TRES columnas exactas: reunion, ID y codigo de programa - "cuando '
    'tenemos el archivo plano, son 3" (32:34). Ni una mas. El manual insiste: '
    '"unicamente haya informacion en las tres columnas correspondientes".';

-- ============================================================================
-- sp_generar_lote_migracion · con su detalle, que tampoco puede ir vacio
-- ============================================================================
CREATE OR REPLACE PROCEDURE sp_generar_lote_migracion(
    p_id_sesion  bigint,
    p_usuario    bigint DEFAULT NULL,
    INOUT p_id_lote bigint DEFAULT NULL)
LANGUAGE plpgsql
AS $$
DECLARE
    v_filas integer;
    v_nombre text;
BEGIN
    SELECT count(*) INTO v_filas FROM fn_exportar_asis(p_id_sesion);

    IF v_filas = 0 THEN
        RAISE EXCEPTION
            'No hay registros migrables en la sesion %. Revise I10: asistentes sin ID o sin programa',
            p_id_sesion USING ERRCODE = 'check_violation';
    END IF;

    SELECT 'ME_CATEDRA_' || c.id_evento_asis || '_R' || s.numero_reunion || '.xlsx'
      INTO v_nombre
      FROM sesion s JOIN catedra c ON c.id_catedra = s.fk_catedra
     WHERE s.id_sesion = p_id_sesion;

    INSERT INTO lote_migracion (fk_sesion, nombre_archivo, fk_usuario,
                                fk_estado_proceso, total_filas)
    VALUES (p_id_sesion, v_nombre, p_usuario, 'GENERADO', v_filas)
    RETURNING id_lote_migracion INTO p_id_lote;

    INSERT INTO detalle_migracion (fk_lote_migracion, fk_registro, id_asis_enviado,
                                   programa_enviado, reunion_enviada)
    SELECT p_id_lote, r.id_registro, a.id_asis, r.fk_programa_snapshot, s.numero_reunion
      FROM registro_asistencia r
      JOIN sesion    s ON s.id_sesion    = r.fk_sesion
      JOIN asistente a ON a.id_asistente = r.fk_asistente
     WHERE r.fk_sesion = p_id_sesion
       AND a.id_asis IS NOT NULL
       AND r.fk_programa_snapshot IS NOT NULL
       AND a.es_externo = false;

    UPDATE sesion SET estado = 'MIGRADA' WHERE id_sesion = p_id_sesion;
END;
$$;

\echo '11 · Funciones y procedimientos creados - 4 funciones, 6 procedimientos'
