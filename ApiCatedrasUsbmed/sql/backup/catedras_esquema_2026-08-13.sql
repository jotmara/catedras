--
-- PostgreSQL database dump
--

\restrict iGIrEm2C6ihU2OQ4NKmBXjq43hqZ6dtgKdGH96L7lHkrgZKqIVandbpXbP5pLhS

-- Dumped from database version 17.6
-- Dumped by pg_dump version 18.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: catedras; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA catedras;


--
-- Name: SCHEMA catedras; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA catedras IS 'Todos los objetos del sistema. Se usa un esquema propio y no public para poder revocar permisos sobre public sin afectar al proyecto.';


--
-- Name: btree_gist; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS btree_gist WITH SCHEMA public;


--
-- Name: EXTENSION btree_gist; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION btree_gist IS 'support for indexing common datatypes in GiST';


--
-- Name: citext; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS citext WITH SCHEMA public;


--
-- Name: EXTENSION citext; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION citext IS 'data type for case-insensitive character strings';


--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: unaccent; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS unaccent WITH SCHEMA public;


--
-- Name: EXTENSION unaccent; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION unaccent IS 'text search dictionary that removes accents';


--
-- Name: fn_emitir_enlace_api(bigint, integer, integer, bigint); Type: FUNCTION; Schema: catedras; Owner: -
--

CREATE FUNCTION catedras.fn_emitir_enlace_api(p_id_sesion bigint, p_minutos_antes integer DEFAULT NULL::integer, p_minutos_despues integer DEFAULT NULL::integer, p_usuario bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
    AS $$
DECLARE
    v_enlace bigint;
BEGIN
    CALL catedras.sp_emitir_enlace(p_id_sesion, p_minutos_antes, p_minutos_despues, p_usuario, v_enlace);
    RETURN v_enlace;
END;
$$;


--
-- Name: fn_exportar_asis(bigint); Type: FUNCTION; Schema: catedras; Owner: -
--

CREATE FUNCTION catedras.fn_exportar_asis(p_id_sesion bigint) RETURNS TABLE(reunion smallint, id_asis character varying, programa character varying)
    LANGUAGE sql STABLE
    SET search_path TO 'catedras', 'public'
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


--
-- Name: FUNCTION fn_exportar_asis(p_id_sesion bigint); Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON FUNCTION catedras.fn_exportar_asis(p_id_sesion bigint) IS 'RN-27. TRES columnas exactas: reunion, ID y codigo de programa - "cuando tenemos el archivo plano, son 3" (32:34). Ni una mas. El manual insiste: "unicamente haya informacion en las tres columnas correspondientes".';


--
-- Name: fn_generar_lote_api(bigint, bigint); Type: FUNCTION; Schema: catedras; Owner: -
--

CREATE FUNCTION catedras.fn_generar_lote_api(p_id_sesion bigint, p_usuario bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
    AS $$
DECLARE
    v_lote bigint;
BEGIN
    CALL catedras.sp_generar_lote_migracion(p_id_sesion, p_usuario, v_lote);
    RETURN v_lote;
END;
$$;


--
-- Name: fn_normalizar(text); Type: FUNCTION; Schema: catedras; Owner: -
--

CREATE FUNCTION catedras.fn_normalizar(p_texto text) RETURNS text
    LANGUAGE sql IMMUTABLE PARALLEL SAFE
    SET search_path TO 'catedras', 'public'
    AS $$
    SELECT lower(trim(regexp_replace(
               public.unaccent('public.unaccent', coalesce(p_texto, '')),
               '\s+', ' ', 'g')));
$$;


--
-- Name: FUNCTION fn_normalizar(p_texto text); Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON FUNCTION catedras.fn_normalizar(p_texto text) IS 'Baja a minusculas, quita tildes y colapsa espacios. Es la funcion con que se compara el texto libre de los formularios contra alias_programa. Es IMMUTABLE a proposito: si no, no se puede construir el indice GIN.';


--
-- Name: fn_resolver_asistente(text); Type: FUNCTION; Schema: catedras; Owner: -
--

CREATE FUNCTION catedras.fn_resolver_asistente(p_identificador text) RETURNS bigint
    LANGUAGE plpgsql STABLE
    SET search_path TO 'catedras', 'public'
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


--
-- Name: FUNCTION fn_resolver_asistente(p_identificador text); Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON FUNCTION catedras.fn_resolver_asistente(p_identificador text) IS 'RN-06. Busca por las tres vias y devuelve el asistente, o NULL. Busca en documentos VIGENTES Y NO VIGENTES a proposito: los 707 casos de personas con varios documentos son justamente quienes digitan el antiguo. Elimina el trabajo manual que describio el profesor Hugo Nelson en 42:01.';


--
-- Name: fn_resolver_programa(text, real); Type: FUNCTION; Schema: catedras; Owner: -
--

CREATE FUNCTION catedras.fn_resolver_programa(p_texto text, p_umbral real DEFAULT 0.45) RETURNS character varying
    LANGUAGE plpgsql STABLE
    SET search_path TO 'catedras', 'public'
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


--
-- Name: FUNCTION fn_resolver_programa(p_texto text, p_umbral real); Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON FUNCTION catedras.fn_resolver_programa(p_texto text, p_umbral real) IS 'Resuelve el texto libre del formulario contra el catalogo. Cuatro pasos, del mas seguro al mas arriesgado. El paso 4 puede equivocarse: por eso devuelve NULL antes que adivinar por debajo del umbral, y lo que quede sin resolver se cuenta y se revisa a mano.';


--
-- Name: fn_responder_encuesta_api(bigint, jsonb); Type: FUNCTION; Schema: catedras; Owner: -
--

CREATE FUNCTION catedras.fn_responder_encuesta_api(p_id_registro bigint, p_respuestas jsonb) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
    AS $$
DECLARE
    v_respuesta bigint;
BEGIN
    CALL catedras.sp_responder_encuesta(p_id_registro, p_respuestas, v_respuesta);
    RETURN v_respuesta;
END;
$$;


--
-- Name: fn_siguiente_reunion(character); Type: FUNCTION; Schema: catedras; Owner: -
--

CREATE FUNCTION catedras.fn_siguiente_reunion(p_id_evento_asis character) RETURNS smallint
    LANGUAGE sql STABLE
    SET search_path TO 'catedras', 'public'
    AS $$
    SELECT coalesce(max(s.numero_reunion), 0)::smallint + 1
      FROM catedra c
      LEFT JOIN sesion s ON s.fk_catedra = c.id_catedra
     WHERE c.id_evento_asis = p_id_evento_asis;
$$;


--
-- Name: FUNCTION fn_siguiente_reunion(p_id_evento_asis character); Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON FUNCTION catedras.fn_siguiente_reunion(p_id_evento_asis character) IS 'I8. Sustituye el paso 2 del manual de migracion: la busqueda manual de la ultima reunion en un listado de 5.711 filas.';


--
-- Name: fn_solicitar_clave_api(text, uuid, inet); Type: FUNCTION; Schema: catedras; Owner: -
--

CREATE FUNCTION catedras.fn_solicitar_clave_api(p_identificador text, p_token uuid, p_ip inet DEFAULT NULL::inet) RETURNS TABLE(id_clave bigint, clave text, enviado_a text)
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
    AS $$
DECLARE
    v_id     bigint;
    v_clave  text;
    v_correo text;
BEGIN
    CALL catedras.sp_solicitar_clave(p_identificador, p_token, p_ip, v_id, v_clave, v_correo);
    RETURN QUERY SELECT v_id, v_clave, v_correo;
END;
$$;


--
-- Name: FUNCTION fn_solicitar_clave_api(p_identificador text, p_token uuid, p_ip inet); Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON FUNCTION catedras.fn_solicitar_clave_api(p_identificador text, p_token uuid, p_ip inet) IS 'Envoltorio de sp_solicitar_clave para la API. RN-17.';


--
-- Name: fn_trg_bitacora(); Type: FUNCTION; Schema: catedras; Owner: -
--

CREATE FUNCTION catedras.fn_trg_bitacora() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
    AS $$
DECLARE
    v_antes   jsonb;
    v_despues jsonb;
    v_llave   text;
BEGIN
    -- Se convierte a jsonb PRIMERO y la llave se extrae de ahi.
    -- No se usa CASE sobre NEW.<columna> porque PL/pgSQL planifica la
    -- expresion COMPLETA contra el tipo de registro que dispara: una rama
    -- que nombre una columna de otra tabla revienta aunque no se ejecute.
    IF TG_OP IN ('UPDATE', 'DELETE') THEN v_antes   := to_jsonb(OLD); END IF;
    IF TG_OP IN ('INSERT', 'UPDATE') THEN v_despues := to_jsonb(NEW); END IF;

    v_llave := coalesce(v_despues, v_antes) ->> ('id_' || replace(TG_TABLE_NAME, '_asistencia', ''));

    INSERT INTO bitacora (nombre_tabla, operacion, llave, datos_antes, datos_despues)
    VALUES (TG_TABLE_NAME, TG_OP, v_llave, v_antes, v_despues);

    RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END;
$$;


--
-- Name: fn_trg_clave_derivar(); Type: FUNCTION; Schema: catedras; Owner: -
--

CREATE FUNCTION catedras.fn_trg_clave_derivar() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
    AS $$
DECLARE
    v_dominios text;
BEGIN
    SELECT valor INTO v_dominios
      FROM parametro WHERE clave = 'DOMINIOS_INSTITUCIONALES';

    v_dominios := coalesce(v_dominios, 'usbmed.edu.co,usb.edu.co');

    NEW.es_correo_institucional := EXISTS (
        SELECT 1
          FROM unnest(string_to_array(v_dominios, ',')) AS d(dom)
         WHERE lower(NEW.enviado_a::text) LIKE '%@' || lower(trim(d.dom))
    );
    RETURN NEW;
END;
$$;


--
-- Name: fn_trg_enlace_canal(); Type: FUNCTION; Schema: catedras; Owner: -
--

CREATE FUNCTION catedras.fn_trg_enlace_canal() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
    AS $$
DECLARE
    v_canal_esperado varchar(10);
BEGIN
    SELECT m.canal_difusion
      INTO v_canal_esperado
      FROM sesion s
      JOIN modalidad m ON m.id_modalidad = s.fk_modalidad
     WHERE s.id_sesion = NEW.fk_sesion;

    IF v_canal_esperado IS DISTINCT FROM 'AMBOS'
       AND NEW.canal IS DISTINCT FROM v_canal_esperado THEN
        RAISE EXCEPTION
            'RN-13: la sesion % es de modalidad que se difunde por %, no por %',
            NEW.fk_sesion, v_canal_esperado, NEW.canal
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END;
$$;


--
-- Name: fn_trg_registro_validar(); Type: FUNCTION; Schema: catedras; Owner: -
--

CREATE FUNCTION catedras.fn_trg_registro_validar() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
    AS $$
DECLARE
    v_ventana        tstzrange;
    v_revocado       timestamptz;
    v_cupo           integer;
    v_registrados    integer;
    v_exige_programa boolean;
BEGIN
    ------------------------------------------------------------------ RN-15 --
    IF NEW.fk_enlace IS NOT NULL AND NEW.origen NOT IN ('MANUAL', 'IMPORTADO') THEN
        SELECT e.ventana, e.revocado_en
          INTO v_ventana, v_revocado
          FROM enlace_registro e
         WHERE e.id_enlace = NEW.fk_enlace;

        IF v_revocado IS NOT NULL THEN
            RAISE EXCEPTION 'RN-15: el enlace % esta revocado', NEW.fk_enlace
                USING ERRCODE = 'check_violation';
        END IF;

        IF NOT (v_ventana @> NEW.registrado_en) THEN
            RAISE EXCEPTION
                'RN-15: % esta fuera de la ventana % del enlace %',
                NEW.registrado_en, v_ventana, NEW.fk_enlace
                USING ERRCODE = 'check_violation';
        END IF;
    END IF;

    ------------------------------------------------------------------ RN-22 --
    -- Instantanea de la VINCULACION vigente
    IF NEW.fk_vinculacion_snapshot IS NULL THEN
        SELECT v.fk_tipo_vinculacion
          INTO NEW.fk_vinculacion_snapshot
          FROM vinculacion_asistente v
         WHERE v.fk_asistente = NEW.fk_asistente
           AND v.fecha_fin IS NULL
         ORDER BY v.fecha_ini DESC
         LIMIT 1;

        IF NEW.fk_vinculacion_snapshot IS NULL THEN
            RAISE EXCEPTION
                'El asistente % no tiene ninguna vinculacion vigente',
                NEW.fk_asistente USING ERRCODE = 'check_violation';
        END IF;
    END IF;

    SELECT tv.exige_programa INTO v_exige_programa
      FROM tipo_vinculacion tv
     WHERE tv.id_tipo_vinculacion = NEW.fk_vinculacion_snapshot;

    -- Instantanea del PROGRAMA vigente, solo si la vinculacion lo exige
    IF NEW.fk_programa_snapshot IS NULL AND v_exige_programa THEN
        SELECT pa.fk_programa
          INTO NEW.fk_programa_snapshot
          FROM programa_asistente pa
          JOIN periodo_academico p ON p.id_periodo = pa.fk_periodo
         WHERE pa.fk_asistente = NEW.fk_asistente
           AND pa.estado = 'ACTIVO'
         ORDER BY p.fecha_ini DESC
         LIMIT 1;
    END IF;

    ------------------------------------------------------------------ RN-07 --
    IF v_exige_programa AND NEW.fk_programa_snapshot IS NULL THEN
        RAISE EXCEPTION
            'RN-07: la vinculacion % exige programa academico y el asistente % no tiene ninguno activo',
            NEW.fk_vinculacion_snapshot, NEW.fk_asistente
            USING ERRCODE = 'check_violation';
    END IF;

    IF NOT v_exige_programa THEN
        -- Rutas de Paz y similares entran SIN programa, a proposito
        NEW.fk_programa_snapshot := NULL;
    END IF;

    ------------------------------------------------------------------ RN-38 --
    SELECT s.cupo INTO v_cupo FROM sesion s WHERE s.id_sesion = NEW.fk_sesion FOR UPDATE;

    IF v_cupo IS NOT NULL THEN
        SELECT count(*) INTO v_registrados
          FROM registro_asistencia r WHERE r.fk_sesion = NEW.fk_sesion;

        IF v_registrados >= v_cupo THEN
            RAISE EXCEPTION 'RN-38: la sesion % alcanzo su cupo de %',
                NEW.fk_sesion, v_cupo USING ERRCODE = 'check_violation';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;


--
-- Name: FUNCTION fn_trg_registro_validar(); Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON FUNCTION catedras.fn_trg_registro_validar() IS 'Cuatro reglas en un disparador porque las cuatro se comprueban en el mismo instante y sobre la misma fila. El FOR UPDATE sobre la sesion serializa el control de cupo: sin el, dos registros simultaneos podrian pasarse.';


--
-- Name: fn_trg_respuesta_item_tipo(); Type: FUNCTION; Schema: catedras; Owner: -
--

CREATE FUNCTION catedras.fn_trg_respuesta_item_tipo() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
    AS $$
DECLARE
    t record;
BEGIN
    SELECT tp.id_tipo_pregunta, tp.guarda_numero, tp.guarda_texto, tp.guarda_opcion,
           p.valor_min, p.valor_max
      INTO t
      FROM pregunta p
      JOIN tipo_pregunta tp ON tp.id_tipo_pregunta = p.fk_tipo_pregunta
     WHERE p.id_pregunta = NEW.fk_pregunta;

    IF t.guarda_numero AND NEW.valor_numerico IS NULL THEN
        RAISE EXCEPTION 'RN-25: la pregunta % es de tipo % y espera valor_numerico',
            NEW.fk_pregunta, t.id_tipo_pregunta USING ERRCODE = 'check_violation';
    ELSIF t.guarda_texto AND NEW.valor_texto IS NULL THEN
        RAISE EXCEPTION 'RN-25: la pregunta % es de tipo % y espera valor_texto',
            NEW.fk_pregunta, t.id_tipo_pregunta USING ERRCODE = 'check_violation';
    ELSIF t.guarda_opcion AND NEW.fk_opcion IS NULL THEN
        RAISE EXCEPTION 'RN-25: la pregunta % es de tipo % y espera fk_opcion',
            NEW.fk_pregunta, t.id_tipo_pregunta USING ERRCODE = 'check_violation';
    END IF;

    -- El rango declarado de la pregunta
    IF NEW.valor_numerico IS NOT NULL AND t.valor_min IS NOT NULL
       AND NEW.valor_numerico NOT BETWEEN t.valor_min AND t.valor_max THEN
        RAISE EXCEPTION 'RN-25: % esta fuera del rango [%, %] de la pregunta %',
            NEW.valor_numerico, t.valor_min, t.valor_max, NEW.fk_pregunta
            USING ERRCODE = 'check_violation';
    END IF;

    -- RN-24 · la opcion elegida pertenece a ESA pregunta
    IF NEW.fk_opcion IS NOT NULL
       AND NOT EXISTS (SELECT 1 FROM opcion_pregunta o
                        WHERE o.id_opcion = NEW.fk_opcion
                          AND o.fk_pregunta = NEW.fk_pregunta) THEN
        RAISE EXCEPTION 'RN-24: la opcion % no pertenece a la pregunta %',
            NEW.fk_opcion, NEW.fk_pregunta USING ERRCODE = 'check_violation';
    END IF;

    RETURN NEW;
END;
$$;


--
-- Name: fn_trg_sesion_consecutivo(); Type: FUNCTION; Schema: catedras; Owner: -
--

CREATE FUNCTION catedras.fn_trg_sesion_consecutivo() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
    AS $$
BEGIN
    IF NEW.numero_reunion IS NULL OR NEW.numero_reunion = 0 THEN
        -- El bloqueo de la catedra serializa dos altas simultaneas
        PERFORM 1 FROM catedra WHERE id_catedra = NEW.fk_catedra FOR UPDATE;

        SELECT coalesce(max(s.numero_reunion), 0) + 1
          INTO NEW.numero_reunion
          FROM sesion s
         WHERE s.fk_catedra = NEW.fk_catedra;
    END IF;
    RETURN NEW;
END;
$$;


--
-- Name: FUNCTION fn_trg_sesion_consecutivo(); Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON FUNCTION catedras.fn_trg_sesion_consecutivo() IS 'RN-10. PROPONE el siguiente consecutivo de la catedra cuando no se indica. El FOR UPDATE serializa dos altas simultaneas: sin el, uq_sesion_reunion rechazaria una de las dos con un error feo en vez de ordenarlas. NO sustituye al numero del ASIS: para las catedras que ya existen alli, la autoridad es numero_reunion_asis. Ver el comentario de arriba y §8.3.';


--
-- Name: fn_validar_clave_api(bigint, text, inet, text); Type: FUNCTION; Schema: catedras; Owner: -
--

CREATE FUNCTION catedras.fn_validar_clave_api(p_id_clave bigint, p_clave text, p_ip inet DEFAULT NULL::inet, p_user_agent text DEFAULT NULL::text) RETURNS bigint
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
    AS $$
DECLARE
    v_registro bigint;
BEGIN
    CALL catedras.sp_validar_clave_y_registrar(p_id_clave, p_clave, p_ip, p_user_agent, v_registro);
    RETURN v_registro;
END;
$$;


--
-- Name: sp_cerrar_encuesta(bigint); Type: PROCEDURE; Schema: catedras; Owner: -
--

CREATE PROCEDURE catedras.sp_cerrar_encuesta(IN p_id_respuesta bigint)
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
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


--
-- Name: PROCEDURE sp_cerrar_encuesta(IN p_id_respuesta bigint); Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON PROCEDURE catedras.sp_cerrar_encuesta(IN p_id_respuesta bigint) IS 'RN-26. No es "al menos uno": es "uno por cada pregunta marcada obligatoria", y eso depende del contenido de otra tabla que ademas cambia con cada version de la encuesta. Ninguna restriccion declarativa puede expresarlo.';


--
-- Name: sp_emitir_enlace(bigint, integer, integer, bigint, bigint); Type: PROCEDURE; Schema: catedras; Owner: -
--

CREATE PROCEDURE catedras.sp_emitir_enlace(IN p_id_sesion bigint, IN p_minutos_antes integer DEFAULT NULL::integer, IN p_minutos_despues integer DEFAULT NULL::integer, IN p_usuario bigint DEFAULT NULL::bigint, INOUT p_id_enlace bigint DEFAULT NULL::bigint)
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
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


--
-- Name: PROCEDURE sp_emitir_enlace(IN p_id_sesion bigint, IN p_minutos_antes integer, IN p_minutos_despues integer, IN p_usuario bigint, INOUT p_id_enlace bigint); Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON PROCEDURE catedras.sp_emitir_enlace(IN p_id_sesion bigint, IN p_minutos_antes integer, IN p_minutos_despues integer, IN p_usuario bigint, INOUT p_id_enlace bigint) IS 'El boton del .docx: "el administrador toca un boton y genera el QR y URL del registro de la catedra especifica". La ventana sale de los parametros, que es lo que pide "el administrador configura hora de inicio y hora de fin".';


--
-- Name: sp_generar_lote_migracion(bigint, bigint, bigint); Type: PROCEDURE; Schema: catedras; Owner: -
--

CREATE PROCEDURE catedras.sp_generar_lote_migracion(IN p_id_sesion bigint, IN p_usuario bigint DEFAULT NULL::bigint, INOUT p_id_lote bigint DEFAULT NULL::bigint)
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
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


--
-- Name: sp_responder_encuesta(bigint, jsonb, bigint); Type: PROCEDURE; Schema: catedras; Owner: -
--

CREATE PROCEDURE catedras.sp_responder_encuesta(IN p_id_registro bigint, IN p_respuestas jsonb, INOUT p_id_respuesta bigint DEFAULT NULL::bigint)
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
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


--
-- Name: sp_solicitar_clave(text, uuid, inet, bigint, text, text); Type: PROCEDURE; Schema: catedras; Owner: -
--

CREATE PROCEDURE catedras.sp_solicitar_clave(IN p_identificador text, IN p_token uuid, IN p_ip inet DEFAULT NULL::inet, INOUT p_id_clave bigint DEFAULT NULL::bigint, INOUT p_clave text DEFAULT NULL::text, INOUT p_enviado_a text DEFAULT NULL::text)
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
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


--
-- Name: PROCEDURE sp_solicitar_clave(IN p_identificador text, IN p_token uuid, IN p_ip inet, INOUT p_id_clave bigint, INOUT p_clave text, INOUT p_enviado_a text); Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON PROCEDURE catedras.sp_solicitar_clave(IN p_identificador text, IN p_token uuid, IN p_ip inet, INOUT p_id_clave bigint, INOUT p_clave text, INOUT p_enviado_a text) IS 'RN-17. La razon de existir de esta clave no es autenticar, es impedir que uno registre a otro: "yo me puedo registrar por cualquier persona, por eso tiene que ser con el correo" (1:04:51). La clave en claro se DEVUELVE para que la aplicacion la envie, y nunca se almacena.';


--
-- Name: sp_validar_clave_y_registrar(bigint, text, inet, text, bigint); Type: PROCEDURE; Schema: catedras; Owner: -
--

CREATE PROCEDURE catedras.sp_validar_clave_y_registrar(IN p_id_clave bigint, IN p_clave text, IN p_ip inet DEFAULT NULL::inet, IN p_user_agent text DEFAULT NULL::text, INOUT p_id_registro bigint DEFAULT NULL::bigint)
    LANGUAGE plpgsql
    SET search_path TO 'catedras', 'public'
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


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alias_programa; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.alias_programa (
    id_alias bigint NOT NULL,
    texto_normalizado character varying(200) NOT NULL,
    fk_programa character varying(5) NOT NULL,
    origen character varying(30) DEFAULT 'FORMULARIO'::character varying NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: TABLE alias_programa; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.alias_programa IS 'Texto libre con que se ha escrito un programa, y el codigo al que corresponde. Nace de la calidad real del formulario actual, que trae "Psicologica", "Entrenamiento Deportivo.", "Ingenieria de datos y software" y una celda con la facultad y el programa en dos lineas. Es una tabla VIVA porque los formularios en texto libre van a seguir llegando durante toda la transicion.';


--
-- Name: alias_programa_id_alias_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.alias_programa ALTER COLUMN id_alias ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.alias_programa_id_alias_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: asistente; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.asistente (
    id_asistente bigint NOT NULL,
    id_asis character varying(15),
    nombres character varying(100) NOT NULL,
    apellidos character varying(100) NOT NULL,
    nombre_completo_asis character varying(200),
    correo_institucional public.citext,
    correo_personal public.citext,
    celular character varying(20),
    es_externo boolean DEFAULT false NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    fk_lote_carga bigint,
    CONSTRAINT chk_asistente_cor_inst_fmt CHECK (((correo_institucional IS NULL) OR (correo_institucional OPERATOR(public.~~) '%@%.%'::public.citext))),
    CONSTRAINT chk_asistente_cor_pers_fmt CHECK (((correo_personal IS NULL) OR (correo_personal OPERATOR(public.~~) '%@%.%'::public.citext))),
    CONSTRAINT chk_asistente_correo CHECK (((correo_institucional IS NOT NULL) OR (correo_personal IS NOT NULL))),
    CONSTRAINT chk_asistente_externo CHECK ((((es_externo = false) AND (id_asis IS NOT NULL)) OR (es_externo = true))),
    CONSTRAINT chk_asistente_idasis CHECK (((id_asis IS NULL) OR ((id_asis)::text ~ '^[0-9A-Za-z]{5,15}$'::text)))
);


--
-- Name: TABLE asistente; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.asistente IS 'Persona que asiste a las catedras abiertas, de forma presencial o virtual. Puede ser estudiante, docente, administrativo, egresado, participante de rutas de formacion o publico externo.';


--
-- Name: COLUMN asistente.id_asis; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.asistente.id_asis IS 'Codigo de identificacion en el sistema ASIS. CORREGIDO respecto del archivo original: es ALFANUMERICO de hasta 15 caracteres, no 10 digitos. El maestro real trae 9.553 filas de 11 caracteres y valores como 1000513C. NULO significa que es un externo que no esta en el ASIS - decision REVISABLE, ver §3.1 del plan.';


--
-- Name: COLUMN asistente.nombre_completo_asis; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.asistente.nombre_completo_asis IS 'El nombre tal como llego del ASIS, sin transformar. Permite rehacer la particion en nombres y apellidos si resulta equivocada.';


--
-- Name: COLUMN asistente.correo_personal; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.asistente.correo_personal IS 'No es un caso raro: los participantes de Rutas de Paz NO tienen correo institucional, y es su unica via para recibir la clave.';


--
-- Name: asistente_id_asistente_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.asistente ALTER COLUMN id_asistente ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.asistente_id_asistente_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: bitacora; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.bitacora (
    id_bitacora bigint NOT NULL,
    ocurrido_en timestamp with time zone DEFAULT now() NOT NULL,
    usuario_bd name DEFAULT CURRENT_USER NOT NULL,
    fk_usuario bigint,
    nombre_tabla character varying(63) NOT NULL,
    operacion character varying(10) NOT NULL,
    llave character varying(100),
    datos_antes jsonb,
    datos_despues jsonb,
    CONSTRAINT chk_bitacora_operacion CHECK (((operacion)::text = ANY ((ARRAY['INSERT'::character varying, 'UPDATE'::character varying, 'DELETE'::character varying])::text[])))
);


--
-- Name: TABLE bitacora; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.bitacora IS 'RN-35 · Registro de toda modificacion sobre datos sensibles, con el antes y el despues en jsonb. La alternativa - una tabla espejo por cada tabla auditada - costaria treinta y siete tablas mas.';


--
-- Name: bitacora_id_bitacora_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.bitacora ALTER COLUMN id_bitacora ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.bitacora_id_bitacora_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: catedra; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.catedra (
    id_catedra bigint NOT NULL,
    id_evento_asis character(9) NOT NULL,
    nombre character varying(200) NOT NULL,
    nombre_asis character varying(30) GENERATED ALWAYS AS ("left"((nombre)::text, 30)) STORED,
    fk_tipo_evento character(4) NOT NULL,
    fk_dependencia character varying(15),
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_catedra_asis CHECK ((id_evento_asis ~ '^[0-9]{9}$'::text))
);


--
-- Name: COLUMN catedra.id_evento_asis; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.catedra.id_evento_asis IS 'Identificador del evento en el ASIS. char(9) CON CEROS A LA IZQUIERDA: 000035392. Como entero se convierte en 35392 y deja de servir para la carga.';


--
-- Name: COLUMN catedra.nombre_asis; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.catedra.nombre_asis IS 'DERIVADO: los 30 primeros caracteres, que es lo que acepta el ASIS. El listado real trae nombres cortados a mitad de palabra - "REMOCION DE METALES PESADOS DE", "CURSO FORMATIVO LOGICO MATEMAT". Guardando el largo y derivando el corto, no se pierde informacion. Al reves, si.';


--
-- Name: catedra_id_catedra_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.catedra ALTER COLUMN id_catedra ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.catedra_id_catedra_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: clave_acceso; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.clave_acceso (
    id_clave bigint NOT NULL,
    fk_asistente bigint NOT NULL,
    fk_enlace bigint NOT NULL,
    clave_hash bytea NOT NULL,
    enviado_a public.citext NOT NULL,
    es_correo_institucional boolean NOT NULL,
    generado_en timestamp with time zone DEFAULT now() NOT NULL,
    expira_en timestamp with time zone NOT NULL,
    usado_en timestamp with time zone,
    intentos smallint DEFAULT 0 NOT NULL,
    ip_solicitud inet,
    CONSTRAINT chk_clave_correo CHECK ((enviado_a OPERATOR(public.~~) '%@%.%'::public.citext)),
    CONSTRAINT chk_clave_expira CHECK ((expira_en > generado_en)),
    CONSTRAINT chk_clave_intentos CHECK (((intentos >= 0) AND (intentos <= 10))),
    CONSTRAINT chk_clave_usada CHECK (((usado_en IS NULL) OR ((usado_en >= generado_en) AND (usado_en <= expira_en))))
);


--
-- Name: COLUMN clave_acceso.clave_hash; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.clave_acceso.clave_hash IS 'RN-34 · La clave CIFRADA. Nunca se guarda en claro. Se calcula con digest() de pgcrypto en el procedimiento sp_solicitar_clave.';


--
-- Name: COLUMN clave_acceso.es_correo_institucional; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.clave_acceso.es_correo_institucional IS 'DERIVADO del dominio de enviado_a por el disparador del script 10. Es la columna que responde al asunto que el profesor Carlos Castro dejo abierto en 55:32: "a mi no me gusta el correo que no sea institucional; dejame, yo lo resuelvo". El modelo deja el dato listo y medible (I18) para que la politica se decida con la evidencia a la vista.';


--
-- Name: clave_acceso_id_clave_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.clave_acceso ALTER COLUMN id_clave ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.clave_acceso_id_clave_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: consentimiento_datos; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.consentimiento_datos (
    id_consentimiento bigint NOT NULL,
    fk_asistente bigint NOT NULL,
    version_politica character varying(20) NOT NULL,
    aceptado_en timestamp with time zone DEFAULT now() NOT NULL,
    ip inet,
    canal character varying(20) DEFAULT 'WEB'::character varying NOT NULL,
    CONSTRAINT chk_consentimiento_canal CHECK (((canal)::text = ANY ((ARRAY['WEB'::character varying, 'PRESENCIAL'::character varying, 'CORREO'::character varying, 'IMPORTADO'::character varying])::text[])))
);


--
-- Name: TABLE consentimiento_datos; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.consentimiento_datos IS 'Ley 1581 de 2012. El sistema guarda documentos, nombres y correos personales de externos: el consentimiento es un HECHO que se registra, no un aviso en la pantalla.';


--
-- Name: consentimiento_datos_id_consentimiento_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.consentimiento_datos ALTER COLUMN id_consentimiento ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.consentimiento_datos_id_consentimiento_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dependencia; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.dependencia (
    id_dependencia character varying(15) NOT NULL,
    nombre character varying(120) NOT NULL,
    fk_dependencia_padre character varying(15),
    activo boolean DEFAULT true NOT NULL,
    CONSTRAINT chk_dependencia_padre CHECK (((fk_dependencia_padre)::text <> (id_dependencia)::text))
);


--
-- Name: detalle_migracion; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.detalle_migracion (
    id_detalle bigint NOT NULL,
    fk_lote_migracion bigint NOT NULL,
    fk_registro bigint NOT NULL,
    id_asis_enviado character varying(15) NOT NULL,
    programa_enviado character varying(5),
    reunion_enviada smallint NOT NULL,
    resultado character varying(12) DEFAULT 'PENDIENTE'::character varying NOT NULL,
    mensaje character varying(300),
    CONSTRAINT chk_detalle_resultado CHECK (((resultado)::text = ANY ((ARRAY['PENDIENTE'::character varying, 'ACEPTADO'::character varying, 'RECHAZADO'::character varying])::text[])))
);


--
-- Name: TABLE detalle_migracion; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.detalle_migracion IS 'Cada fila enviada en un lote, TAL COMO SE ENVIO, y el resultado que dio.';


--
-- Name: COLUMN detalle_migracion.id_asis_enviado; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.detalle_migracion.id_asis_enviado IS 'COPIA LITERAL del ID que salio en el archivo. Se repite a proposito una columna que ya esta en asistente: NO SON LO MISMO. Si el dato de origen cambia despues del envio, la tabla dira una cosa y el ASIS tendra otra, y sin esta copia un rechazo es indepurable seis meses despues.';


--
-- Name: COLUMN detalle_migracion.programa_enviado; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.detalle_migracion.programa_enviado IS 'COPIA LITERAL del codigo de programa. NULO solo es legitimo si la vinculacion no exigia programa - y en ese caso el registro no deberia haber entrado al lote (RN-28).';


--
-- Name: detalle_migracion_id_detalle_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.detalle_migracion ALTER COLUMN id_detalle ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.detalle_migracion_id_detalle_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: documento_asistente; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.documento_asistente (
    id_documento bigint NOT NULL,
    fk_asistente bigint NOT NULL,
    fk_tipo_documento character varying(5) NOT NULL,
    numero character varying(20) NOT NULL,
    vigente boolean DEFAULT true NOT NULL,
    registrado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_documento_numero CHECK (((numero)::text ~ '^[0-9A-Za-z-]{4,20}$'::text))
);


--
-- Name: TABLE documento_asistente; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.documento_asistente IS 'Numero de documento asociado a un asistente. Una persona puede tener varios a lo largo del tiempo; solo uno esta vigente (RN-05, indice parcial en el script 09). Sirve para resolver el ID cuando la persona no lo recuerda y digita la cedula.';


--
-- Name: documento_asistente_id_documento_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.documento_asistente ALTER COLUMN id_documento ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.documento_asistente_id_documento_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: encuesta; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.encuesta (
    id_encuesta bigint NOT NULL,
    nombre character varying(120) NOT NULL,
    version smallint DEFAULT 1 NOT NULL,
    vigente_desde date DEFAULT CURRENT_DATE NOT NULL,
    vigente_hasta date,
    activa boolean DEFAULT true NOT NULL,
    CONSTRAINT chk_encuesta_ver CHECK ((version >= 1)),
    CONSTRAINT chk_encuesta_vig CHECK (((vigente_hasta IS NULL) OR (vigente_hasta >= vigente_desde)))
);


--
-- Name: TABLE encuesta; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.encuesta IS 'Cuestionario de calidad en una version concreta. Se versiona porque con columnas fijas, cambiar una pregunta romperia la comparabilidad historica: las respuestas viejas quedarian bajo un enunciado que no es el que se pregunto.';


--
-- Name: encuesta_id_encuesta_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.encuesta ALTER COLUMN id_encuesta ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.encuesta_id_encuesta_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: enlace_registro; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.enlace_registro (
    id_enlace bigint NOT NULL,
    fk_sesion bigint NOT NULL,
    token uuid DEFAULT gen_random_uuid() NOT NULL,
    url_publica character varying(300) NOT NULL,
    ruta_imagen_qr character varying(300),
    canal character varying(10) NOT NULL,
    ventana tstzrange NOT NULL,
    usos_maximos integer,
    revocado_en timestamp with time zone,
    fk_usuario_crea bigint,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_enlace_canal CHECK (((canal)::text = ANY ((ARRAY['QR'::character varying, 'ENLACE'::character varying])::text[]))),
    CONSTRAINT chk_enlace_ruta_qr CHECK (((ruta_imagen_qr IS NULL) OR ((ruta_imagen_qr)::text !~ '^([A-Za-z]:|/|\\\\)'::text))),
    CONSTRAINT chk_enlace_usos CHECK (((usos_maximos IS NULL) OR (usos_maximos > 0))),
    CONSTRAINT chk_enlace_ventana CHECK (((NOT isempty(ventana)) AND (lower(ventana) IS NOT NULL) AND (upper(ventana) IS NOT NULL)))
);


--
-- Name: TABLE enlace_registro; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.enlace_registro IS 'Punto de entrada al registro de una sesion, materializado como QR o como URL. El .docx exige que "el QR y URL no pueden ser reutilizables" y que tengan "hora de inicio y hora de cierre" configurables.';


--
-- Name: COLUMN enlace_registro.canal; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.enlace_registro.canal IS 'QR o ENLACE. Debe concordar con la modalidad de la sesion (RN-13).';


--
-- Name: COLUMN enlace_registro.ventana; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.enlace_registro.ventana IS 'Apertura y cierre EN UN SOLO ATRIBUTO de rango. Con dos columnas sueltas, ni el EXCLUDE de RN-36 ni la contencion de RN-15 serian declarativos: los dos serian codigo que alguien tendria que mantener.';


--
-- Name: enlace_registro_id_enlace_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.enlace_registro ALTER COLUMN id_enlace ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.enlace_registro_id_enlace_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: estado_proceso; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.estado_proceso (
    id_estado character varying(12) NOT NULL,
    nombre character varying(40) NOT NULL,
    es_final boolean DEFAULT false NOT NULL,
    es_exitoso boolean DEFAULT false NOT NULL,
    CONSTRAINT chk_estado_coherente CHECK (((es_exitoso = false) OR (es_final = true)))
);


--
-- Name: TABLE estado_proceso; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.estado_proceso IS 'Los cinco estados del Monitor Procesos del ASIS, mas GENERADO para el momento en que el archivo existe pero todavia no se ha subido.';


--
-- Name: facultad; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.facultad (
    id_facultad character varying(10) NOT NULL,
    nombre character varying(120) NOT NULL,
    fk_facultad_padre character varying(10),
    activo boolean DEFAULT true NOT NULL,
    CONSTRAINT chk_facultad_padre CHECK (((fk_facultad_padre)::text <> (id_facultad)::text))
);


--
-- Name: TABLE facultad; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.facultad IS 'Unidad academica que agrupa programas. La referencia reflexiva produce un ARBOL - cada nodo tiene un solo padre -, no un grafo. Por eso se resuelve con una columna en la misma tabla y se consulta con WITH RECURSIVE.';


--
-- Name: lote_carga_asistente; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.lote_carga_asistente (
    id_lote_carga bigint NOT NULL,
    nombre_archivo character varying(200) NOT NULL,
    cargado_en timestamp with time zone DEFAULT now() NOT NULL,
    fk_usuario bigint,
    filas_leidas integer DEFAULT 0 NOT NULL,
    filas_aceptadas integer DEFAULT 0 NOT NULL,
    filas_rechazadas integer DEFAULT 0 NOT NULL,
    observaciones text,
    CONSTRAINT chk_lote_carga_filas CHECK (((filas_leidas >= 0) AND (filas_aceptadas >= 0) AND (filas_rechazadas >= 0) AND ((filas_aceptadas + filas_rechazadas) <= filas_leidas)))
);


--
-- Name: TABLE lote_carga_asistente; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.lote_carga_asistente IS 'Cada ejecucion de la carga del archivo de personas del ASIS. "Ese archivo lo cargamos en la base de datos como una tabla" (52:57). Una carga de 16.093 filas necesita EVIDENCIA, no un mensaje en pantalla: sin estos contadores, "cargo menos filas de las que tenia" es indepurable.';


--
-- Name: lote_carga_asistente_id_lote_carga_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.lote_carga_asistente ALTER COLUMN id_lote_carga ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.lote_carga_asistente_id_lote_carga_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: lote_migracion; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.lote_migracion (
    id_lote_migracion bigint NOT NULL,
    fk_sesion bigint NOT NULL,
    nombre_proceso character varying(60) DEFAULT 'ME_MIGRACION_CATEDRA'::character varying NOT NULL,
    nombre_archivo character varying(200) NOT NULL,
    generado_en timestamp with time zone DEFAULT now() NOT NULL,
    fk_usuario bigint,
    instancia_proceso_asis character varying(30),
    fk_estado_proceso character varying(12) DEFAULT 'GENERADO'::character varying NOT NULL,
    total_filas integer DEFAULT 0 NOT NULL,
    observaciones text,
    CONSTRAINT chk_lote_mig_filas CHECK ((total_filas >= 0))
);


--
-- Name: COLUMN lote_migracion.instancia_proceso_asis; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.lote_migracion.instancia_proceso_asis IS 'El numero de instancia que devuelve el ASIS al ejecutar el proceso en PSUNX01. Es lo que permite cerrar el ciclo contra el Monitor Procesos.';


--
-- Name: lote_migracion_id_lote_migracion_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.lote_migracion ALTER COLUMN id_lote_migracion ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.lote_migracion_id_lote_migracion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: modalidad; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.modalidad (
    id_modalidad character varying(15) NOT NULL,
    nombre character varying(60) NOT NULL,
    canal_difusion character varying(10) NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    CONSTRAINT chk_modalidad_canal CHECK (((canal_difusion)::text = ANY ((ARRAY['QR'::character varying, 'ENLACE'::character varying, 'AMBOS'::character varying])::text[])))
);


--
-- Name: COLUMN modalidad.canal_difusion; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.modalidad.canal_difusion IS 'QR si es presencial, ENLACE si es virtual. Traduce la regla del profesor Hugo Nelson en 1:06:53: "cuando es virtual enviamos el enlace; si es presencial, el QR". Se hace cumplir en el script 10 (RN-13).';


--
-- Name: novedad_carga; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.novedad_carga (
    id_novedad bigint NOT NULL,
    fk_lote_carga bigint NOT NULL,
    numero_fila integer NOT NULL,
    contenido_crudo text NOT NULL,
    motivo character varying(200) NOT NULL,
    CONSTRAINT chk_novedad_fila CHECK ((numero_fila > 0))
);


--
-- Name: COLUMN novedad_carga.contenido_crudo; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.novedad_carga.contenido_crudo IS 'La fila del archivo TAL COMO VENIA, sin interpretar. Es lo unico que permite depurar un rechazo por formato: si se guardara ya convertida, se perderia justamente el dato que causo el problema.';


--
-- Name: novedad_carga_id_novedad_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.novedad_carga ALTER COLUMN id_novedad ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.novedad_carga_id_novedad_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: opcion_pregunta; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.opcion_pregunta (
    id_opcion bigint NOT NULL,
    fk_pregunta bigint NOT NULL,
    etiqueta character varying(150) NOT NULL,
    valor smallint,
    orden smallint NOT NULL
);


--
-- Name: opcion_pregunta_id_opcion_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.opcion_pregunta ALTER COLUMN id_opcion ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.opcion_pregunta_id_opcion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: parametro; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.parametro (
    clave character varying(60) NOT NULL,
    valor character varying(200) NOT NULL,
    tipo_dato character varying(15) DEFAULT 'TEXTO'::character varying NOT NULL,
    descripcion character varying(300) NOT NULL,
    fk_usuario_modifica bigint,
    modificado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_parametro_tipo CHECK (((tipo_dato)::text = ANY ((ARRAY['TEXTO'::character varying, 'ENTERO'::character varying, 'BOOLEANO'::character varying, 'FECHA'::character varying, 'DECIMAL'::character varying])::text[])))
);


--
-- Name: TABLE parametro; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.parametro IS 'Configuracion que el administrador cambia sin tocar el codigo. Del .docx: "el administrador configura o parametriza los valores que considere".';


--
-- Name: periodo_academico; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.periodo_academico (
    id_periodo character(6) NOT NULL,
    fecha_ini date NOT NULL,
    fecha_fin date NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    CONSTRAINT chk_periodo_fechas CHECK ((fecha_fin > fecha_ini)),
    CONSTRAINT chk_periodo_formato CHECK ((id_periodo ~ '^[0-9]{4}-[1-3]$'::text))
);


--
-- Name: TABLE periodo_academico; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.periodo_academico IS 'Periodo academico: 2026-1, 2026-2. Lo pidio el profesor Hugo Nelson por su nombre - "cuantas personas externas han ingresado en 2026-2" (56:16).';


--
-- Name: ponencia; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.ponencia (
    fk_sesion bigint NOT NULL,
    fk_asistente bigint NOT NULL,
    rol character varying(15) DEFAULT 'PONENTE'::character varying NOT NULL,
    CONSTRAINT chk_ponencia_rol CHECK (((rol)::text = ANY ((ARRAY['PONENTE'::character varying, 'MODERADOR'::character varying, 'INVITADO'::character varying, 'ORGANIZADOR'::character varying])::text[])))
);


--
-- Name: pregunta; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.pregunta (
    id_pregunta bigint NOT NULL,
    fk_encuesta bigint NOT NULL,
    enunciado character varying(300) NOT NULL,
    orden smallint NOT NULL,
    fk_tipo_pregunta character varying(15) NOT NULL,
    obligatoria boolean DEFAULT false NOT NULL,
    valor_min smallint,
    valor_max smallint,
    CONSTRAINT chk_pregunta_ord CHECK ((orden >= 1)),
    CONSTRAINT chk_pregunta_rango CHECK ((((valor_min IS NULL) AND (valor_max IS NULL)) OR ((valor_min IS NOT NULL) AND (valor_max IS NOT NULL) AND (valor_max > valor_min))))
);


--
-- Name: pregunta_id_pregunta_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.pregunta ALTER COLUMN id_pregunta ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.pregunta_id_pregunta_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: programa_academico; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.programa_academico (
    codigo character varying(5) NOT NULL,
    nombre character varying(150) NOT NULL,
    fk_facultad character varying(10),
    nivel character varying(25) DEFAULT 'PREGRADO'::character varying NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    CONSTRAINT chk_programa_codigo CHECK (((codigo)::text ~ '^[A-Z][0-9A-Z]{3,4}$'::text)),
    CONSTRAINT chk_programa_nivel CHECK (((nivel)::text = ANY ((ARRAY['PREGRADO'::character varying, 'ESPECIALIZACION'::character varying, 'MAESTRIA'::character varying, 'DOCTORADO'::character varying, 'EDUCACION_CONTINUA'::character varying, 'OTRO'::character varying])::text[])))
);


--
-- Name: TABLE programa_academico; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.programa_academico IS 'Programa academico. 105 codigos distintos en el maestro real: 103 con la forma M + 4 digitos, mas MCDER de 5 caracteres y MCCP de 4.';


--
-- Name: COLUMN programa_academico.codigo; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.programa_academico.codigo IS 'CLAVE NATURAL a proposito: es el codigo que viaja al archivo plano del ASIS. Un identificador sustituto obligaria a un JOIN en la consulta mas critica del sistema, que es justamente la exportacion.';


--
-- Name: programa_asistente; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.programa_asistente (
    fk_asistente bigint NOT NULL,
    fk_programa character varying(5) NOT NULL,
    fk_periodo character(6) NOT NULL,
    estado character varying(15) DEFAULT 'ACTIVO'::character varying NOT NULL,
    CONSTRAINT chk_programa_asistente_estado CHECK (((estado)::text = ANY ((ARRAY['ACTIVO'::character varying, 'RETIRADO'::character varying, 'GRADUADO'::character varying, 'APLAZADO'::character varying])::text[])))
);


--
-- Name: TABLE programa_asistente; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.programa_asistente IS 'Matricula de un asistente en un programa, por periodo. Es N:M por dato comprobado: en el maestro real el mismo ID aparece con varios codigos de programa. La clave de tres columnas absorbe los pares duplicados que trae el archivo del ASIS - hay pares repetidos hasta tres veces.';


--
-- Name: registro_asistencia; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.registro_asistencia (
    id_registro bigint NOT NULL,
    fk_sesion bigint NOT NULL,
    fk_asistente bigint NOT NULL,
    fk_enlace bigint,
    fk_clave bigint,
    registrado_en timestamp with time zone DEFAULT now() NOT NULL,
    fk_programa_snapshot character varying(5),
    fk_vinculacion_snapshot character varying(15) NOT NULL,
    origen character varying(15) DEFAULT 'QR'::character varying NOT NULL,
    ip inet,
    user_agent character varying(300),
    CONSTRAINT chk_registro_clave CHECK ((((origen)::text = ANY ((ARRAY['MANUAL'::character varying, 'IMPORTADO'::character varying])::text[])) OR (fk_clave IS NOT NULL))),
    CONSTRAINT chk_registro_origen CHECK (((origen)::text = ANY ((ARRAY['QR'::character varying, 'ENLACE'::character varying, 'MANUAL'::character varying, 'IMPORTADO'::character varying])::text[])))
);


--
-- Name: TABLE registro_asistencia; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.registro_asistencia IS 'Hecho de que un asistente quedo registrado en una sesion, en un instante concreto, con el programa y la vinculacion que tenia en ese momento. Es la tabla central del sistema.';


--
-- Name: COLUMN registro_asistencia.fk_programa_snapshot; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.registro_asistencia.fk_programa_snapshot IS 'INSTANTANEA, no referencia viva. El programa que el asistente tenia EL DIA de la catedra. NUNCA se actualiza. Razon: "el programa es importante porque despues eso le da informacion a Registro de que programas hizo el estudiante" (50:14) - es una afirmacion sobre el pasado. Si se leyera del vigente, un estudiante que cambia de carrera reescribiria su propio historial y el archivo enviado al ASIS dejaria de ser reproducible. NULO cuando la vinculacion no exige programa (Rutas de Paz, RN-07).';


--
-- Name: COLUMN registro_asistencia.fk_vinculacion_snapshot; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.registro_asistencia.fk_vinculacion_snapshot IS 'INSTANTANEA de la vinculacion. Un egresado que asistio siendo estudiante debe seguir contando como estudiante en los informes de aquel periodo.';


--
-- Name: registro_asistencia_id_registro_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.registro_asistencia ALTER COLUMN id_registro ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.registro_asistencia_id_registro_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: respuesta_encuesta; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.respuesta_encuesta (
    id_respuesta bigint NOT NULL,
    fk_registro bigint NOT NULL,
    fk_encuesta bigint NOT NULL,
    respondida_en timestamp with time zone DEFAULT now() NOT NULL,
    completa boolean DEFAULT false NOT NULL
);


--
-- Name: COLUMN respuesta_encuesta.completa; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.respuesta_encuesta.completa IS 'Solo lo marca sp_cerrar_encuesta, tras comprobar que todas las preguntas obligatorias tienen respuesta (RN-26). Es una regla NO DECLARATIVA: ninguna clave foranea puede exigir "al menos uno".';


--
-- Name: respuesta_encuesta_id_respuesta_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.respuesta_encuesta ALTER COLUMN id_respuesta ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.respuesta_encuesta_id_respuesta_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: respuesta_item; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.respuesta_item (
    id_item bigint NOT NULL,
    fk_respuesta bigint NOT NULL,
    fk_pregunta bigint NOT NULL,
    valor_numerico smallint,
    valor_texto text,
    fk_opcion bigint,
    CONSTRAINT chk_respuesta_item_un_valor CHECK ((((((valor_numerico IS NOT NULL))::integer + ((valor_texto IS NOT NULL))::integer) + ((fk_opcion IS NOT NULL))::integer) = 1))
);


--
-- Name: TABLE respuesta_item; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.respuesta_item IS 'Respuesta a una pregunta concreta. La alternativa ortodoxa es una especializacion supertipo/subtipo con una tabla por tipo de respuesta: es correcta y se acepta, pero cuesta tres tablas y una union en cada consulta de evaluacion.';


--
-- Name: CONSTRAINT chk_respuesta_item_un_valor ON respuesta_item; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON CONSTRAINT chk_respuesta_item_un_valor ON catedras.respuesta_item IS 'RN-25. Impide la corrupcion silenciosa: sin esta restriccion, un item con las tres columnas vacias se colaria y los promedios del informe de evaluacion saldrian mal SIN AVISAR. La concordancia entre la columna usada y el tipo de la pregunta la verifica el disparador del script 10.';


--
-- Name: respuesta_item_id_item_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.respuesta_item ALTER COLUMN id_item ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.respuesta_item_id_item_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: rol; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.rol (
    id_rol character varying(20) NOT NULL,
    nombre character varying(60) NOT NULL,
    descripcion character varying(200)
);


--
-- Name: rol_por_usuario; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.rol_por_usuario (
    fk_usuario bigint NOT NULL,
    fk_rol character varying(20) NOT NULL,
    fecha_ini date DEFAULT CURRENT_DATE NOT NULL,
    fecha_fin date,
    CONSTRAINT chk_rol_usuario_fechas CHECK (((fecha_fin IS NULL) OR (fecha_fin >= fecha_ini)))
);


--
-- Name: sede; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.sede (
    id_sede character varying(15) NOT NULL,
    nombre character varying(80) NOT NULL,
    direccion character varying(200),
    es_virtual boolean DEFAULT false NOT NULL,
    activo boolean DEFAULT true NOT NULL
);


--
-- Name: TABLE sede; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.sede IS 'Lugar fisico o virtual donde se dicta una sesion. Aparece porque "puede que una catedra este en San Benito, otra este virtual y otra este en Bello" (1:03:33): LA SEDE ES LO QUE DISTINGUE DOS CATEDRAS A LA MISMA HORA. Como texto libre en sesion, el informe por sede no se puede escribir.';


--
-- Name: sesion; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.sesion (
    id_sesion bigint NOT NULL,
    fk_catedra bigint NOT NULL,
    numero_reunion smallint NOT NULL,
    numero_reunion_asis smallint,
    titulo character varying(200),
    inicio timestamp with time zone NOT NULL,
    fin timestamp with time zone NOT NULL,
    fk_modalidad character varying(15) NOT NULL,
    fk_sede character varying(15) NOT NULL,
    fk_periodo character(6) NOT NULL,
    fk_encuesta bigint,
    lugar character varying(200),
    enlace_virtual character varying(300),
    cupo integer,
    estado character varying(15) DEFAULT 'PROGRAMADA'::character varying NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_sesion_cupo CHECK (((cupo IS NULL) OR (cupo > 0))),
    CONSTRAINT chk_sesion_estado CHECK (((estado)::text = ANY ((ARRAY['PROGRAMADA'::character varying, 'ABIERTA'::character varying, 'CERRADA'::character varying, 'MIGRADA'::character varying])::text[]))),
    CONSTRAINT chk_sesion_fechas CHECK ((fin > inicio)),
    CONSTRAINT chk_sesion_reunion CHECK ((numero_reunion >= 1))
);


--
-- Name: TABLE sesion; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.sesion IS 'Cada una de las reuniones en que se dicta una catedra. ENTIDAD DEBIL: la "reunion 3" no significa nada suelta, es la reunion 3 DE UN EVENTO.';


--
-- Name: COLUMN sesion.numero_reunion; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.sesion.numero_reunion IS 'El numero de reunion con que la sesion viaja al ASIS. Si no se indica, el disparador del script 10 PROPONE el maximo de la catedra mas uno - y eso elimina el paso 2 del manual para las catedras nuevas. Para las que ya existen en el ASIS, el valor bueno es numero_reunion_asis: el dato real demuestra que el ASIS no numera por evento desde 1.';


--
-- Name: COLUMN sesion.numero_reunion_asis; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.sesion.numero_reunion_asis IS 'El numero de reunion segun el ASIS. DECISION RESUELTA POR EL DATO: el ASIS lleva un contador propio - de 5.481 eventos con una sola reunion, solo 588 tienen el numero 1, y los demas llegan hasta 4348. Cuando esta columna tiene valor, MANDA sobre numero_reunion.';


--
-- Name: sesion_id_sesion_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.sesion ALTER COLUMN id_sesion ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.sesion_id_sesion_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tipo_documento; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.tipo_documento (
    id_tipo_documento character varying(5) NOT NULL,
    nombre character varying(60) NOT NULL,
    activo boolean DEFAULT true NOT NULL
);


--
-- Name: TABLE tipo_documento; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.tipo_documento IS 'Clase de documento de identidad. Catalogo cerrado que elimina las mas de diez formas de escribir "cedula" que trae el formulario actual.';


--
-- Name: tipo_evento; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.tipo_evento (
    id_tipo_evento character(4) NOT NULL,
    nombre character varying(80) NOT NULL,
    activo boolean DEFAULT true NOT NULL
);


--
-- Name: TABLE tipo_evento; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.tipo_evento IS 'Clasificacion del evento en el ASIS. Ocho valores observados en las 5.711 filas reales: CAAB (5.449), DLLH (188), DEPR (44), SLDI (16), ARCU (5), MTG (5), DIIB (3), EIIC (1).';


--
-- Name: tipo_pregunta; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.tipo_pregunta (
    id_tipo_pregunta character varying(15) NOT NULL,
    nombre character varying(60) NOT NULL,
    guarda_numero boolean DEFAULT false NOT NULL,
    guarda_texto boolean DEFAULT false NOT NULL,
    guarda_opcion boolean DEFAULT false NOT NULL,
    CONSTRAINT chk_tipo_pregunta_destino CHECK (((((guarda_numero)::integer + (guarda_texto)::integer) + (guarda_opcion)::integer) = 1))
);


--
-- Name: TABLE tipo_pregunta; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.tipo_pregunta IS 'Clase de pregunta. Las tres columnas booleanas dicen en cual de las tres columnas de valor de respuesta_item se guarda la respuesta. Es lo que permite que la regla condicional (RN-25) sea DATO y no codigo.';


--
-- Name: tipo_vinculacion; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.tipo_vinculacion (
    id_tipo_vinculacion character varying(15) NOT NULL,
    nombre character varying(60) NOT NULL,
    es_interno boolean NOT NULL,
    exige_programa boolean DEFAULT true NOT NULL,
    activo boolean DEFAULT true NOT NULL
);


--
-- Name: TABLE tipo_vinculacion; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.tipo_vinculacion IS 'RUTAS_PAZ tiene exige_programa = false por la excepcion que planteo el profesor Hugo Nelson en 41:16: "ellos entrarian sin programa, pero solo ellos". ADMINISTRATIVO tambien, porque no esta matriculado en nada.';


--
-- Name: COLUMN tipo_vinculacion.es_interno; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.tipo_vinculacion.es_interno IS 'Resuelve el informe 2 del enunciado - internos contra externos - con una agrupacion, en vez de un CASE de veinte lineas.';


--
-- Name: COLUMN tipo_vinculacion.exige_programa; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.tipo_vinculacion.exige_programa IS 'FALSO en Rutas de Paz. Traduce la frase "ellos entrarian sin programa, pero solo ellos" (41:16) en un DATO. Habilitar una nueva excepcion es un UPDATE de una fila, no un ALTER TABLE en produccion.';


--
-- Name: usuario; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.usuario (
    id_usuario bigint NOT NULL,
    fk_asistente bigint NOT NULL,
    usuario character varying(40) NOT NULL,
    clave_hash character varying(255) NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    ultimo_acceso timestamp with time zone,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_usuario_login CHECK (((usuario)::text ~ '^[a-z0-9._-]{4,40}$'::text))
);


--
-- Name: COLUMN usuario.clave_hash; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON COLUMN catedras.usuario.clave_hash IS 'RN-34 · Nunca la clave en claro. Aqui se guarda un hash con sal; el algoritmo lo decide la aplicacion (bcrypt o argon2 preferiblemente).';


--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE; Schema: catedras; Owner: -
--

ALTER TABLE catedras.usuario ALTER COLUMN id_usuario ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME catedras.usuario_id_usuario_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: v_asistencia_completa; Type: VIEW; Schema: catedras; Owner: -
--

CREATE VIEW catedras.v_asistencia_completa AS
 SELECT r.id_registro,
    r.registrado_en,
    r.origen,
    c.id_evento_asis,
    c.nombre AS catedra,
    s.id_sesion,
    s.numero_reunion,
    s.titulo AS sesion,
    s.inicio,
    s.fk_periodo AS periodo,
    se.nombre AS sede,
    m.nombre AS modalidad,
    a.id_asistente,
    a.id_asis,
    (((a.nombres)::text || ' '::text) || (a.apellidos)::text) AS asistente,
    a.es_externo,
    r.fk_programa_snapshot AS programa,
    p.nombre AS programa_nombre,
    p.fk_facultad AS facultad,
    r.fk_vinculacion_snapshot AS vinculacion,
    tv.es_interno,
    (re.id_respuesta IS NOT NULL) AS respondio_encuesta
   FROM ((((((((catedras.registro_asistencia r
     JOIN catedras.sesion s ON ((s.id_sesion = r.fk_sesion)))
     JOIN catedras.catedra c ON ((c.id_catedra = s.fk_catedra)))
     JOIN catedras.sede se ON (((se.id_sede)::text = (s.fk_sede)::text)))
     JOIN catedras.modalidad m ON (((m.id_modalidad)::text = (s.fk_modalidad)::text)))
     JOIN catedras.asistente a ON ((a.id_asistente = r.fk_asistente)))
     JOIN catedras.tipo_vinculacion tv ON (((tv.id_tipo_vinculacion)::text = (r.fk_vinculacion_snapshot)::text)))
     LEFT JOIN catedras.programa_academico p ON (((p.codigo)::text = (r.fk_programa_snapshot)::text)))
     LEFT JOIN catedras.respuesta_encuesta re ON ((re.fk_registro = r.id_registro)));


--
-- Name: VIEW v_asistencia_completa; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON VIEW catedras.v_asistencia_completa IS 'Base de los informes I1 a I5 y I14. Usa las INSTANTANEAS del registro, no el programa ni la vinculacion vigentes: es lo que hace que un informe de un periodo cerrado siga dando lo mismo dentro de un ano.';


--
-- Name: vinculacion_asistente; Type: TABLE; Schema: catedras; Owner: -
--

CREATE TABLE catedras.vinculacion_asistente (
    fk_asistente bigint NOT NULL,
    fk_tipo_vinculacion character varying(15) NOT NULL,
    fecha_ini date NOT NULL,
    fecha_fin date,
    CONSTRAINT chk_vinculacion_fechas CHECK (((fecha_fin IS NULL) OR (fecha_fin >= fecha_ini)))
);


--
-- Name: TABLE vinculacion_asistente; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON TABLE catedras.vinculacion_asistente IS 'Vinculacion institucional de una persona a lo largo del tiempo.';


--
-- Name: v_asistente_vigente; Type: VIEW; Schema: catedras; Owner: -
--

CREATE VIEW catedras.v_asistente_vigente AS
 SELECT a.id_asistente,
    a.id_asis,
    (((a.nombres)::text || ' '::text) || (a.apellidos)::text) AS nombre_completo,
    a.es_externo,
    COALESCE(a.correo_institucional, a.correo_personal) AS correo_contacto,
    (a.correo_institucional IS NOT NULL) AS tiene_correo_institucional,
    d.numero AS documento_vigente,
    d.fk_tipo_documento AS tipo_documento,
    v.fk_tipo_vinculacion AS vinculacion,
    tv.nombre AS vinculacion_nombre,
    tv.es_interno,
    tv.exige_programa,
    a.activo
   FROM (((catedras.asistente a
     LEFT JOIN catedras.documento_asistente d ON (((d.fk_asistente = a.id_asistente) AND d.vigente)))
     LEFT JOIN LATERAL ( SELECT va.fk_tipo_vinculacion
           FROM catedras.vinculacion_asistente va
          WHERE ((va.fk_asistente = a.id_asistente) AND (va.fecha_fin IS NULL))
          ORDER BY va.fecha_ini DESC
         LIMIT 1) v ON (true))
     LEFT JOIN catedras.tipo_vinculacion tv ON (((tv.id_tipo_vinculacion)::text = (v.fk_tipo_vinculacion)::text)));


--
-- Name: VIEW v_asistente_vigente; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON VIEW catedras.v_asistente_vigente IS 'La foto ACTUAL de una persona: su documento vigente y su vinculacion vigente. Ojo: para los informes de asistencia NO se usa esta vista, sino las instantaneas del registro. Aqui esta el hoy; alli, el dia de la catedra.';


--
-- Name: v_control_ventana; Type: VIEW; Schema: catedras; Owner: -
--

CREATE VIEW catedras.v_control_ventana AS
 SELECT r.id_registro,
    r.registrado_en,
    e.ventana,
    r.origen
   FROM (catedras.registro_asistencia r
     JOIN catedras.enlace_registro e ON ((e.id_enlace = r.fk_enlace)))
  WHERE (((r.origen)::text <> ALL ((ARRAY['MANUAL'::character varying, 'IMPORTADO'::character varying])::text[])) AND (NOT (e.ventana @> r.registrado_en)));


--
-- Name: VIEW v_control_ventana; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON VIEW catedras.v_control_ventana IS 'CONTROL de RN-15. Debe devolver CERO filas siempre. Si alguna vez devuelve algo, es que se desactivo el disparador o que alguien inserto por detras.';


--
-- Name: v_embudo_registro; Type: VIEW; Schema: catedras; Owner: -
--

CREATE VIEW catedras.v_embudo_registro AS
 SELECT s.id_sesion,
    c.nombre AS catedra,
    s.numero_reunion,
    ( SELECT count(*) AS count
           FROM catedras.enlace_registro e
          WHERE (e.fk_sesion = s.id_sesion)) AS enlaces,
    ( SELECT count(*) AS count
           FROM (catedras.clave_acceso k
             JOIN catedras.enlace_registro e ON ((e.id_enlace = k.fk_enlace)))
          WHERE (e.fk_sesion = s.id_sesion)) AS claves_enviadas,
    ( SELECT count(*) AS count
           FROM (catedras.clave_acceso k
             JOIN catedras.enlace_registro e ON ((e.id_enlace = k.fk_enlace)))
          WHERE ((e.fk_sesion = s.id_sesion) AND (k.usado_en IS NOT NULL))) AS claves_usadas,
    ( SELECT count(*) AS count
           FROM catedras.registro_asistencia r
          WHERE (r.fk_sesion = s.id_sesion)) AS registros,
    ( SELECT count(*) AS count
           FROM (catedras.respuesta_encuesta re
             JOIN catedras.registro_asistencia r ON ((r.id_registro = re.fk_registro)))
          WHERE (r.fk_sesion = s.id_sesion)) AS encuestas
   FROM (catedras.sesion s
     JOIN catedras.catedra c ON ((c.id_catedra = s.fk_catedra)));


--
-- Name: v_evaluacion_sesion; Type: VIEW; Schema: catedras; Owner: -
--

CREATE VIEW catedras.v_evaluacion_sesion AS
 SELECT s.id_sesion,
    c.nombre AS catedra,
    s.numero_reunion,
    p.orden,
    p.enunciado,
    tp.id_tipo_pregunta AS tipo,
    count(ri.id_item) AS respuestas,
    round(avg(ri.valor_numerico), 2) AS promedio,
    min(ri.valor_numerico) AS minimo,
    max(ri.valor_numerico) AS maximo
   FROM ((((((catedras.respuesta_item ri
     JOIN catedras.respuesta_encuesta re ON ((re.id_respuesta = ri.fk_respuesta)))
     JOIN catedras.registro_asistencia r ON ((r.id_registro = re.fk_registro)))
     JOIN catedras.sesion s ON ((s.id_sesion = r.fk_sesion)))
     JOIN catedras.catedra c ON ((c.id_catedra = s.fk_catedra)))
     JOIN catedras.pregunta p ON ((p.id_pregunta = ri.fk_pregunta)))
     JOIN catedras.tipo_pregunta tp ON (((tp.id_tipo_pregunta)::text = (p.fk_tipo_pregunta)::text)))
  WHERE tp.guarda_numero
  GROUP BY s.id_sesion, c.nombre, s.numero_reunion, p.orden, p.enunciado, tp.id_tipo_pregunta;


--
-- Name: v_pendiente_migracion; Type: VIEW; Schema: catedras; Owner: -
--

CREATE VIEW catedras.v_pendiente_migracion AS
 SELECT s.id_sesion,
    c.id_evento_asis,
    c.nombre AS catedra,
    s.numero_reunion,
    s.inicio,
    count(*) AS registros,
    count(*) FILTER (WHERE (a.id_asis IS NULL)) AS sin_id_asis,
    count(*) FILTER (WHERE (r.fk_programa_snapshot IS NULL)) AS sin_programa,
    count(*) FILTER (WHERE a.es_externo) AS externos,
    count(*) FILTER (WHERE ((a.id_asis IS NOT NULL) AND (r.fk_programa_snapshot IS NOT NULL) AND (NOT a.es_externo))) AS migrables
   FROM (((catedras.registro_asistencia r
     JOIN catedras.sesion s ON ((s.id_sesion = r.fk_sesion)))
     JOIN catedras.catedra c ON ((c.id_catedra = s.fk_catedra)))
     JOIN catedras.asistente a ON ((a.id_asistente = r.fk_asistente)))
  WHERE (NOT (EXISTS ( SELECT 1
           FROM catedras.lote_migracion lm
          WHERE ((lm.fk_sesion = s.id_sesion) AND ((lm.fk_estado_proceso)::text = 'CORRECTO'::text)))))
  GROUP BY s.id_sesion, c.id_evento_asis, c.nombre, s.numero_reunion, s.inicio;


--
-- Name: enlace_registro ex_enlace_sin_solape; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.enlace_registro
    ADD CONSTRAINT ex_enlace_sin_solape EXCLUDE USING gist (fk_sesion WITH =, ventana WITH &&) WHERE ((revocado_en IS NULL));


--
-- Name: CONSTRAINT ex_enlace_sin_solape ON enlace_registro; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON CONSTRAINT ex_enlace_sin_solape ON catedras.enlace_registro IS 'RN-36. El WHERE hace que los enlaces revocados no estorben: se puede revocar uno y emitir otro para la misma franja.';


--
-- Name: alias_programa pk_alias_programa; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.alias_programa
    ADD CONSTRAINT pk_alias_programa PRIMARY KEY (id_alias);


--
-- Name: asistente pk_asistente; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.asistente
    ADD CONSTRAINT pk_asistente PRIMARY KEY (id_asistente);


--
-- Name: bitacora pk_bitacora; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.bitacora
    ADD CONSTRAINT pk_bitacora PRIMARY KEY (id_bitacora);


--
-- Name: catedra pk_catedra; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.catedra
    ADD CONSTRAINT pk_catedra PRIMARY KEY (id_catedra);


--
-- Name: clave_acceso pk_clave_acceso; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.clave_acceso
    ADD CONSTRAINT pk_clave_acceso PRIMARY KEY (id_clave);


--
-- Name: consentimiento_datos pk_consentimiento; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.consentimiento_datos
    ADD CONSTRAINT pk_consentimiento PRIMARY KEY (id_consentimiento);


--
-- Name: dependencia pk_dependencia; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.dependencia
    ADD CONSTRAINT pk_dependencia PRIMARY KEY (id_dependencia);


--
-- Name: detalle_migracion pk_detalle_migracion; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.detalle_migracion
    ADD CONSTRAINT pk_detalle_migracion PRIMARY KEY (id_detalle);


--
-- Name: documento_asistente pk_documento_asistente; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.documento_asistente
    ADD CONSTRAINT pk_documento_asistente PRIMARY KEY (id_documento);


--
-- Name: encuesta pk_encuesta; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.encuesta
    ADD CONSTRAINT pk_encuesta PRIMARY KEY (id_encuesta);


--
-- Name: enlace_registro pk_enlace_registro; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.enlace_registro
    ADD CONSTRAINT pk_enlace_registro PRIMARY KEY (id_enlace);


--
-- Name: estado_proceso pk_estado_proceso; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.estado_proceso
    ADD CONSTRAINT pk_estado_proceso PRIMARY KEY (id_estado);


--
-- Name: facultad pk_facultad; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.facultad
    ADD CONSTRAINT pk_facultad PRIMARY KEY (id_facultad);


--
-- Name: lote_carga_asistente pk_lote_carga; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.lote_carga_asistente
    ADD CONSTRAINT pk_lote_carga PRIMARY KEY (id_lote_carga);


--
-- Name: lote_migracion pk_lote_migracion; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.lote_migracion
    ADD CONSTRAINT pk_lote_migracion PRIMARY KEY (id_lote_migracion);


--
-- Name: modalidad pk_modalidad; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.modalidad
    ADD CONSTRAINT pk_modalidad PRIMARY KEY (id_modalidad);


--
-- Name: novedad_carga pk_novedad_carga; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.novedad_carga
    ADD CONSTRAINT pk_novedad_carga PRIMARY KEY (id_novedad);


--
-- Name: opcion_pregunta pk_opcion_pregunta; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.opcion_pregunta
    ADD CONSTRAINT pk_opcion_pregunta PRIMARY KEY (id_opcion);


--
-- Name: parametro pk_parametro; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.parametro
    ADD CONSTRAINT pk_parametro PRIMARY KEY (clave);


--
-- Name: periodo_academico pk_periodo_academico; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.periodo_academico
    ADD CONSTRAINT pk_periodo_academico PRIMARY KEY (id_periodo);


--
-- Name: ponencia pk_ponencia; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.ponencia
    ADD CONSTRAINT pk_ponencia PRIMARY KEY (fk_sesion, fk_asistente, rol);


--
-- Name: pregunta pk_pregunta; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.pregunta
    ADD CONSTRAINT pk_pregunta PRIMARY KEY (id_pregunta);


--
-- Name: programa_academico pk_programa_academico; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.programa_academico
    ADD CONSTRAINT pk_programa_academico PRIMARY KEY (codigo);


--
-- Name: programa_asistente pk_programa_asistente; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.programa_asistente
    ADD CONSTRAINT pk_programa_asistente PRIMARY KEY (fk_asistente, fk_programa, fk_periodo);


--
-- Name: registro_asistencia pk_registro_asistencia; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.registro_asistencia
    ADD CONSTRAINT pk_registro_asistencia PRIMARY KEY (id_registro);


--
-- Name: respuesta_encuesta pk_respuesta_encuesta; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.respuesta_encuesta
    ADD CONSTRAINT pk_respuesta_encuesta PRIMARY KEY (id_respuesta);


--
-- Name: respuesta_item pk_respuesta_item; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.respuesta_item
    ADD CONSTRAINT pk_respuesta_item PRIMARY KEY (id_item);


--
-- Name: rol pk_rol; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.rol
    ADD CONSTRAINT pk_rol PRIMARY KEY (id_rol);


--
-- Name: rol_por_usuario pk_rol_por_usuario; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.rol_por_usuario
    ADD CONSTRAINT pk_rol_por_usuario PRIMARY KEY (fk_usuario, fk_rol, fecha_ini);


--
-- Name: CONSTRAINT pk_rol_por_usuario ON rol_por_usuario; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON CONSTRAINT pk_rol_por_usuario ON catedras.rol_por_usuario IS 'RN-31 · fecha_ini EN LA CLAVE PRIMARIA. Sin ella, quien fue administrador, dejo de serlo y vuelve, quedaria bloqueado para siempre. Es el mismo error que en vinculacion_asistente, y falla igual de silenciosamente.';


--
-- Name: sede pk_sede; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.sede
    ADD CONSTRAINT pk_sede PRIMARY KEY (id_sede);


--
-- Name: sesion pk_sesion; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.sesion
    ADD CONSTRAINT pk_sesion PRIMARY KEY (id_sesion);


--
-- Name: tipo_documento pk_tipo_documento; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.tipo_documento
    ADD CONSTRAINT pk_tipo_documento PRIMARY KEY (id_tipo_documento);


--
-- Name: tipo_evento pk_tipo_evento; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.tipo_evento
    ADD CONSTRAINT pk_tipo_evento PRIMARY KEY (id_tipo_evento);


--
-- Name: tipo_pregunta pk_tipo_pregunta; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.tipo_pregunta
    ADD CONSTRAINT pk_tipo_pregunta PRIMARY KEY (id_tipo_pregunta);


--
-- Name: tipo_vinculacion pk_tipo_vinculacion; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.tipo_vinculacion
    ADD CONSTRAINT pk_tipo_vinculacion PRIMARY KEY (id_tipo_vinculacion);


--
-- Name: usuario pk_usuario; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.usuario
    ADD CONSTRAINT pk_usuario PRIMARY KEY (id_usuario);


--
-- Name: vinculacion_asistente pk_vinculacion_asistente; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.vinculacion_asistente
    ADD CONSTRAINT pk_vinculacion_asistente PRIMARY KEY (fk_asistente, fk_tipo_vinculacion, fecha_ini);


--
-- Name: CONSTRAINT pk_vinculacion_asistente ON vinculacion_asistente; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON CONSTRAINT pk_vinculacion_asistente ON catedras.vinculacion_asistente IS 'fecha_ini ENTRA EN LA CLAVE PRIMARIA. Sin ella, un egresado que se matricula en una maestria no podria volver a ser estudiante: el INSERT se rechazaria y el historico quedaria incompleto en silencio.';


--
-- Name: alias_programa uq_alias_texto; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.alias_programa
    ADD CONSTRAINT uq_alias_texto UNIQUE (texto_normalizado);


--
-- Name: asistente uq_asistente_asis; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.asistente
    ADD CONSTRAINT uq_asistente_asis UNIQUE (id_asis);


--
-- Name: asistente uq_asistente_corinst; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.asistente
    ADD CONSTRAINT uq_asistente_corinst UNIQUE (correo_institucional);


--
-- Name: catedra uq_catedra_asis; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.catedra
    ADD CONSTRAINT uq_catedra_asis UNIQUE (id_evento_asis);


--
-- Name: consentimiento_datos uq_consentimiento_ver; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.consentimiento_datos
    ADD CONSTRAINT uq_consentimiento_ver UNIQUE (fk_asistente, version_politica);


--
-- Name: dependencia uq_dependencia_nombre; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.dependencia
    ADD CONSTRAINT uq_dependencia_nombre UNIQUE (nombre);


--
-- Name: detalle_migracion uq_detalle_lote_reg; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.detalle_migracion
    ADD CONSTRAINT uq_detalle_lote_reg UNIQUE (fk_lote_migracion, fk_registro);


--
-- Name: documento_asistente uq_documento_numero; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.documento_asistente
    ADD CONSTRAINT uq_documento_numero UNIQUE (fk_tipo_documento, numero);


--
-- Name: encuesta uq_encuesta_ver; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.encuesta
    ADD CONSTRAINT uq_encuesta_ver UNIQUE (nombre, version);


--
-- Name: enlace_registro uq_enlace_token; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.enlace_registro
    ADD CONSTRAINT uq_enlace_token UNIQUE (token);


--
-- Name: facultad uq_facultad_nombre; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.facultad
    ADD CONSTRAINT uq_facultad_nombre UNIQUE (nombre);


--
-- Name: opcion_pregunta uq_opcion_orden; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.opcion_pregunta
    ADD CONSTRAINT uq_opcion_orden UNIQUE (fk_pregunta, orden);


--
-- Name: pregunta uq_pregunta_ord; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.pregunta
    ADD CONSTRAINT uq_pregunta_ord UNIQUE (fk_encuesta, orden);


--
-- Name: registro_asistencia uq_registro_sesion_asis; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.registro_asistencia
    ADD CONSTRAINT uq_registro_sesion_asis UNIQUE (fk_sesion, fk_asistente);


--
-- Name: respuesta_item uq_respuesta_item; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.respuesta_item
    ADD CONSTRAINT uq_respuesta_item UNIQUE (fk_respuesta, fk_pregunta);


--
-- Name: respuesta_encuesta uq_respuesta_registro; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.respuesta_encuesta
    ADD CONSTRAINT uq_respuesta_registro UNIQUE (fk_registro);


--
-- Name: rol uq_rol_nombre; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.rol
    ADD CONSTRAINT uq_rol_nombre UNIQUE (nombre);


--
-- Name: sede uq_sede_nombre; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.sede
    ADD CONSTRAINT uq_sede_nombre UNIQUE (nombre);


--
-- Name: sesion uq_sesion_reunion; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.sesion
    ADD CONSTRAINT uq_sesion_reunion UNIQUE (fk_catedra, numero_reunion);


--
-- Name: tipo_documento uq_tipo_documento_nom; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.tipo_documento
    ADD CONSTRAINT uq_tipo_documento_nom UNIQUE (nombre);


--
-- Name: tipo_vinculacion uq_tipo_vinculacion_nom; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.tipo_vinculacion
    ADD CONSTRAINT uq_tipo_vinculacion_nom UNIQUE (nombre);


--
-- Name: usuario uq_usuario_login; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.usuario
    ADD CONSTRAINT uq_usuario_login UNIQUE (usuario);


--
-- Name: usuario uq_usuario_persona; Type: CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.usuario
    ADD CONSTRAINT uq_usuario_persona UNIQUE (fk_asistente);


--
-- Name: ix_alias_trgm; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_alias_trgm ON catedras.alias_programa USING gin (texto_normalizado public.gin_trgm_ops);


--
-- Name: INDEX ix_alias_trgm; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON INDEX catedras.ix_alias_trgm IS 'Indice de trigramas. Permite resolver "Psicologica" -> PSICOLOGIA y "Ingenieria de datos y software" -> M0286 por similitud, no por igualdad. En otro motor esto exigiria una tabla de equivalencias exactas o trabajo manual sobre cada fila.';


--
-- Name: ix_asistente_correo_personal; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_asistente_correo_personal ON catedras.asistente USING btree (correo_personal) WHERE (correo_personal IS NOT NULL);


--
-- Name: ix_bitacora_fecha; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_bitacora_fecha ON catedras.bitacora USING btree (ocurrido_en DESC);


--
-- Name: ix_bitacora_tabla; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_bitacora_tabla ON catedras.bitacora USING btree (nombre_tabla, ocurrido_en DESC);


--
-- Name: ix_catedra_depend; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_catedra_depend ON catedras.catedra USING btree (fk_dependencia) WHERE (fk_dependencia IS NOT NULL);


--
-- Name: ix_catedra_tipo; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_catedra_tipo ON catedras.catedra USING btree (fk_tipo_evento);


--
-- Name: ix_clave_asistente; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_clave_asistente ON catedras.clave_acceso USING btree (fk_asistente, generado_en DESC);


--
-- Name: ix_clave_enlace; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_clave_enlace ON catedras.clave_acceso USING btree (fk_enlace);


--
-- Name: ix_clave_intentos; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_clave_intentos ON catedras.clave_acceso USING btree (fk_asistente, intentos) WHERE (intentos > 0);


--
-- Name: ix_clave_no_institucional; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_clave_no_institucional ON catedras.clave_acceso USING btree (generado_en DESC) WHERE (NOT es_correo_institucional);


--
-- Name: INDEX ix_clave_no_institucional; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON INDEX catedras.ix_clave_no_institucional IS 'I18. Alimenta la decision que el profesor Carlos Castro dejo pendiente en 55:32 sobre los correos no institucionales.';


--
-- Name: ix_detmig_registro; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_detmig_registro ON catedras.detalle_migracion USING btree (fk_registro);


--
-- Name: ix_documento_numero; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_documento_numero ON catedras.documento_asistente USING btree (numero);


--
-- Name: INDEX ix_documento_numero; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON INDEX catedras.ix_documento_numero IS 'La persona digita su cedula sin decir que tipo de documento es. Sin este indice, uq_documento_numero no sirve porque su primera columna es el tipo.';


--
-- Name: ix_enlace_ventana; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_enlace_ventana ON catedras.enlace_registro USING gist (ventana);


--
-- Name: ix_lotemig_sesion; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_lotemig_sesion ON catedras.lote_migracion USING btree (fk_sesion, generado_en DESC);


--
-- Name: ix_novedad_lote; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_novedad_lote ON catedras.novedad_carga USING btree (fk_lote_carga);


--
-- Name: ix_pregunta_encuesta; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_pregunta_encuesta ON catedras.pregunta USING btree (fk_encuesta, orden);


--
-- Name: ix_progasi_periodo; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_progasi_periodo ON catedras.programa_asistente USING btree (fk_periodo);


--
-- Name: ix_progasi_programa; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_progasi_programa ON catedras.programa_asistente USING btree (fk_programa);


--
-- Name: ix_programa_facultad; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_programa_facultad ON catedras.programa_academico USING btree (fk_facultad);


--
-- Name: ix_registro_asistente; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_registro_asistente ON catedras.registro_asistencia USING btree (fk_asistente);


--
-- Name: ix_registro_fecha; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_registro_fecha ON catedras.registro_asistencia USING btree (registrado_en DESC);


--
-- Name: ix_registro_programa_snap; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_registro_programa_snap ON catedras.registro_asistencia USING btree (fk_programa_snapshot) WHERE (fk_programa_snapshot IS NOT NULL);


--
-- Name: ix_registro_sesion; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_registro_sesion ON catedras.registro_asistencia USING btree (fk_sesion, registrado_en);


--
-- Name: ix_registro_vinc_snap; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_registro_vinc_snap ON catedras.registro_asistencia USING btree (fk_vinculacion_snapshot);


--
-- Name: ix_respenc_encuesta; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_respenc_encuesta ON catedras.respuesta_encuesta USING btree (fk_encuesta);


--
-- Name: ix_respitem_pregunta; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_respitem_pregunta ON catedras.respuesta_item USING btree (fk_pregunta);


--
-- Name: ix_rolusr_vigente; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_rolusr_vigente ON catedras.rol_por_usuario USING btree (fk_usuario) WHERE (fecha_fin IS NULL);


--
-- Name: ix_sesion_inicio; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_sesion_inicio ON catedras.sesion USING btree (inicio DESC);


--
-- Name: ix_sesion_modalidad; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_sesion_modalidad ON catedras.sesion USING btree (fk_modalidad);


--
-- Name: ix_sesion_periodo; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_sesion_periodo ON catedras.sesion USING btree (fk_periodo);


--
-- Name: ix_sesion_sede; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_sesion_sede ON catedras.sesion USING btree (fk_sede);


--
-- Name: ix_vinculacion_vigente; Type: INDEX; Schema: catedras; Owner: -
--

CREATE INDEX ix_vinculacion_vigente ON catedras.vinculacion_asistente USING btree (fk_asistente, fecha_ini DESC) WHERE (fecha_fin IS NULL);


--
-- Name: ux_detmig_aceptado; Type: INDEX; Schema: catedras; Owner: -
--

CREATE UNIQUE INDEX ux_detmig_aceptado ON catedras.detalle_migracion USING btree (fk_registro) WHERE ((resultado)::text = 'ACEPTADO'::text);


--
-- Name: INDEX ux_detmig_aceptado; Type: COMMENT; Schema: catedras; Owner: -
--

COMMENT ON INDEX catedras.ux_detmig_aceptado IS 'RN-29. Permite reintentar cuantas veces haga falta y garantiza que la asistencia no se cargue dos veces en el ASIS.';


--
-- Name: ux_documento_vigente; Type: INDEX; Schema: catedras; Owner: -
--

CREATE UNIQUE INDEX ux_documento_vigente ON catedras.documento_asistente USING btree (fk_asistente) WHERE vigente;


--
-- Name: ux_enlace_vigente; Type: INDEX; Schema: catedras; Owner: -
--

CREATE UNIQUE INDEX ux_enlace_vigente ON catedras.enlace_registro USING btree (fk_sesion) WHERE (revocado_en IS NULL);


--
-- Name: asistente trg_bitacora_asistente; Type: TRIGGER; Schema: catedras; Owner: -
--

CREATE TRIGGER trg_bitacora_asistente AFTER DELETE OR UPDATE ON catedras.asistente FOR EACH ROW EXECUTE FUNCTION catedras.fn_trg_bitacora();


--
-- Name: registro_asistencia trg_bitacora_registro; Type: TRIGGER; Schema: catedras; Owner: -
--

CREATE TRIGGER trg_bitacora_registro AFTER INSERT OR DELETE OR UPDATE ON catedras.registro_asistencia FOR EACH ROW EXECUTE FUNCTION catedras.fn_trg_bitacora();


--
-- Name: clave_acceso trg_clave_derivar; Type: TRIGGER; Schema: catedras; Owner: -
--

CREATE TRIGGER trg_clave_derivar BEFORE INSERT OR UPDATE OF enviado_a ON catedras.clave_acceso FOR EACH ROW EXECUTE FUNCTION catedras.fn_trg_clave_derivar();


--
-- Name: enlace_registro trg_enlace_canal; Type: TRIGGER; Schema: catedras; Owner: -
--

CREATE TRIGGER trg_enlace_canal BEFORE INSERT OR UPDATE OF canal, fk_sesion ON catedras.enlace_registro FOR EACH ROW EXECUTE FUNCTION catedras.fn_trg_enlace_canal();


--
-- Name: registro_asistencia trg_registro_validar; Type: TRIGGER; Schema: catedras; Owner: -
--

CREATE TRIGGER trg_registro_validar BEFORE INSERT ON catedras.registro_asistencia FOR EACH ROW EXECUTE FUNCTION catedras.fn_trg_registro_validar();


--
-- Name: respuesta_item trg_respuesta_item_tipo; Type: TRIGGER; Schema: catedras; Owner: -
--

CREATE TRIGGER trg_respuesta_item_tipo BEFORE INSERT OR UPDATE ON catedras.respuesta_item FOR EACH ROW EXECUTE FUNCTION catedras.fn_trg_respuesta_item_tipo();


--
-- Name: sesion trg_sesion_consecutivo; Type: TRIGGER; Schema: catedras; Owner: -
--

CREATE TRIGGER trg_sesion_consecutivo BEFORE INSERT ON catedras.sesion FOR EACH ROW EXECUTE FUNCTION catedras.fn_trg_sesion_consecutivo();


--
-- Name: alias_programa fk_alias_programa; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.alias_programa
    ADD CONSTRAINT fk_alias_programa FOREIGN KEY (fk_programa) REFERENCES catedras.programa_academico(codigo) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: asistente fk_asistente_lote; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.asistente
    ADD CONSTRAINT fk_asistente_lote FOREIGN KEY (fk_lote_carga) REFERENCES catedras.lote_carga_asistente(id_lote_carga) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: bitacora fk_bitacora_usuario; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.bitacora
    ADD CONSTRAINT fk_bitacora_usuario FOREIGN KEY (fk_usuario) REFERENCES catedras.usuario(id_usuario) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: catedra fk_catedra_dependencia; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.catedra
    ADD CONSTRAINT fk_catedra_dependencia FOREIGN KEY (fk_dependencia) REFERENCES catedras.dependencia(id_dependencia) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: catedra fk_catedra_tipo_evento; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.catedra
    ADD CONSTRAINT fk_catedra_tipo_evento FOREIGN KEY (fk_tipo_evento) REFERENCES catedras.tipo_evento(id_tipo_evento) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: clave_acceso fk_clave_asistente; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.clave_acceso
    ADD CONSTRAINT fk_clave_asistente FOREIGN KEY (fk_asistente) REFERENCES catedras.asistente(id_asistente) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: clave_acceso fk_clave_enlace; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.clave_acceso
    ADD CONSTRAINT fk_clave_enlace FOREIGN KEY (fk_enlace) REFERENCES catedras.enlace_registro(id_enlace) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: consentimiento_datos fk_consentimiento_asistente; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.consentimiento_datos
    ADD CONSTRAINT fk_consentimiento_asistente FOREIGN KEY (fk_asistente) REFERENCES catedras.asistente(id_asistente) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: dependencia fk_dependencia_padre; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.dependencia
    ADD CONSTRAINT fk_dependencia_padre FOREIGN KEY (fk_dependencia_padre) REFERENCES catedras.dependencia(id_dependencia) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: detalle_migracion fk_detmig_lote; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.detalle_migracion
    ADD CONSTRAINT fk_detmig_lote FOREIGN KEY (fk_lote_migracion) REFERENCES catedras.lote_migracion(id_lote_migracion) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: detalle_migracion fk_detmig_registro; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.detalle_migracion
    ADD CONSTRAINT fk_detmig_registro FOREIGN KEY (fk_registro) REFERENCES catedras.registro_asistencia(id_registro) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: documento_asistente fk_documento_asistente; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.documento_asistente
    ADD CONSTRAINT fk_documento_asistente FOREIGN KEY (fk_asistente) REFERENCES catedras.asistente(id_asistente) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: documento_asistente fk_documento_tipo; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.documento_asistente
    ADD CONSTRAINT fk_documento_tipo FOREIGN KEY (fk_tipo_documento) REFERENCES catedras.tipo_documento(id_tipo_documento) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: enlace_registro fk_enlace_sesion; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.enlace_registro
    ADD CONSTRAINT fk_enlace_sesion FOREIGN KEY (fk_sesion) REFERENCES catedras.sesion(id_sesion) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: enlace_registro fk_enlace_usuario; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.enlace_registro
    ADD CONSTRAINT fk_enlace_usuario FOREIGN KEY (fk_usuario_crea) REFERENCES catedras.usuario(id_usuario) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: facultad fk_facultad_padre; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.facultad
    ADD CONSTRAINT fk_facultad_padre FOREIGN KEY (fk_facultad_padre) REFERENCES catedras.facultad(id_facultad) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: lote_carga_asistente fk_lotecarga_usuario; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.lote_carga_asistente
    ADD CONSTRAINT fk_lotecarga_usuario FOREIGN KEY (fk_usuario) REFERENCES catedras.usuario(id_usuario) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: lote_migracion fk_lotemig_estado; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.lote_migracion
    ADD CONSTRAINT fk_lotemig_estado FOREIGN KEY (fk_estado_proceso) REFERENCES catedras.estado_proceso(id_estado) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: lote_migracion fk_lotemig_sesion; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.lote_migracion
    ADD CONSTRAINT fk_lotemig_sesion FOREIGN KEY (fk_sesion) REFERENCES catedras.sesion(id_sesion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: lote_migracion fk_lotemig_usuario; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.lote_migracion
    ADD CONSTRAINT fk_lotemig_usuario FOREIGN KEY (fk_usuario) REFERENCES catedras.usuario(id_usuario) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: novedad_carga fk_novedad_lote; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.novedad_carga
    ADD CONSTRAINT fk_novedad_lote FOREIGN KEY (fk_lote_carga) REFERENCES catedras.lote_carga_asistente(id_lote_carga) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: opcion_pregunta fk_opcion_pregunta; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.opcion_pregunta
    ADD CONSTRAINT fk_opcion_pregunta FOREIGN KEY (fk_pregunta) REFERENCES catedras.pregunta(id_pregunta) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: parametro fk_parametro_usuario; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.parametro
    ADD CONSTRAINT fk_parametro_usuario FOREIGN KEY (fk_usuario_modifica) REFERENCES catedras.usuario(id_usuario) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: ponencia fk_ponencia_asistente; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.ponencia
    ADD CONSTRAINT fk_ponencia_asistente FOREIGN KEY (fk_asistente) REFERENCES catedras.asistente(id_asistente) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: ponencia fk_ponencia_sesion; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.ponencia
    ADD CONSTRAINT fk_ponencia_sesion FOREIGN KEY (fk_sesion) REFERENCES catedras.sesion(id_sesion) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pregunta fk_pregunta_encuesta; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.pregunta
    ADD CONSTRAINT fk_pregunta_encuesta FOREIGN KEY (fk_encuesta) REFERENCES catedras.encuesta(id_encuesta) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: pregunta fk_pregunta_tipo; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.pregunta
    ADD CONSTRAINT fk_pregunta_tipo FOREIGN KEY (fk_tipo_pregunta) REFERENCES catedras.tipo_pregunta(id_tipo_pregunta) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: programa_asistente fk_progasi_asistente; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.programa_asistente
    ADD CONSTRAINT fk_progasi_asistente FOREIGN KEY (fk_asistente) REFERENCES catedras.asistente(id_asistente) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: programa_asistente fk_progasi_periodo; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.programa_asistente
    ADD CONSTRAINT fk_progasi_periodo FOREIGN KEY (fk_periodo) REFERENCES catedras.periodo_academico(id_periodo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: programa_asistente fk_progasi_programa; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.programa_asistente
    ADD CONSTRAINT fk_progasi_programa FOREIGN KEY (fk_programa) REFERENCES catedras.programa_academico(codigo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: programa_academico fk_programa_facultad; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.programa_academico
    ADD CONSTRAINT fk_programa_facultad FOREIGN KEY (fk_facultad) REFERENCES catedras.facultad(id_facultad) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: registro_asistencia fk_registro_asistente; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.registro_asistencia
    ADD CONSTRAINT fk_registro_asistente FOREIGN KEY (fk_asistente) REFERENCES catedras.asistente(id_asistente) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: registro_asistencia fk_registro_clave; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.registro_asistencia
    ADD CONSTRAINT fk_registro_clave FOREIGN KEY (fk_clave) REFERENCES catedras.clave_acceso(id_clave) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: registro_asistencia fk_registro_enlace; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.registro_asistencia
    ADD CONSTRAINT fk_registro_enlace FOREIGN KEY (fk_enlace) REFERENCES catedras.enlace_registro(id_enlace) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: registro_asistencia fk_registro_programa_snap; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.registro_asistencia
    ADD CONSTRAINT fk_registro_programa_snap FOREIGN KEY (fk_programa_snapshot) REFERENCES catedras.programa_academico(codigo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: registro_asistencia fk_registro_sesion; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.registro_asistencia
    ADD CONSTRAINT fk_registro_sesion FOREIGN KEY (fk_sesion) REFERENCES catedras.sesion(id_sesion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: registro_asistencia fk_registro_vinculacion_snap; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.registro_asistencia
    ADD CONSTRAINT fk_registro_vinculacion_snap FOREIGN KEY (fk_vinculacion_snapshot) REFERENCES catedras.tipo_vinculacion(id_tipo_vinculacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: respuesta_encuesta fk_respenc_encuesta; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.respuesta_encuesta
    ADD CONSTRAINT fk_respenc_encuesta FOREIGN KEY (fk_encuesta) REFERENCES catedras.encuesta(id_encuesta) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: respuesta_encuesta fk_respenc_registro; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.respuesta_encuesta
    ADD CONSTRAINT fk_respenc_registro FOREIGN KEY (fk_registro) REFERENCES catedras.registro_asistencia(id_registro) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: respuesta_item fk_respitem_opcion; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.respuesta_item
    ADD CONSTRAINT fk_respitem_opcion FOREIGN KEY (fk_opcion) REFERENCES catedras.opcion_pregunta(id_opcion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: respuesta_item fk_respitem_pregunta; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.respuesta_item
    ADD CONSTRAINT fk_respitem_pregunta FOREIGN KEY (fk_pregunta) REFERENCES catedras.pregunta(id_pregunta) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: respuesta_item fk_respitem_respuesta; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.respuesta_item
    ADD CONSTRAINT fk_respitem_respuesta FOREIGN KEY (fk_respuesta) REFERENCES catedras.respuesta_encuesta(id_respuesta) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: rol_por_usuario fk_rolusr_rol; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.rol_por_usuario
    ADD CONSTRAINT fk_rolusr_rol FOREIGN KEY (fk_rol) REFERENCES catedras.rol(id_rol) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: rol_por_usuario fk_rolusr_usuario; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.rol_por_usuario
    ADD CONSTRAINT fk_rolusr_usuario FOREIGN KEY (fk_usuario) REFERENCES catedras.usuario(id_usuario) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: sesion fk_sesion_catedra; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.sesion
    ADD CONSTRAINT fk_sesion_catedra FOREIGN KEY (fk_catedra) REFERENCES catedras.catedra(id_catedra) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: sesion fk_sesion_encuesta; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.sesion
    ADD CONSTRAINT fk_sesion_encuesta FOREIGN KEY (fk_encuesta) REFERENCES catedras.encuesta(id_encuesta) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: sesion fk_sesion_modalidad; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.sesion
    ADD CONSTRAINT fk_sesion_modalidad FOREIGN KEY (fk_modalidad) REFERENCES catedras.modalidad(id_modalidad) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: sesion fk_sesion_periodo; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.sesion
    ADD CONSTRAINT fk_sesion_periodo FOREIGN KEY (fk_periodo) REFERENCES catedras.periodo_academico(id_periodo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: sesion fk_sesion_sede; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.sesion
    ADD CONSTRAINT fk_sesion_sede FOREIGN KEY (fk_sede) REFERENCES catedras.sede(id_sede) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: usuario fk_usuario_asistente; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.usuario
    ADD CONSTRAINT fk_usuario_asistente FOREIGN KEY (fk_asistente) REFERENCES catedras.asistente(id_asistente) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: vinculacion_asistente fk_vinculacion_asistente; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.vinculacion_asistente
    ADD CONSTRAINT fk_vinculacion_asistente FOREIGN KEY (fk_asistente) REFERENCES catedras.asistente(id_asistente) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: vinculacion_asistente fk_vinculacion_tipo; Type: FK CONSTRAINT; Schema: catedras; Owner: -
--

ALTER TABLE ONLY catedras.vinculacion_asistente
    ADD CONSTRAINT fk_vinculacion_tipo FOREIGN KEY (fk_tipo_vinculacion) REFERENCES catedras.tipo_vinculacion(id_tipo_vinculacion) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

\unrestrict iGIrEm2C6ihU2OQ4NKmBXjq43hqZ6dtgKdGH96L7lHkrgZKqIVandbpXbP5pLhS

