-- ============================================================================
--  03 · DDL - Bloque C · Catedras, sesiones y sedes
--  Tablas: tipo_evento · sede · modalidad · dependencia
--          catedra · sesion · ponencia
-- ============================================================================

SET search_path TO catedras, public;

-- ----------------------------------------------------------------------------
-- tipo_evento · los 8 codigos reales del ASIS
-- ----------------------------------------------------------------------------
CREATE TABLE tipo_evento (
    id_tipo_evento  char(4)      NOT NULL,
    nombre          varchar(80)  NOT NULL,
    activo          boolean      NOT NULL DEFAULT true,

    CONSTRAINT pk_tipo_evento PRIMARY KEY (id_tipo_evento)
);

COMMENT ON TABLE tipo_evento IS
    'Clasificacion del evento en el ASIS. Ocho valores observados en las 5.711 '
    'filas reales: CAAB (5.449), DLLH (188), DEPR (44), SLDI (16), ARCU (5), '
    'MTG (5), DIIB (3), EIIC (1).';

-- ----------------------------------------------------------------------------
-- sede
-- ----------------------------------------------------------------------------
CREATE TABLE sede (
    id_sede     varchar(15)   NOT NULL,
    nombre      varchar(80)   NOT NULL,
    direccion   varchar(200),
    es_virtual  boolean       NOT NULL DEFAULT false,
    activo      boolean       NOT NULL DEFAULT true,

    CONSTRAINT pk_sede        PRIMARY KEY (id_sede),
    CONSTRAINT uq_sede_nombre UNIQUE (nombre)
);

COMMENT ON TABLE sede IS
    'Lugar fisico o virtual donde se dicta una sesion. Aparece porque "puede '
    'que una catedra este en San Benito, otra este virtual y otra este en '
    'Bello" (1:03:33): LA SEDE ES LO QUE DISTINGUE DOS CATEDRAS A LA MISMA '
    'HORA. Como texto libre en sesion, el informe por sede no se puede escribir.';

-- ----------------------------------------------------------------------------
-- modalidad · gobierna comportamiento, no es una etiqueta
-- ----------------------------------------------------------------------------
CREATE TABLE modalidad (
    id_modalidad    varchar(15)  NOT NULL,
    nombre          varchar(60)  NOT NULL,
    canal_difusion  varchar(10)  NOT NULL,
    activo          boolean      NOT NULL DEFAULT true,

    CONSTRAINT pk_modalidad          PRIMARY KEY (id_modalidad),
    CONSTRAINT chk_modalidad_canal   CHECK (canal_difusion IN ('QR', 'ENLACE', 'AMBOS'))
);

COMMENT ON COLUMN modalidad.canal_difusion IS
    'QR si es presencial, ENLACE si es virtual. Traduce la regla del profesor '
    'Hugo Nelson en 1:06:53: "cuando es virtual enviamos el enlace; si es '
    'presencial, el QR". Se hace cumplir en el script 10 (RN-13).';

-- ----------------------------------------------------------------------------
-- dependencia · reflexiva -> arbol
-- ----------------------------------------------------------------------------
CREATE TABLE dependencia (
    id_dependencia         varchar(15)   NOT NULL,
    nombre                 varchar(120)  NOT NULL,
    fk_dependencia_padre   varchar(15),
    activo                 boolean       NOT NULL DEFAULT true,

    CONSTRAINT pk_dependencia        PRIMARY KEY (id_dependencia),
    CONSTRAINT uq_dependencia_nombre UNIQUE (nombre),
    CONSTRAINT chk_dependencia_padre CHECK (fk_dependencia_padre <> id_dependencia)
);

-- ----------------------------------------------------------------------------
-- catedra
-- ----------------------------------------------------------------------------
CREATE TABLE catedra (
    id_catedra       bigint        GENERATED ALWAYS AS IDENTITY,
    id_evento_asis   char(9)       NOT NULL,
    nombre           varchar(200)  NOT NULL,
    nombre_asis      varchar(30)   GENERATED ALWAYS AS (left(nombre, 30)) STORED,
    fk_tipo_evento   char(4)       NOT NULL,
    fk_dependencia   varchar(15),
    activo           boolean       NOT NULL DEFAULT true,
    creado_en        timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT pk_catedra       PRIMARY KEY (id_catedra),
    CONSTRAINT uq_catedra_asis  UNIQUE (id_evento_asis),
    -- RN-09 · nueve caracteres, con ceros a la izquierda
    CONSTRAINT chk_catedra_asis CHECK (id_evento_asis ~ '^[0-9]{9}$')
);

COMMENT ON COLUMN catedra.id_evento_asis IS
    'Identificador del evento en el ASIS. char(9) CON CEROS A LA IZQUIERDA: '
    '000035392. Como entero se convierte en 35392 y deja de servir para la '
    'carga.';

COMMENT ON COLUMN catedra.nombre_asis IS
    'DERIVADO: los 30 primeros caracteres, que es lo que acepta el ASIS. El '
    'listado real trae nombres cortados a mitad de palabra - "REMOCION DE '
    'METALES PESADOS DE", "CURSO FORMATIVO LOGICO MATEMAT". Guardando el '
    'largo y derivando el corto, no se pierde informacion. Al reves, si.';

-- ----------------------------------------------------------------------------
-- sesion · ENTIDAD DEBIL de catedra
-- ----------------------------------------------------------------------------
CREATE TABLE sesion (
    id_sesion            bigint        GENERATED ALWAYS AS IDENTITY,
    fk_catedra           bigint        NOT NULL,
    numero_reunion       smallint      NOT NULL,
    numero_reunion_asis  smallint,
    titulo               varchar(200),
    inicio               timestamptz   NOT NULL,
    fin                  timestamptz   NOT NULL,
    fk_modalidad         varchar(15)   NOT NULL,
    fk_sede              varchar(15)   NOT NULL,
    fk_periodo           char(6)       NOT NULL,
    fk_encuesta          bigint,
    lugar                varchar(200),
    enlace_virtual       varchar(300),
    cupo                 integer,
    estado               varchar(15)   NOT NULL DEFAULT 'PROGRAMADA',
    creado_en            timestamptz   NOT NULL DEFAULT now(),

    CONSTRAINT pk_sesion PRIMARY KEY (id_sesion),
    -- RN-10 · el consecutivo por catedra. Verificado: el par es unico en las
    --         5.711 filas reales de USBME_LCONTROL_CATEDRAS
    CONSTRAINT uq_sesion_reunion  UNIQUE (fk_catedra, numero_reunion),
    CONSTRAINT chk_sesion_reunion CHECK (numero_reunion >= 1),
    -- RN-37
    CONSTRAINT chk_sesion_fechas  CHECK (fin > inicio),
    CONSTRAINT chk_sesion_cupo    CHECK (cupo IS NULL OR cupo > 0),
    CONSTRAINT chk_sesion_estado
        CHECK (estado IN ('PROGRAMADA', 'ABIERTA', 'CERRADA', 'MIGRADA'))
);

COMMENT ON TABLE sesion IS
    'Cada una de las reuniones en que se dicta una catedra. ENTIDAD DEBIL: la '
    '"reunion 3" no significa nada suelta, es la reunion 3 DE UN EVENTO.';

COMMENT ON COLUMN sesion.numero_reunion IS
    'El numero de reunion con que la sesion viaja al ASIS. Si no se indica, el '
    'disparador del script 10 PROPONE el maximo de la catedra mas uno - y eso '
    'elimina el paso 2 del manual para las catedras nuevas. Para las que ya '
    'existen en el ASIS, el valor bueno es numero_reunion_asis: el dato real '
    'demuestra que el ASIS no numera por evento desde 1.';

COMMENT ON COLUMN sesion.numero_reunion_asis IS
    'El numero de reunion segun el ASIS. DECISION RESUELTA POR EL DATO: el ASIS '
    'lleva un contador propio - de 5.481 eventos con una sola reunion, solo 588 '
    'tienen el numero 1, y los demas llegan hasta 4348. Cuando esta columna '
    'tiene valor, MANDA sobre numero_reunion.';

-- ----------------------------------------------------------------------------
-- ponencia · N:M con atributo
-- ----------------------------------------------------------------------------
CREATE TABLE ponencia (
    fk_sesion     bigint       NOT NULL,
    fk_asistente  bigint       NOT NULL,
    rol           varchar(15)  NOT NULL DEFAULT 'PONENTE',

    CONSTRAINT pk_ponencia  PRIMARY KEY (fk_sesion, fk_asistente, rol),
    CONSTRAINT chk_ponencia_rol
        CHECK (rol IN ('PONENTE', 'MODERADOR', 'INVITADO', 'ORGANIZADOR'))
);

\echo '03 · Bloque C creado - 7 tablas'
