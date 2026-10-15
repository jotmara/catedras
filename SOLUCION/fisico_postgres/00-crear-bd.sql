-- ============================================================================
--  00 · Base de datos, extensiones y esquema
--  Proyecto: Catedras Abiertas - Universidad de San Buenaventura, Medellin
--  Motor:    PostgreSQL 14 o superior
--
--  Ejecutar conectado a la base 'postgres':
--      psql -U postgres -f 00-crear-bd.sql
-- ============================================================================

\set ON_ERROR_STOP on

-- La creacion de la base va fuera de transaccion.
DROP DATABASE IF EXISTS catedras;

CREATE DATABASE catedras
    WITH ENCODING  = 'UTF8'
         TEMPLATE  = template0
         LC_COLLATE = 'C'
         LC_CTYPE   = 'C';

COMMENT ON DATABASE catedras IS
    'Registro y control de asistencia a catedras abiertas. Sustituye el '
    'formulario anonimo y la migracion manual al ASIS.';

\connect catedras

-- ----------------------------------------------------------------------------
-- Extensiones
--
-- Cada una responde a una necesidad concreta del modelo; ninguna esta
-- por costumbre. Ver fisico_postgres/README.md, apartado 3.
-- ----------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS pgcrypto;    -- hash de la clave de acceso (RN-18)
CREATE EXTENSION IF NOT EXISTS btree_gist;  -- EXCLUDE de ventanas solapadas (RN-36)
CREATE EXTENSION IF NOT EXISTS citext;      -- correos sin distinguir mayusculas (RN-06)
CREATE EXTENSION IF NOT EXISTS unaccent;    -- normalizacion de texto libre
CREATE EXTENSION IF NOT EXISTS pg_trgm;     -- emparejamiento difuso de programas

-- ----------------------------------------------------------------------------
-- Esquema
-- ----------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS catedras;

COMMENT ON SCHEMA catedras IS
    'Todos los objetos del sistema. Se usa un esquema propio y no public '
    'para poder revocar permisos sobre public sin afectar al proyecto.';

-- unaccent() debe ser inmutable para poder indexarla; se envuelve.
CREATE OR REPLACE FUNCTION catedras.fn_normalizar(p_texto text)
RETURNS text
LANGUAGE sql IMMUTABLE PARALLEL SAFE
AS $$
    SELECT lower(trim(regexp_replace(
               public.unaccent('public.unaccent', coalesce(p_texto, '')),
               '\s+', ' ', 'g')));
$$;

COMMENT ON FUNCTION catedras.fn_normalizar(text) IS
    'Baja a minusculas, quita tildes y colapsa espacios. Es la funcion con que '
    'se compara el texto libre de los formularios contra alias_programa. '
    'Es IMMUTABLE a proposito: si no, no se puede construir el indice GIN.';

SET search_path TO catedras, public;

\echo '00 · Base catedras creada, con 5 extensiones y el esquema catedras'
