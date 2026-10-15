-- ============================================================================
--  07 · DDL - Bloque G · Seguridad, configuracion y auditoria
--  Tablas: usuario · rol · rol_por_usuario · parametro · bitacora
-- ============================================================================

SET search_path TO catedras, public;

-- ----------------------------------------------------------------------------
-- usuario
--
-- El administrador ES una persona del ASIS: se apoya en asistente y asi no se
-- duplican nombres ni correos.
-- ----------------------------------------------------------------------------
CREATE TABLE usuario (
    id_usuario     bigint       GENERATED ALWAYS AS IDENTITY,
    fk_asistente   bigint       NOT NULL,
    usuario        varchar(40)  NOT NULL,
    clave_hash     varchar(255) NOT NULL,
    activo         boolean      NOT NULL DEFAULT true,
    ultimo_acceso  timestamptz,
    creado_en      timestamptz  NOT NULL DEFAULT now(),

    CONSTRAINT pk_usuario         PRIMARY KEY (id_usuario),
    CONSTRAINT uq_usuario_login   UNIQUE (usuario),
    -- 1:1 con asistente
    CONSTRAINT uq_usuario_persona UNIQUE (fk_asistente),
    CONSTRAINT chk_usuario_login  CHECK (usuario ~ '^[a-z0-9._-]{4,40}$')
);

COMMENT ON COLUMN usuario.clave_hash IS
    'RN-34 · Nunca la clave en claro. Aqui se guarda un hash con sal; el '
    'algoritmo lo decide la aplicacion (bcrypt o argon2 preferiblemente).';

-- ----------------------------------------------------------------------------
-- rol
-- ----------------------------------------------------------------------------
CREATE TABLE rol (
    id_rol       varchar(20)  NOT NULL,
    nombre       varchar(60)  NOT NULL,
    descripcion  varchar(200),

    CONSTRAINT pk_rol        PRIMARY KEY (id_rol),
    CONSTRAINT uq_rol_nombre UNIQUE (nombre)
);

-- ----------------------------------------------------------------------------
-- rol_por_usuario · la misma leccion que vinculacion_asistente
-- ----------------------------------------------------------------------------
CREATE TABLE rol_por_usuario (
    fk_usuario  bigint       NOT NULL,
    fk_rol      varchar(20)  NOT NULL,
    fecha_ini   date         NOT NULL DEFAULT current_date,
    fecha_fin   date,

    CONSTRAINT pk_rol_por_usuario PRIMARY KEY (fk_usuario, fk_rol, fecha_ini),
    CONSTRAINT chk_rol_usuario_fechas
        CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_ini)
);

COMMENT ON CONSTRAINT pk_rol_por_usuario ON rol_por_usuario IS
    'RN-31 · fecha_ini EN LA CLAVE PRIMARIA. Sin ella, quien fue administrador, '
    'dejo de serlo y vuelve, quedaria bloqueado para siempre. Es el mismo '
    'error que en vinculacion_asistente, y falla igual de silenciosamente.';

-- ----------------------------------------------------------------------------
-- parametro
-- ----------------------------------------------------------------------------
CREATE TABLE parametro (
    clave               varchar(60)  NOT NULL,
    valor               varchar(200) NOT NULL,
    tipo_dato           varchar(15)  NOT NULL DEFAULT 'TEXTO',
    descripcion         varchar(300) NOT NULL,
    fk_usuario_modifica bigint,
    modificado_en       timestamptz  NOT NULL DEFAULT now(),

    CONSTRAINT pk_parametro PRIMARY KEY (clave),
    CONSTRAINT chk_parametro_tipo
        CHECK (tipo_dato IN ('TEXTO', 'ENTERO', 'BOOLEANO', 'FECHA', 'DECIMAL'))
);

COMMENT ON TABLE parametro IS
    'Configuracion que el administrador cambia sin tocar el codigo. Del .docx: '
    '"el administrador configura o parametriza los valores que considere".';

-- ----------------------------------------------------------------------------
-- bitacora
-- ----------------------------------------------------------------------------
CREATE TABLE bitacora (
    id_bitacora    bigint       GENERATED ALWAYS AS IDENTITY,
    ocurrido_en    timestamptz  NOT NULL DEFAULT now(),
    usuario_bd     name         NOT NULL DEFAULT current_user,
    fk_usuario     bigint,
    nombre_tabla   varchar(63)  NOT NULL,
    operacion      varchar(10)  NOT NULL,
    llave          varchar(100),
    datos_antes    jsonb,
    datos_despues  jsonb,

    CONSTRAINT pk_bitacora PRIMARY KEY (id_bitacora),
    CONSTRAINT chk_bitacora_operacion
        CHECK (operacion IN ('INSERT', 'UPDATE', 'DELETE'))
);

COMMENT ON TABLE bitacora IS
    'RN-35 · Registro de toda modificacion sobre datos sensibles, con el antes '
    'y el despues en jsonb. La alternativa - una tabla espejo por cada tabla '
    'auditada - costaria treinta y siete tablas mas.';

\echo '07 · Bloque G creado - 5 tablas'
