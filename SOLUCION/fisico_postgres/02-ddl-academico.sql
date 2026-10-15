-- ============================================================================
--  02 · DDL - Bloque B · Estructura academica
--  Tablas: facultad · programa_academico · periodo_academico
--          programa_asistente
-- ============================================================================

SET search_path TO catedras, public;

-- ----------------------------------------------------------------------------
-- facultad · relacion reflexiva -> arbol
-- ----------------------------------------------------------------------------
CREATE TABLE facultad (
    id_facultad         varchar(10)   NOT NULL,
    nombre              varchar(120)  NOT NULL,
    fk_facultad_padre   varchar(10),
    activo              boolean       NOT NULL DEFAULT true,

    CONSTRAINT pk_facultad        PRIMARY KEY (id_facultad),
    CONSTRAINT uq_facultad_nombre UNIQUE (nombre),
    -- Una facultad no puede ser su propia madre
    CONSTRAINT chk_facultad_padre CHECK (fk_facultad_padre <> id_facultad)
);

COMMENT ON TABLE facultad IS
    'Unidad academica que agrupa programas. La referencia reflexiva produce un '
    'ARBOL - cada nodo tiene un solo padre -, no un grafo. Por eso se resuelve '
    'con una columna en la misma tabla y se consulta con WITH RECURSIVE.';

-- ----------------------------------------------------------------------------
-- programa_academico · clave NATURAL
-- ----------------------------------------------------------------------------
CREATE TABLE programa_academico (
    codigo       varchar(5)    NOT NULL,
    nombre       varchar(150)  NOT NULL,
    fk_facultad  varchar(10),
    nivel        varchar(25)   NOT NULL DEFAULT 'PREGRADO',
    activo       boolean       NOT NULL DEFAULT true,

    CONSTRAINT pk_programa_academico PRIMARY KEY (codigo),
    -- El codigo NO es siempre M + 4 digitos: el maestro real trae MCDER (5)
    -- y MCCP (4). Es varchar y no char PORQUE char rellena con espacios, y
    -- 'MCCP ' saldria con un espacio final en el archivo plano - justo lo
    -- que el manual de migracion prohibe: "verificar que el archivo este
    -- limpio y que no se haya agregado ningun texto adicional".
    CONSTRAINT chk_programa_codigo   CHECK (codigo ~ '^[A-Z][0-9A-Z]{3,4}$'),
    CONSTRAINT chk_programa_nivel
        CHECK (nivel IN ('PREGRADO', 'ESPECIALIZACION', 'MAESTRIA',
                         'DOCTORADO', 'EDUCACION_CONTINUA', 'OTRO'))
);

COMMENT ON TABLE programa_academico IS
    'Programa academico. 105 codigos distintos en el maestro real: 103 con la '
    'forma M + 4 digitos, mas MCDER de 5 caracteres y MCCP de 4.';

COMMENT ON COLUMN programa_academico.codigo IS
    'CLAVE NATURAL a proposito: es el codigo que viaja al archivo plano del '
    'ASIS. Un identificador sustituto obligaria a un JOIN en la consulta mas '
    'critica del sistema, que es justamente la exportacion.';

-- ----------------------------------------------------------------------------
-- periodo_academico
-- ----------------------------------------------------------------------------
CREATE TABLE periodo_academico (
    id_periodo  char(6)  NOT NULL,
    fecha_ini   date     NOT NULL,
    fecha_fin   date     NOT NULL,
    activo      boolean  NOT NULL DEFAULT true,

    CONSTRAINT pk_periodo_academico PRIMARY KEY (id_periodo),
    CONSTRAINT chk_periodo_formato  CHECK (id_periodo ~ '^[0-9]{4}-[1-3]$'),
    CONSTRAINT chk_periodo_fechas   CHECK (fecha_fin > fecha_ini)
);

COMMENT ON TABLE periodo_academico IS
    'Periodo academico: 2026-1, 2026-2. Lo pidio el profesor Hugo Nelson por su '
    'nombre - "cuantas personas externas han ingresado en 2026-2" (56:16).';

-- ----------------------------------------------------------------------------
-- programa_asistente · N:M con atributos
-- ----------------------------------------------------------------------------
CREATE TABLE programa_asistente (
    fk_asistente  bigint    NOT NULL,
    fk_programa   varchar(5) NOT NULL,
    fk_periodo    char(6)   NOT NULL,
    estado        varchar(15) NOT NULL DEFAULT 'ACTIVO',

    CONSTRAINT pk_programa_asistente
        PRIMARY KEY (fk_asistente, fk_programa, fk_periodo),
    CONSTRAINT chk_programa_asistente_estado
        CHECK (estado IN ('ACTIVO', 'RETIRADO', 'GRADUADO', 'APLAZADO'))
);

COMMENT ON TABLE programa_asistente IS
    'Matricula de un asistente en un programa, por periodo. Es N:M por dato '
    'comprobado: en el maestro real el mismo ID aparece con varios codigos de '
    'programa. La clave de tres columnas absorbe los pares duplicados que trae '
    'el archivo del ASIS - hay pares repetidos hasta tres veces.';

\echo '02 · Bloque B creado - 4 tablas'
