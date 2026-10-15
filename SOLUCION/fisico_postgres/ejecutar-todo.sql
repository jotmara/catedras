-- ============================================================================
--  Ejecuta la solucion completa, en orden.
--
--      cd SOLUCION/fisico_postgres
--      python preparar-datos.py          <- genera datos/*.csv desde los Excel
--      psql -U postgres -f ejecutar-todo.sql
--
--  El script 00 crea la base y se conecta a ella; los demas corren alli.
--  El 17 crea roles: hace falta un usuario con privilegio de creacion de roles.
-- ============================================================================

\set ON_ERROR_STOP on
\timing on

\echo '=== 00 · Base de datos, extensiones y esquema ============================'
\i 00-crear-bd.sql

\echo '=== 01 · DDL asistentes e identidad ======================================'
\i 01-ddl-asistentes.sql
\echo '=== 02 · DDL estructura academica ========================================'
\i 02-ddl-academico.sql
\echo '=== 03 · DDL catedras, sesiones y sedes =================================='
\i 03-ddl-catedras.sql
\echo '=== 04 · DDL acceso y registro ==========================================='
\i 04-ddl-registro.sql
\echo '=== 05 · DDL encuesta ===================================================='
\i 05-ddl-encuesta.sql
\echo '=== 06 · DDL integracion con el ASIS ====================================='
\i 06-ddl-integracion.sql
\echo '=== 07 · DDL seguridad y configuracion ==================================='
\i 07-ddl-seguridad.sql

\echo '=== 08 · Claves foraneas ================================================='
\i 08-constraints-fk.sql

\echo '=== 10 · Disparadores ===================================================='
-- Van antes de los datos: la carga los ejercita, que es como se comprueban.
\i 10-triggers.sql

\echo '=== 11 · Funciones y procedimientos ======================================'
\i 11-funciones-procedimientos.sql

\echo '=== 12 · Catalogos ======================================================='
\i 12-datos-catalogos.sql

\echo '=== 13 · Carga REAL del ASIS ============================================='
\i 13-carga-asis.sql

\echo '=== 15 · Vistas =========================================================='
\i 15-vistas.sql

\echo '=== 14 · Datos de prueba ================================================='
-- Va DESPUES de las vistas porque algunas comprobaciones las usan.
\i 14-datos-prueba.sql

\echo '=== 09 · Indices ========================================================='
-- Van al final, con los datos ya cargados: crear un indice sobre una tabla
-- vacia no dice nada, y el plan de ejecucion sin datos es inutil.
\i 09-indices.sql
ANALYZE;

\echo '=== 17 · Roles y permisos ==============================================='
\i 17-usuarios-permisos.sql

\echo '=== 16 · Los 20 informes ================================================'
\i 16-consultas-informes.sql

-- ============================================================================
\echo ''
\echo '=== VERIFICACIONES FINALES =============================================='
-- ============================================================================

\echo '--- Objetos creados ---'
SELECT (SELECT count(*) FROM information_schema.tables
         WHERE table_schema='catedras' AND table_type='BASE TABLE')   AS tablas,
       (SELECT count(*) FROM information_schema.views
         WHERE table_schema='catedras')                                AS vistas,
       (SELECT count(*) FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace
         WHERE n.nspname='catedras' AND c.contype='f')                 AS claves_foraneas,
       (SELECT count(*) FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace
         WHERE n.nspname='catedras' AND c.contype='c')                 AS checks,
       (SELECT count(*) FROM pg_trigger t JOIN pg_class cl ON cl.oid=t.tgrelid
          JOIN pg_namespace n ON n.oid=cl.relnamespace
         WHERE n.nspname='catedras' AND NOT t.tgisinternal)            AS disparadores;

\echo '--- Volumenes cargados, contra lo medido en los Excel ---'
SELECT 'catedras'   AS objeto, count(*) AS filas, 5497  AS esperado FROM catedras.catedra
UNION ALL SELECT 'sesiones',   count(*), 5714  FROM catedras.sesion
UNION ALL SELECT 'programas',  count(*), 105   FROM catedras.programa_academico
UNION ALL SELECT 'asistentes', count(*), 14811 FROM catedras.asistente
UNION ALL SELECT 'documentos', count(*), 15517 FROM catedras.documento_asistente
UNION ALL SELECT 'registros',  count(*), 166   FROM catedras.registro_asistencia;

\echo '--- CONTROLES · las cuatro deben dar CERO ---'
SELECT 'registros fuera de ventana (RN-15)' AS control,
       (SELECT count(*) FROM catedras.v_control_ventana) AS debe_ser_cero
UNION ALL
SELECT 'pares (catedra, reunion) duplicados (RN-10)',
       (SELECT count(*) FROM (SELECT fk_catedra, numero_reunion FROM catedras.sesion
                               GROUP BY 1,2 HAVING count(*)>1) q)
UNION ALL
SELECT 'encuestas completas sin ningun item (R29)',
       (SELECT count(*) FROM catedras.respuesta_encuesta re
         WHERE re.completa AND NOT EXISTS (SELECT 1 FROM catedras.respuesta_item ri
                                            WHERE ri.fk_respuesta = re.id_respuesta))
UNION ALL
SELECT 'externos colados en el archivo del ASIS (RN-08)',
       (SELECT count(*) FROM catedras.detalle_migracion dm
          JOIN catedras.registro_asistencia r ON r.id_registro = dm.fk_registro
          JOIN catedras.asistente a ON a.id_asistente = r.fk_asistente
         WHERE a.es_externo OR a.id_asis IS NULL);

\echo ''
\echo '=== LISTO ==============================================================='
