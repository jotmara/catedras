-- ============================================================================
--  17 · Roles de base de datos y permisos
--
--  Los permisos se aprueban demostrando un FALLO: al final hay un bloque de
--  pruebas que DEBE dar error. Un permiso que no se ha visto fallar no esta
--  comprobado.
-- ============================================================================

SET search_path TO catedras, public;

-- ---------------------------------------------------------------------------
-- Roles de grupo
-- ---------------------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_admin_catedras') THEN
        CREATE ROLE rol_admin_catedras NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_coordinador') THEN
        CREATE ROLE rol_coordinador NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_consulta') THEN
        CREATE ROLE rol_consulta NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_app_registro') THEN
        CREATE ROLE rol_app_registro NOLOGIN;
    END IF;
END $$;

GRANT USAGE ON SCHEMA catedras TO rol_admin_catedras, rol_coordinador,
                                  rol_consulta, rol_app_registro;

-- ---------------------------------------------------------------------------
-- rol_consulta · SOLO LECTURA
-- ---------------------------------------------------------------------------
GRANT SELECT ON ALL TABLES IN SCHEMA catedras TO rol_consulta;
REVOKE SELECT ON clave_acceso, bitacora FROM rol_consulta;

COMMENT ON ROLE rol_consulta IS
    'Solo lectura. Se le NIEGA clave_acceso y bitacora: los hash de las claves '
    'y el detalle de auditoria no son informacion de consulta.';

-- ---------------------------------------------------------------------------
-- rol_coordinador · lectura, mas registro manual
-- ---------------------------------------------------------------------------
GRANT SELECT ON ALL TABLES IN SCHEMA catedras TO rol_coordinador;
REVOKE SELECT ON clave_acceso FROM rol_coordinador;
GRANT INSERT, UPDATE ON catedra, sesion, enlace_registro, registro_asistencia,
                        encuesta, pregunta, opcion_pregunta TO rol_coordinador;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA catedras TO rol_coordinador;

-- ---------------------------------------------------------------------------
-- rol_app_registro · lo MINIMO que necesita la aplicacion web
--
-- No se le da SELECT sobre asistente entero: entra por los procedimientos.
-- ---------------------------------------------------------------------------
GRANT SELECT ON sesion, catedra, enlace_registro, modalidad, sede,
                encuesta, pregunta, opcion_pregunta, tipo_pregunta,
                parametro TO rol_app_registro;
GRANT INSERT ON registro_asistencia, respuesta_encuesta, respuesta_item,
                consentimiento_datos TO rol_app_registro;
GRANT SELECT, INSERT, UPDATE ON clave_acceso TO rol_app_registro;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA catedras TO rol_app_registro;

GRANT EXECUTE ON FUNCTION fn_resolver_asistente(text)          TO rol_app_registro;
GRANT EXECUTE ON FUNCTION fn_siguiente_reunion(char)           TO rol_app_registro;
GRANT EXECUTE ON PROCEDURE sp_solicitar_clave(text, uuid, inet, bigint, text, text)
                                                               TO rol_app_registro;
GRANT EXECUTE ON PROCEDURE sp_validar_clave_y_registrar(bigint, text, inet, text, bigint)
                                                               TO rol_app_registro;
GRANT EXECUTE ON PROCEDURE sp_responder_encuesta(bigint, jsonb, bigint)
                                                               TO rol_app_registro;

COMMENT ON ROLE rol_app_registro IS
    'La aplicacion web. NO tiene DELETE sobre nada, ni SELECT sobre asistente: '
    'resuelve la identidad llamando a fn_resolver_asistente, que devuelve solo '
    'un identificador. Asi la aplicacion no puede volcarse el maestro de '
    '14.808 personas.';

-- ---------------------------------------------------------------------------
-- rol_admin_catedras · todo menos borrar evidencia
-- ---------------------------------------------------------------------------
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA catedras TO rol_admin_catedras;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA catedras TO rol_admin_catedras;
GRANT EXECUTE ON ALL ROUTINES IN SCHEMA catedras TO rol_admin_catedras;

-- RN-32 · nadie borra. Ni el administrador.
REVOKE DELETE ON ALL TABLES IN SCHEMA catedras FROM rol_admin_catedras,
                                                    rol_coordinador,
                                                    rol_consulta,
                                                    rol_app_registro;

-- La bitacora no se modifica ni se borra, tampoco por el administrador
REVOKE UPDATE ON bitacora FROM rol_admin_catedras, rol_coordinador;

-- ---------------------------------------------------------------------------
-- Usuarios de ejemplo
-- ---------------------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'u_gestor_catedras') THEN
        CREATE ROLE u_gestor_catedras LOGIN PASSWORD 'cambiar-en-produccion';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'u_app_web') THEN
        CREATE ROLE u_app_web LOGIN PASSWORD 'cambiar-en-produccion';
    END IF;
END $$;

GRANT rol_admin_catedras TO u_gestor_catedras;
GRANT rol_app_registro   TO u_app_web;

-- ============================================================================
--  PRUEBAS · estas TRES deben FALLAR. Si alguna pasa, los permisos estan mal.
-- ============================================================================
\echo ''
\echo '=== Pruebas de permisos: las tres deben dar error ==='

SET ROLE u_app_web;

\echo '--- 1 · la aplicacion NO puede volcarse el maestro de personas ---'
DO $$
BEGIN
    PERFORM count(*) FROM catedras.asistente;
    RAISE EXCEPTION 'FALLO DE SEGURIDAD: la aplicacion pudo leer asistente';
EXCEPTION
    WHEN insufficient_privilege THEN
        RAISE NOTICE 'CORRECTO: permiso denegado sobre asistente';
END $$;

\echo '--- 2 · nadie borra registros de asistencia (RN-32) ---'
DO $$
BEGIN
    DELETE FROM catedras.registro_asistencia WHERE false;
    RAISE EXCEPTION 'FALLO DE SEGURIDAD: se permitio DELETE';
EXCEPTION
    WHEN insufficient_privilege THEN
        RAISE NOTICE 'CORRECTO: DELETE denegado';
END $$;

RESET ROLE;
SET ROLE u_gestor_catedras;

\echo '--- 3 · ni el administrador puede alterar la bitacora ---'
DO $$
BEGIN
    UPDATE catedras.bitacora SET operacion = 'INSERT' WHERE false;
    RAISE EXCEPTION 'FALLO DE SEGURIDAD: se permitio UPDATE sobre bitacora';
EXCEPTION
    WHEN insufficient_privilege THEN
        RAISE NOTICE 'CORRECTO: UPDATE sobre bitacora denegado';
END $$;

RESET ROLE;

\echo '17 · Roles y permisos aplicados, con sus tres pruebas'
