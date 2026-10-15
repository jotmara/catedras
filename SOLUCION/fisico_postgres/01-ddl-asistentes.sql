-- ============================================================================
--  01 · DDL - Bloque A · Asistentes e identidad
--  Tablas: tipo_documento · asistente · documento_asistente
--          tipo_vinculacion · vinculacion_asistente · consentimiento_datos
--
--  Las claves foraneas se declaran en el script 08.
-- ============================================================================

SET search_path TO catedras, public;

-- ----------------------------------------------------------------------------
-- tipo_documento
-- ----------------------------------------------------------------------------
CREATE TABLE tipo_documento (
    id_tipo_documento  varchar(5)   NOT NULL,
    nombre             varchar(60)  NOT NULL,
    activo             boolean      NOT NULL DEFAULT true,

    CONSTRAINT pk_tipo_documento     PRIMARY KEY (id_tipo_documento),
    CONSTRAINT uq_tipo_documento_nom UNIQUE (nombre)
);

COMMENT ON TABLE tipo_documento IS
    'Clase de documento de identidad. Catalogo cerrado que elimina las mas de '
    'diez formas de escribir "cedula" que trae el formulario actual.';

-- ----------------------------------------------------------------------------
-- asistente
--
-- La entidad central. Conserva el nombre que le dio el usuario experto.
-- ----------------------------------------------------------------------------
CREATE TABLE asistente (
    id_asistente          bigint        GENERATED ALWAYS AS IDENTITY,
    id_asis               varchar(15),
    nombres               varchar(100)  NOT NULL,
    apellidos             varchar(100)  NOT NULL,
    nombre_completo_asis  varchar(200),
    correo_institucional  citext,
    correo_personal       citext,
    celular               varchar(20),
    es_externo            boolean       NOT NULL DEFAULT false,
    activo                boolean       NOT NULL DEFAULT true,
    creado_en             timestamptz   NOT NULL DEFAULT now(),
    fk_lote_carga         bigint,

    CONSTRAINT pk_asistente        PRIMARY KEY (id_asistente),
    CONSTRAINT uq_asistente_asis   UNIQUE (id_asis),
    CONSTRAINT uq_asistente_corinst UNIQUE (correo_institucional),

    -- RN-03 · dominio del id_asis, corregido contra el dato real
    CONSTRAINT chk_asistente_idasis
        CHECK (id_asis IS NULL OR id_asis ~ '^[0-9A-Za-z]{5,15}$'),

    -- RN-01 · el interno tiene id_asis; el externo, no
    CONSTRAINT chk_asistente_externo
        CHECK ( (es_externo = false AND id_asis IS NOT NULL)
             OR (es_externo = true) ),

    -- Todo asistente necesita al menos una via de contacto para la clave
    CONSTRAINT chk_asistente_correo
        CHECK (correo_institucional IS NOT NULL OR correo_personal IS NOT NULL),

    CONSTRAINT chk_asistente_cor_inst_fmt
        CHECK (correo_institucional IS NULL OR correo_institucional LIKE '%@%.%'),
    CONSTRAINT chk_asistente_cor_pers_fmt
        CHECK (correo_personal IS NULL OR correo_personal LIKE '%@%.%')
);

COMMENT ON TABLE asistente IS
    'Persona que asiste a las catedras abiertas, de forma presencial o virtual. '
    'Puede ser estudiante, docente, administrativo, egresado, participante de '
    'rutas de formacion o publico externo.';

COMMENT ON COLUMN asistente.id_asis IS
    'Codigo de identificacion en el sistema ASIS. CORREGIDO respecto del '
    'archivo original: es ALFANUMERICO de hasta 15 caracteres, no 10 digitos. '
    'El maestro real trae 9.553 filas de 11 caracteres y valores como 1000513C. '
    'NULO significa que es un externo que no esta en el ASIS - decision '
    'REVISABLE, ver §3.1 del plan.';

COMMENT ON COLUMN asistente.nombre_completo_asis IS
    'El nombre tal como llego del ASIS, sin transformar. Permite rehacer la '
    'particion en nombres y apellidos si resulta equivocada.';

COMMENT ON COLUMN asistente.correo_personal IS
    'No es un caso raro: los participantes de Rutas de Paz NO tienen correo '
    'institucional, y es su unica via para recibir la clave.';

-- ----------------------------------------------------------------------------
-- documento_asistente
--
-- Atributo multivaluado convertido en tabla: 707 personas del maestro real
-- tienen mas de un numero de documento.
-- ----------------------------------------------------------------------------
CREATE TABLE documento_asistente (
    id_documento       bigint      GENERATED ALWAYS AS IDENTITY,
    fk_asistente       bigint      NOT NULL,
    fk_tipo_documento  varchar(5)  NOT NULL,
    numero             varchar(20) NOT NULL,
    vigente            boolean     NOT NULL DEFAULT true,
    registrado_en      timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT pk_documento_asistente PRIMARY KEY (id_documento),
    -- RN-04 · un documento identifica a lo sumo una persona (verificado: 0 casos)
    CONSTRAINT uq_documento_numero    UNIQUE (fk_tipo_documento, numero),
    CONSTRAINT chk_documento_numero   CHECK (numero ~ '^[0-9A-Za-z-]{4,20}$')
);

COMMENT ON TABLE documento_asistente IS
    'Numero de documento asociado a un asistente. Una persona puede tener '
    'varios a lo largo del tiempo; solo uno esta vigente (RN-05, indice '
    'parcial en el script 09). Sirve para resolver el ID cuando la persona '
    'no lo recuerda y digita la cedula.';

-- ----------------------------------------------------------------------------
-- tipo_vinculacion
--
-- Las dos columnas booleanas son el corazon de este catalogo: convierten
-- dos reglas del negocio en dato modificable con un UPDATE.
-- ----------------------------------------------------------------------------
CREATE TABLE tipo_vinculacion (
    id_tipo_vinculacion  varchar(15)  NOT NULL,
    nombre               varchar(60)  NOT NULL,
    es_interno           boolean      NOT NULL,
    exige_programa       boolean      NOT NULL DEFAULT true,
    activo               boolean      NOT NULL DEFAULT true,

    CONSTRAINT pk_tipo_vinculacion     PRIMARY KEY (id_tipo_vinculacion),
    CONSTRAINT uq_tipo_vinculacion_nom UNIQUE (nombre)
);

COMMENT ON COLUMN tipo_vinculacion.es_interno IS
    'Resuelve el informe 2 del enunciado - internos contra externos - con una '
    'agrupacion, en vez de un CASE de veinte lineas.';

COMMENT ON COLUMN tipo_vinculacion.exige_programa IS
    'FALSO en Rutas de Paz. Traduce la frase "ellos entrarian sin programa, '
    'pero solo ellos" (41:16) en un DATO. Habilitar una nueva excepcion es un '
    'UPDATE de una fila, no un ALTER TABLE en produccion.';

-- ----------------------------------------------------------------------------
-- vinculacion_asistente
--
-- Relacion N:M con atributos. fecha_ini ENTRA EN LA CLAVE PRIMARIA.
-- ----------------------------------------------------------------------------
CREATE TABLE vinculacion_asistente (
    fk_asistente         bigint      NOT NULL,
    fk_tipo_vinculacion  varchar(15) NOT NULL,
    fecha_ini            date        NOT NULL,
    fecha_fin            date,

    CONSTRAINT pk_vinculacion_asistente
        PRIMARY KEY (fk_asistente, fk_tipo_vinculacion, fecha_ini),
    CONSTRAINT chk_vinculacion_fechas
        CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_ini)
);

COMMENT ON TABLE vinculacion_asistente IS
    'Vinculacion institucional de una persona a lo largo del tiempo.';

COMMENT ON CONSTRAINT pk_vinculacion_asistente ON vinculacion_asistente IS
    'fecha_ini ENTRA EN LA CLAVE PRIMARIA. Sin ella, un egresado que se '
    'matricula en una maestria no podria volver a ser estudiante: el INSERT '
    'se rechazaria y el historico quedaria incompleto en silencio.';

-- ----------------------------------------------------------------------------
-- consentimiento_datos
-- ----------------------------------------------------------------------------
CREATE TABLE consentimiento_datos (
    id_consentimiento  bigint       GENERATED ALWAYS AS IDENTITY,
    fk_asistente       bigint       NOT NULL,
    version_politica   varchar(20)  NOT NULL,
    aceptado_en        timestamptz  NOT NULL DEFAULT now(),
    ip                 inet,
    canal              varchar(20)  NOT NULL DEFAULT 'WEB',

    CONSTRAINT pk_consentimiento     PRIMARY KEY (id_consentimiento),
    CONSTRAINT uq_consentimiento_ver UNIQUE (fk_asistente, version_politica),
    CONSTRAINT chk_consentimiento_canal
        CHECK (canal IN ('WEB', 'PRESENCIAL', 'CORREO', 'IMPORTADO'))
);

COMMENT ON TABLE consentimiento_datos IS
    'Ley 1581 de 2012. El sistema guarda documentos, nombres y correos '
    'personales de externos: el consentimiento es un HECHO que se registra, '
    'no un aviso en la pantalla.';

\echo '01 · Bloque A creado - 6 tablas'
