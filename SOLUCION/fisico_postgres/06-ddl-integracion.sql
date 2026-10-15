-- ============================================================================
--  06 · DDL - Bloque F · Integracion con el ASIS
--  Tablas: lote_carga_asistente · novedad_carga · alias_programa
--          estado_proceso · lote_migracion · detalle_migracion
--
--  Entrada: el archivo de personas que se descarga del ASIS.
--  Salida:  el archivo plano de TRES columnas que exige la carga.
-- ============================================================================

SET search_path TO catedras, public;

-- ----------------------------------------------------------------------------
-- lote_carga_asistente
-- ----------------------------------------------------------------------------
CREATE TABLE lote_carga_asistente (
    id_lote_carga    bigint       GENERATED ALWAYS AS IDENTITY,
    nombre_archivo   varchar(200) NOT NULL,
    cargado_en       timestamptz  NOT NULL DEFAULT now(),
    fk_usuario       bigint,
    filas_leidas     integer      NOT NULL DEFAULT 0,
    filas_aceptadas  integer      NOT NULL DEFAULT 0,
    filas_rechazadas integer      NOT NULL DEFAULT 0,
    observaciones    text,

    CONSTRAINT pk_lote_carga PRIMARY KEY (id_lote_carga),
    CONSTRAINT chk_lote_carga_filas
        CHECK (filas_leidas >= 0 AND filas_aceptadas >= 0 AND filas_rechazadas >= 0
               AND filas_aceptadas + filas_rechazadas <= filas_leidas)
);

COMMENT ON TABLE lote_carga_asistente IS
    'Cada ejecucion de la carga del archivo de personas del ASIS. "Ese archivo '
    'lo cargamos en la base de datos como una tabla" (52:57). Una carga de '
    '16.093 filas necesita EVIDENCIA, no un mensaje en pantalla: sin estos '
    'contadores, "cargo menos filas de las que tenia" es indepurable.';

-- ----------------------------------------------------------------------------
-- novedad_carga
-- ----------------------------------------------------------------------------
CREATE TABLE novedad_carga (
    id_novedad       bigint       GENERATED ALWAYS AS IDENTITY,
    fk_lote_carga    bigint       NOT NULL,
    numero_fila      integer      NOT NULL,
    contenido_crudo  text         NOT NULL,
    motivo           varchar(200) NOT NULL,

    CONSTRAINT pk_novedad_carga  PRIMARY KEY (id_novedad),
    CONSTRAINT chk_novedad_fila  CHECK (numero_fila > 0)
);

COMMENT ON COLUMN novedad_carga.contenido_crudo IS
    'La fila del archivo TAL COMO VENIA, sin interpretar. Es lo unico que '
    'permite depurar un rechazo por formato: si se guardara ya convertida, se '
    'perderia justamente el dato que causo el problema.';

-- ----------------------------------------------------------------------------
-- alias_programa · tabla VIVA, no script de una vez
-- ----------------------------------------------------------------------------
CREATE TABLE alias_programa (
    id_alias           bigint       GENERATED ALWAYS AS IDENTITY,
    texto_normalizado  varchar(200) NOT NULL,
    fk_programa        varchar(5)   NOT NULL,
    origen             varchar(30)  NOT NULL DEFAULT 'FORMULARIO',
    creado_en          timestamptz  NOT NULL DEFAULT now(),

    CONSTRAINT pk_alias_programa PRIMARY KEY (id_alias),
    CONSTRAINT uq_alias_texto    UNIQUE (texto_normalizado)
);

COMMENT ON TABLE alias_programa IS
    'Texto libre con que se ha escrito un programa, y el codigo al que '
    'corresponde. Nace de la calidad real del formulario actual, que trae '
    '"Psicologica", "Entrenamiento Deportivo.", "Ingenieria de datos y '
    'software" y una celda con la facultad y el programa en dos lineas. '
    'Es una tabla VIVA porque los formularios en texto libre van a seguir '
    'llegando durante toda la transicion.';

-- ----------------------------------------------------------------------------
-- estado_proceso · los CINCO estados literales del manual, pagina 6
-- ----------------------------------------------------------------------------
CREATE TABLE estado_proceso (
    id_estado    varchar(12)  NOT NULL,
    nombre       varchar(40)  NOT NULL,
    es_final     boolean      NOT NULL DEFAULT false,
    es_exitoso   boolean      NOT NULL DEFAULT false,

    CONSTRAINT pk_estado_proceso PRIMARY KEY (id_estado),
    CONSTRAINT chk_estado_coherente
        CHECK (es_exitoso = false OR es_final = true)
);

COMMENT ON TABLE estado_proceso IS
    'Estados del Monitor Procesos del ASIS. Son los cinco literales del manual '
    'de migracion: En cola, En curso, Error, Correcto, Incorrecto.';

-- ----------------------------------------------------------------------------
-- lote_migracion
-- ----------------------------------------------------------------------------
CREATE TABLE lote_migracion (
    id_lote_migracion      bigint       GENERATED ALWAYS AS IDENTITY,
    fk_sesion              bigint       NOT NULL,
    nombre_proceso         varchar(60)  NOT NULL DEFAULT 'ME_MIGRACION_CATEDRA',
    nombre_archivo         varchar(200) NOT NULL,
    generado_en            timestamptz  NOT NULL DEFAULT now(),
    fk_usuario             bigint,
    instancia_proceso_asis varchar(30),
    fk_estado_proceso      varchar(12)  NOT NULL DEFAULT 'GENERADO',
    total_filas            integer      NOT NULL DEFAULT 0,
    observaciones          text,

    CONSTRAINT pk_lote_migracion PRIMARY KEY (id_lote_migracion),
    CONSTRAINT chk_lote_mig_filas CHECK (total_filas >= 0)
);

COMMENT ON COLUMN lote_migracion.instancia_proceso_asis IS
    'El numero de instancia que devuelve el ASIS al ejecutar el proceso en '
    'PSUNX01. Es lo que permite cerrar el ciclo contra el Monitor Procesos.';

-- ----------------------------------------------------------------------------
-- detalle_migracion · guarda LO QUE SE ENVIO
-- ----------------------------------------------------------------------------
CREATE TABLE detalle_migracion (
    id_detalle         bigint       GENERATED ALWAYS AS IDENTITY,
    fk_lote_migracion  bigint       NOT NULL,
    fk_registro        bigint       NOT NULL,
    id_asis_enviado    varchar(15)  NOT NULL,
    programa_enviado   varchar(5),
    reunion_enviada    smallint     NOT NULL,
    resultado          varchar(12)  NOT NULL DEFAULT 'PENDIENTE',
    mensaje            varchar(300),

    CONSTRAINT pk_detalle_migracion PRIMARY KEY (id_detalle),
    CONSTRAINT uq_detalle_lote_reg  UNIQUE (fk_lote_migracion, fk_registro),
    CONSTRAINT chk_detalle_resultado
        CHECK (resultado IN ('PENDIENTE', 'ACEPTADO', 'RECHAZADO'))
);

COMMENT ON TABLE detalle_migracion IS
    'Cada fila enviada en un lote, TAL COMO SE ENVIO, y el resultado que dio.';

COMMENT ON COLUMN detalle_migracion.id_asis_enviado IS
    'COPIA LITERAL del ID que salio en el archivo. Se repite a proposito una '
    'columna que ya esta en asistente: NO SON LO MISMO. Si el dato de origen '
    'cambia despues del envio, la tabla dira una cosa y el ASIS tendra otra, '
    'y sin esta copia un rechazo es indepurable seis meses despues.';

COMMENT ON COLUMN detalle_migracion.programa_enviado IS
    'COPIA LITERAL del codigo de programa. NULO solo es legitimo si la '
    'vinculacion no exigia programa - y en ese caso el registro no deberia '
    'haber entrado al lote (RN-28).';

\echo '06 · Bloque F creado - 6 tablas'
