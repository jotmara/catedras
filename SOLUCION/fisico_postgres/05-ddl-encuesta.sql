-- ============================================================================
--  05 · DDL - Bloque E · Encuesta de calidad parametrizable
--  Tablas: encuesta · tipo_pregunta · pregunta · opcion_pregunta
--          respuesta_encuesta · respuesta_item
--
--  Cuatro tablas de definicion y dos de respuesta, en vez de cinco columnas
--  fijas, porque el enunciado dice que "el administrador configura o
--  parametriza los valores que considere".
-- ============================================================================

SET search_path TO catedras, public;

-- ----------------------------------------------------------------------------
-- encuesta
-- ----------------------------------------------------------------------------
CREATE TABLE encuesta (
    id_encuesta     bigint       GENERATED ALWAYS AS IDENTITY,
    nombre          varchar(120) NOT NULL,
    version         smallint     NOT NULL DEFAULT 1,
    vigente_desde   date         NOT NULL DEFAULT current_date,
    vigente_hasta   date,
    activa          boolean      NOT NULL DEFAULT true,

    CONSTRAINT pk_encuesta        PRIMARY KEY (id_encuesta),
    CONSTRAINT uq_encuesta_ver    UNIQUE (nombre, version),
    CONSTRAINT chk_encuesta_ver   CHECK (version >= 1),
    CONSTRAINT chk_encuesta_vig   CHECK (vigente_hasta IS NULL
                                      OR vigente_hasta >= vigente_desde)
);

COMMENT ON TABLE encuesta IS
    'Cuestionario de calidad en una version concreta. Se versiona porque con '
    'columnas fijas, cambiar una pregunta romperia la comparabilidad '
    'historica: las respuestas viejas quedarian bajo un enunciado que no es el '
    'que se pregunto.';

-- ----------------------------------------------------------------------------
-- tipo_pregunta · decide DONDE se guarda la respuesta
-- ----------------------------------------------------------------------------
CREATE TABLE tipo_pregunta (
    id_tipo_pregunta  varchar(15)  NOT NULL,
    nombre            varchar(60)  NOT NULL,
    guarda_numero     boolean      NOT NULL DEFAULT false,
    guarda_texto      boolean      NOT NULL DEFAULT false,
    guarda_opcion     boolean      NOT NULL DEFAULT false,

    CONSTRAINT pk_tipo_pregunta PRIMARY KEY (id_tipo_pregunta),
    -- Exactamente uno de los tres destinos
    CONSTRAINT chk_tipo_pregunta_destino
        CHECK (guarda_numero::int + guarda_texto::int + guarda_opcion::int = 1)
);

COMMENT ON TABLE tipo_pregunta IS
    'Clase de pregunta. Las tres columnas booleanas dicen en cual de las tres '
    'columnas de valor de respuesta_item se guarda la respuesta. Es lo que '
    'permite que la regla condicional (RN-25) sea DATO y no codigo.';

-- ----------------------------------------------------------------------------
-- pregunta
-- ----------------------------------------------------------------------------
CREATE TABLE pregunta (
    id_pregunta       bigint       GENERATED ALWAYS AS IDENTITY,
    fk_encuesta       bigint       NOT NULL,
    enunciado         varchar(300) NOT NULL,
    orden             smallint     NOT NULL,
    fk_tipo_pregunta  varchar(15)  NOT NULL,
    obligatoria       boolean      NOT NULL DEFAULT false,
    valor_min         smallint,
    valor_max         smallint,

    CONSTRAINT pk_pregunta      PRIMARY KEY (id_pregunta),
    CONSTRAINT uq_pregunta_ord  UNIQUE (fk_encuesta, orden),
    CONSTRAINT chk_pregunta_ord CHECK (orden >= 1),
    CONSTRAINT chk_pregunta_rango
        CHECK ((valor_min IS NULL AND valor_max IS NULL)
            OR (valor_min IS NOT NULL AND valor_max IS NOT NULL AND valor_max > valor_min))
);

-- ----------------------------------------------------------------------------
-- opcion_pregunta
-- ----------------------------------------------------------------------------
CREATE TABLE opcion_pregunta (
    id_opcion    bigint       GENERATED ALWAYS AS IDENTITY,
    fk_pregunta  bigint       NOT NULL,
    etiqueta     varchar(150) NOT NULL,
    valor        smallint,
    orden        smallint     NOT NULL,

    CONSTRAINT pk_opcion_pregunta PRIMARY KEY (id_opcion),
    CONSTRAINT uq_opcion_orden    UNIQUE (fk_pregunta, orden)
);

-- ----------------------------------------------------------------------------
-- respuesta_encuesta · 1:1 con el registro
-- ----------------------------------------------------------------------------
CREATE TABLE respuesta_encuesta (
    id_respuesta   bigint       GENERATED ALWAYS AS IDENTITY,
    fk_registro    bigint       NOT NULL,
    fk_encuesta    bigint       NOT NULL,
    respondida_en  timestamptz  NOT NULL DEFAULT now(),
    completa       boolean      NOT NULL DEFAULT false,

    CONSTRAINT pk_respuesta_encuesta PRIMARY KEY (id_respuesta),
    -- RN-23 · una encuesta por registro, como maximo
    CONSTRAINT uq_respuesta_registro UNIQUE (fk_registro)
);

COMMENT ON COLUMN respuesta_encuesta.completa IS
    'Solo lo marca sp_cerrar_encuesta, tras comprobar que todas las preguntas '
    'obligatorias tienen respuesta (RN-26). Es una regla NO DECLARATIVA: '
    'ninguna clave foranea puede exigir "al menos uno".';

-- ----------------------------------------------------------------------------
-- respuesta_item · ENTIDAD DEBIL, con la regla condicional
-- ----------------------------------------------------------------------------
CREATE TABLE respuesta_item (
    id_item         bigint    GENERATED ALWAYS AS IDENTITY,
    fk_respuesta    bigint    NOT NULL,
    fk_pregunta     bigint    NOT NULL,
    valor_numerico  smallint,
    valor_texto     text,
    fk_opcion       bigint,

    CONSTRAINT pk_respuesta_item PRIMARY KEY (id_item),
    CONSTRAINT uq_respuesta_item UNIQUE (fk_respuesta, fk_pregunta),

    -- RN-25 · EXACTAMENTE UNA columna de valor. Los tres vacios, o dos llenos,
    --         es dato corrupto, no un caso opcional.
    CONSTRAINT chk_respuesta_item_un_valor
        CHECK ( (valor_numerico IS NOT NULL)::int
              + (valor_texto    IS NOT NULL)::int
              + (fk_opcion      IS NOT NULL)::int = 1 )
);

COMMENT ON CONSTRAINT chk_respuesta_item_un_valor ON respuesta_item IS
    'RN-25. Impide la corrupcion silenciosa: sin esta restriccion, un item con '
    'las tres columnas vacias se colaria y los promedios del informe de '
    'evaluacion saldrian mal SIN AVISAR. La concordancia entre la columna '
    'usada y el tipo de la pregunta la verifica el disparador del script 10.';

COMMENT ON TABLE respuesta_item IS
    'Respuesta a una pregunta concreta. La alternativa ortodoxa es una '
    'especializacion supertipo/subtipo con una tabla por tipo de respuesta: '
    'es correcta y se acepta, pero cuesta tres tablas y una union en cada '
    'consulta de evaluacion.';

\echo '05 · Bloque E creado - 6 tablas'
