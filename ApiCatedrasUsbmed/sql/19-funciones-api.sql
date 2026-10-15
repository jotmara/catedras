-- ============================================================================
--  19 · Funciones envoltorio para la API
--
--  Este script pertenece a ApiCatedrasUsbmed, no al diseno de la base: son
--  envoltorios delgados sobre los procedimientos del script 11.
--
--  POR QUE EXISTEN
--  Los procedimientos del modelo usan parametros INOUT y se invocan con CALL.
--  Npgsql y Dapper no pueden recoger esos valores de salida de forma portable:
--  CALL no devuelve un conjunto de resultados. Estas funciones hacen el CALL por
--  dentro y DEVUELVEN el resultado, que es lo que un SELECT si puede leer.
--
--  NO duplican logica. Cada una es un CALL y un RETURN: toda la regla de negocio
--  sigue viviendo en los procedimientos originales.
--
--  Aplicar despues de ejecutar-todo.sql:
--      psql -U postgres -d catedras -f sql/19-funciones-api.sql
-- ============================================================================

SET search_path TO catedras, public;

-- NOTA sobre SET search_path en cada funcion:
-- el search_path de este script NO se hereda dentro del cuerpo de una funcion: alli rige
-- el de la SESION QUE LLAMA. La API se conecta sin fijarlo, asi que sin la calificacion
-- catedras.sp_* y sin el SET de cada funcion, PostgreSQL responde
-- "no existe el procedimiento sp_emitir_enlace(...)" aunque exista.

-- ---------------------------------------------------------------------------
-- fn_solicitar_clave_api
-- Devuelve la clave EN CLARO para que la API la envie por correo. La base sigue
-- guardando solo el hash. La API no la propaga mas alla del servicio de correo.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_solicitar_clave_api(
    p_identificador text,
    p_token         uuid,
    p_ip            inet DEFAULT NULL)
RETURNS TABLE (id_clave bigint, clave text, enviado_a text)
LANGUAGE plpgsql
SET search_path = catedras, public
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

COMMENT ON FUNCTION fn_solicitar_clave_api(text, uuid, inet) IS
    'Envoltorio de sp_solicitar_clave para la API. RN-17.';

-- ---------------------------------------------------------------------------
-- fn_validar_clave_api
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_validar_clave_api(
    p_id_clave   bigint,
    p_clave      text,
    p_ip         inet DEFAULT NULL,
    p_user_agent text DEFAULT NULL)
RETURNS bigint
LANGUAGE plpgsql
SET search_path = catedras, public
AS $$
DECLARE
    v_registro bigint;
BEGIN
    CALL catedras.sp_validar_clave_y_registrar(p_id_clave, p_clave, p_ip, p_user_agent, v_registro);
    RETURN v_registro;
END;
$$;

-- ---------------------------------------------------------------------------
-- fn_responder_encuesta_api
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_responder_encuesta_api(
    p_id_registro bigint,
    p_respuestas  jsonb)
RETURNS bigint
LANGUAGE plpgsql
SET search_path = catedras, public
AS $$
DECLARE
    v_respuesta bigint;
BEGIN
    CALL catedras.sp_responder_encuesta(p_id_registro, p_respuestas, v_respuesta);
    RETURN v_respuesta;
END;
$$;

-- ---------------------------------------------------------------------------
-- fn_emitir_enlace_api
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_emitir_enlace_api(
    p_id_sesion       bigint,
    p_minutos_antes   integer DEFAULT NULL,
    p_minutos_despues integer DEFAULT NULL,
    p_usuario         bigint  DEFAULT NULL)
RETURNS bigint
LANGUAGE plpgsql
SET search_path = catedras, public
AS $$
DECLARE
    v_enlace bigint;
BEGIN
    CALL catedras.sp_emitir_enlace(p_id_sesion, p_minutos_antes, p_minutos_despues, p_usuario, v_enlace);
    RETURN v_enlace;
END;
$$;

-- ---------------------------------------------------------------------------
-- fn_generar_lote_api
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_generar_lote_api(
    p_id_sesion bigint,
    p_usuario   bigint DEFAULT NULL)
RETURNS bigint
LANGUAGE plpgsql
SET search_path = catedras, public
AS $$
DECLARE
    v_lote bigint;
BEGIN
    CALL catedras.sp_generar_lote_migracion(p_id_sesion, p_usuario, v_lote);
    RETURN v_lote;
END;
$$;

-- ---------------------------------------------------------------------------
-- Permisos: el camino publico solo necesita las tres del flujo de acceso.
-- ---------------------------------------------------------------------------
GRANT EXECUTE ON FUNCTION fn_solicitar_clave_api(text, uuid, inet)        TO rol_app_registro;
GRANT EXECUTE ON FUNCTION fn_validar_clave_api(bigint, text, inet, text)  TO rol_app_registro;
GRANT EXECUTE ON FUNCTION fn_responder_encuesta_api(bigint, jsonb)        TO rol_app_registro;
GRANT EXECUTE ON FUNCTION fn_emitir_enlace_api(bigint, integer, integer, bigint) TO rol_admin_catedras;
GRANT EXECUTE ON FUNCTION fn_generar_lote_api(bigint, bigint)             TO rol_admin_catedras;

\echo '19 · Funciones envoltorio de la API creadas'

-- ============================================================================
--  ARREGLO DE FONDO · search_path de las rutinas del modelo
--
--  Las rutinas de 11-funciones-procedimientos.sql referencian las tablas SIN
--  calificar y se crearon bajo un `SET search_path` de SCRIPT. Ese SET es de
--  SESION: NO queda horneado en la funcion. Llamadas desde un cliente que no lo
--  fija -como esta API-, PostgreSQL responde "no existe la relacion
--  registro_asistencia" aunque exista.
--
--  Se detecto ejecutando el recorrido completo por HTTP, no compilando.
--
--  Esto lo deja resuelto en la propia base. La API ademas fija Search Path en su
--  cadena de conexion, como cinturon.
-- ============================================================================

DO $$
DECLARE
    r record;
BEGIN
    FOR r IN
        SELECT p.oid::regprocedure AS firma, p.prokind
          FROM pg_proc p
          JOIN pg_namespace n ON n.oid = p.pronamespace
         WHERE n.nspname = 'catedras'
           AND p.proname LIKE ANY (ARRAY['fn\_%', 'sp\_%'])
           AND NOT EXISTS (
                 SELECT 1 FROM unnest(coalesce(p.proconfig, '{}')) c
                  WHERE c LIKE 'search_path=%')
    LOOP
        EXECUTE format('%s %s SET search_path = catedras, public',
                       CASE r.prokind WHEN 'p' THEN 'ALTER PROCEDURE' ELSE 'ALTER FUNCTION' END,
                       r.firma);
    END LOOP;
END $$;

\echo '19b · search_path fijado en todas las rutinas del esquema catedras'
