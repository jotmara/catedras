-- ============================================================================
--  04 · DDL - Bloque D · Acceso y registro · EL NUCLEO DEL MODELO
--  Tablas: enlace_registro · clave_acceso · registro_asistencia
--
--  Aqui estan la ventana como rango, el EXCLUDE de no solapamiento y las dos
--  columnas de instantanea que hacen reproducible el archivo del ASIS.
-- ============================================================================

SET search_path TO catedras, public;

-- ----------------------------------------------------------------------------
-- enlace_registro
--
-- El QR y la URL NO son dos entidades: son dos presentaciones del mismo token.
-- Separarlas duplicaria la ventana horaria y permitiria que se contradijeran.
-- ----------------------------------------------------------------------------
CREATE TABLE enlace_registro (
    id_enlace        bigint       GENERATED ALWAYS AS IDENTITY,
    fk_sesion        bigint       NOT NULL,
    token            uuid         NOT NULL DEFAULT gen_random_uuid(),
    url_publica      varchar(300) NOT NULL,
    ruta_imagen_qr   varchar(300),
    canal            varchar(10)  NOT NULL,
    ventana          tstzrange    NOT NULL,
    usos_maximos     integer,
    revocado_en      timestamptz,
    fk_usuario_crea  bigint,
    creado_en        timestamptz  NOT NULL DEFAULT now(),

    CONSTRAINT pk_enlace_registro PRIMARY KEY (id_enlace),
    -- RN-16 · el token es unico y no adivinable
    CONSTRAINT uq_enlace_token    UNIQUE (token),
    CONSTRAINT chk_enlace_canal   CHECK (canal IN ('QR', 'ENLACE')),
    CONSTRAINT chk_enlace_ventana CHECK (NOT isempty(ventana)
                                     AND lower(ventana) IS NOT NULL
                                     AND upper(ventana) IS NOT NULL),
    CONSTRAINT chk_enlace_usos    CHECK (usos_maximos IS NULL OR usos_maximos > 0),
    -- La ruta de la imagen debe ser RELATIVA
    CONSTRAINT chk_enlace_ruta_qr
        CHECK (ruta_imagen_qr IS NULL
               OR (ruta_imagen_qr !~ '^([A-Za-z]:|/|\\\\)')),

    -- RN-36 · dos enlaces de la MISMA sesion no pueden solaparse en el tiempo.
    --         Declarativo gracias a btree_gist. En otro motor esto seria un
    --         disparador con bloqueo explicito.
    CONSTRAINT ex_enlace_sin_solape
        EXCLUDE USING gist (fk_sesion WITH =, ventana WITH &&)
        WHERE (revocado_en IS NULL)
);

COMMENT ON TABLE enlace_registro IS
    'Punto de entrada al registro de una sesion, materializado como QR o como '
    'URL. El .docx exige que "el QR y URL no pueden ser reutilizables" y que '
    'tengan "hora de inicio y hora de cierre" configurables.';

COMMENT ON COLUMN enlace_registro.ventana IS
    'Apertura y cierre EN UN SOLO ATRIBUTO de rango. Con dos columnas sueltas, '
    'ni el EXCLUDE de RN-36 ni la contencion de RN-15 serian declarativos: '
    'los dos serian codigo que alguien tendria que mantener.';

COMMENT ON COLUMN enlace_registro.canal IS
    'QR o ENLACE. Debe concordar con la modalidad de la sesion (RN-13).';

COMMENT ON CONSTRAINT ex_enlace_sin_solape ON enlace_registro IS
    'RN-36. El WHERE hace que los enlaces revocados no estorben: se puede '
    'revocar uno y emitir otro para la misma franja.';

-- ----------------------------------------------------------------------------
-- clave_acceso
--
-- No es autenticacion: es ANTISUPLANTACION. "Yo me puedo registrar por
-- cualquier persona, por eso tiene que ser con el correo; si no, yo te
-- registro a vos y vos me registras a mi" (1:04:51).
-- ----------------------------------------------------------------------------
CREATE TABLE clave_acceso (
    id_clave                bigint       GENERATED ALWAYS AS IDENTITY,
    fk_asistente            bigint       NOT NULL,
    fk_enlace               bigint       NOT NULL,
    clave_hash              bytea        NOT NULL,
    enviado_a               citext       NOT NULL,
    es_correo_institucional boolean      NOT NULL,
    generado_en             timestamptz  NOT NULL DEFAULT now(),
    expira_en               timestamptz  NOT NULL,
    usado_en                timestamptz,
    intentos                smallint     NOT NULL DEFAULT 0,
    ip_solicitud            inet,

    CONSTRAINT pk_clave_acceso     PRIMARY KEY (id_clave),
    CONSTRAINT chk_clave_expira    CHECK (expira_en > generado_en),
    -- RN-20 · una clave usada lo fue dentro de su vigencia
    CONSTRAINT chk_clave_usada     CHECK (usado_en IS NULL
                                      OR (usado_en >= generado_en AND usado_en <= expira_en)),
    CONSTRAINT chk_clave_intentos  CHECK (intentos >= 0 AND intentos <= 10),
    CONSTRAINT chk_clave_correo    CHECK (enviado_a LIKE '%@%.%')
);

COMMENT ON COLUMN clave_acceso.clave_hash IS
    'RN-34 · La clave CIFRADA. Nunca se guarda en claro. Se calcula con '
    'digest() de pgcrypto en el procedimiento sp_solicitar_clave.';

COMMENT ON COLUMN clave_acceso.es_correo_institucional IS
    'DERIVADO del dominio de enviado_a por el disparador del script 10. '
    'Es la columna que responde al asunto que el profesor Carlos Castro dejo '
    'abierto en 55:32: "a mi no me gusta el correo que no sea institucional; '
    'dejame, yo lo resuelvo". El modelo deja el dato listo y medible (I18) '
    'para que la politica se decida con la evidencia a la vista.';

-- ----------------------------------------------------------------------------
-- registro_asistencia · EL ROMBO CENTRAL
-- ----------------------------------------------------------------------------
CREATE TABLE registro_asistencia (
    id_registro               bigint       GENERATED ALWAYS AS IDENTITY,
    fk_sesion                 bigint       NOT NULL,
    fk_asistente              bigint       NOT NULL,
    fk_enlace                 bigint,
    fk_clave                  bigint,
    registrado_en             timestamptz  NOT NULL DEFAULT now(),
    fk_programa_snapshot      varchar(5),
    fk_vinculacion_snapshot   varchar(15)  NOT NULL,
    origen                    varchar(15)  NOT NULL DEFAULT 'QR',
    ip                        inet,
    user_agent                varchar(300),

    CONSTRAINT pk_registro_asistencia PRIMARY KEY (id_registro),
    -- RN-21 · una persona se registra a lo sumo UNA VEZ por sesion
    CONSTRAINT uq_registro_sesion_asis UNIQUE (fk_sesion, fk_asistente),
    CONSTRAINT chk_registro_origen
        CHECK (origen IN ('QR', 'ENLACE', 'MANUAL', 'IMPORTADO')),
    -- Todo registro no manual nace de una clave usada (RN-17)
    CONSTRAINT chk_registro_clave
        CHECK (origen IN ('MANUAL', 'IMPORTADO') OR fk_clave IS NOT NULL)
);

COMMENT ON TABLE registro_asistencia IS
    'Hecho de que un asistente quedo registrado en una sesion, en un instante '
    'concreto, con el programa y la vinculacion que tenia en ese momento. Es la '
    'tabla central del sistema.';

COMMENT ON COLUMN registro_asistencia.fk_programa_snapshot IS
    'INSTANTANEA, no referencia viva. El programa que el asistente tenia EL DIA '
    'de la catedra. NUNCA se actualiza. Razon: "el programa es importante '
    'porque despues eso le da informacion a Registro de que programas hizo el '
    'estudiante" (50:14) - es una afirmacion sobre el pasado. Si se leyera del '
    'vigente, un estudiante que cambia de carrera reescribiria su propio '
    'historial y el archivo enviado al ASIS dejaria de ser reproducible. '
    'NULO cuando la vinculacion no exige programa (Rutas de Paz, RN-07).';

COMMENT ON COLUMN registro_asistencia.fk_vinculacion_snapshot IS
    'INSTANTANEA de la vinculacion. Un egresado que asistio siendo estudiante '
    'debe seguir contando como estudiante en los informes de aquel periodo.';

\echo '04 · Bloque D creado - 3 tablas, con el EXCLUDE de RN-36'
