-- ============================================================================
--  12 · Datos de catalogo
--
--  Todos los valores salen de una fuente verificable: el dato real del ASIS,
--  el manual de migracion, o una cita de la reunion.
-- ============================================================================

SET search_path TO catedras, public;

-- ---------------------------------------------------------------------------
-- tipo_documento · cierra las mas de diez formas de escribir "cedula"
-- ---------------------------------------------------------------------------
INSERT INTO tipo_documento (id_tipo_documento, nombre) VALUES
    ('CC',  'Cedula de ciudadania'),
    ('TI',  'Tarjeta de identidad'),
    ('CE',  'Cedula de extranjeria'),
    ('PA',  'Pasaporte'),
    ('PEP', 'Permiso especial de permanencia'),
    ('NIT', 'Numero de identificacion tributaria');

-- ---------------------------------------------------------------------------
-- tipo_vinculacion · las dos columnas booleanas son las que deciden
-- ---------------------------------------------------------------------------
INSERT INTO tipo_vinculacion (id_tipo_vinculacion, nombre, es_interno, exige_programa) VALUES
    ('ESTUDIANTE',   'Estudiante USB',              true,  true),
    ('DOCENTE',      'Docente USB',                 true,  true),
    ('ADMINISTRATIVO','Administrativo USB',         true,  false),
    ('EGRESADO',     'Egresado USB',                true,  true),
    ('RUTAS_PAZ',    'Rutas de paz y formacion',    true,  false),
    ('COLEGIO',      'Colegio invitado',            false, false),
    ('EXTERNO',      'Publico externo',             false, false);

COMMENT ON TABLE tipo_vinculacion IS
    'RUTAS_PAZ tiene exige_programa = false por la excepcion que planteo el '
    'profesor Hugo Nelson en 41:16: "ellos entrarian sin programa, pero solo '
    'ellos". ADMINISTRATIVO tambien, porque no esta matriculado en nada.';

-- ---------------------------------------------------------------------------
-- tipo_evento · los OCHO codigos observados en las 5.711 filas reales
-- ---------------------------------------------------------------------------
INSERT INTO tipo_evento (id_tipo_evento, nombre) VALUES
    ('CAAB', 'Catedra abierta'),
    ('DLLH', 'Desarrollo humano'),
    ('DEPR', 'Deporte y recreacion'),
    ('SLDI', 'Salud integral'),
    ('ARCU', 'Arte y cultura'),
    ('MTG',  'Mesa de trabajo o grupo'),
    ('DIIB', 'Difusion institucional'),
    ('EIIC', 'Encuentro de investigacion');

-- ---------------------------------------------------------------------------
-- sede · "una catedra en San Benito, otra virtual y otra en Bello" (1:03:33)
-- ---------------------------------------------------------------------------
INSERT INTO sede (id_sede, nombre, direccion, es_virtual) VALUES
    ('SAN_BENITO', 'Campus San Benito', 'Carrera 56C 51-110, Medellin', false),
    ('BELLO',      'Campus Bello',      'Calle 45 61-40, Bello',        false),
    ('VIRTUAL',    'Virtual',           NULL,                            true);

-- ---------------------------------------------------------------------------
-- modalidad · canal_difusion decide QR o enlace (1:06:53)
-- ---------------------------------------------------------------------------
INSERT INTO modalidad (id_modalidad, nombre, canal_difusion) VALUES
    ('PRESENCIAL',    'Presencial',    'QR'),
    ('VIRTUAL',       'Virtual',       'ENLACE'),
    ('TELEPRESENCIAL','Telepresencial','ENLACE'),
    ('HIBRIDA',       'Hibrida',       'AMBOS');

-- ---------------------------------------------------------------------------
-- estado_proceso · los CINCO estados literales del manual, pagina 6
-- ---------------------------------------------------------------------------
INSERT INTO estado_proceso (id_estado, nombre, es_final, es_exitoso) VALUES
    ('GENERADO',   'Generado, sin enviar',  false, false),
    ('EN_COLA',    'En cola',               false, false),
    ('EN_CURSO',   'En curso',              false, false),
    ('ERROR',      'Error',                 true,  false),
    ('CORRECTO',   'Correcto',              true,  true),
    ('INCORRECTO', 'Incorrecto',            true,  false);

COMMENT ON TABLE estado_proceso IS
    'Los cinco estados del Monitor Procesos del ASIS, mas GENERADO para el '
    'momento en que el archivo existe pero todavia no se ha subido.';

-- ---------------------------------------------------------------------------
-- tipo_pregunta
-- ---------------------------------------------------------------------------
INSERT INTO tipo_pregunta (id_tipo_pregunta, nombre, guarda_numero, guarda_texto, guarda_opcion) VALUES
    ('ESCALA_5',    'Escala de 1 a 5',   true,  false, false),
    ('SI_NO',       'Si o no',           true,  false, false),
    ('TEXTO_LIBRE', 'Texto libre',       false, true,  false),
    ('OPCION_UNICA','Opcion unica',      false, false, true);

-- ---------------------------------------------------------------------------
-- rol
-- ---------------------------------------------------------------------------
INSERT INTO rol (id_rol, nombre, descripcion) VALUES
    ('ADMIN',       'Administrador',            'Gestiona catedras, enlaces, cargas y migraciones'),
    ('COORDINADOR', 'Coordinador de dependencia','Ve y gestiona lo de su dependencia'),
    ('CONSULTA',    'Consulta',                 'Solo lectura de informes');

-- ---------------------------------------------------------------------------
-- parametro · "el administrador configura o parametriza los valores que
--             considere" (.docx)
-- ---------------------------------------------------------------------------
INSERT INTO parametro (clave, valor, tipo_dato, descripcion) VALUES
    ('VENTANA_MINUTOS_ANTES',    '30',  'ENTERO',
     'Minutos antes del inicio en que se abre el registro'),
    ('VENTANA_MINUTOS_DESPUES',  '30',  'ENTERO',
     'Minutos despues del fin en que se cierra el registro'),
    ('CLAVE_VIGENCIA_MINUTOS',   '10',  'ENTERO',
     'Minutos que vive la clave enviada al correo'),
    ('CLAVE_LONGITUD',           '6',   'ENTERO',
     'Digitos de la clave de un solo uso'),
    ('CLAVE_MAX_INTENTOS',       '3',   'ENTERO',
     'Intentos antes de anular la clave'),
    ('DOMINIOS_INSTITUCIONALES', 'usbmed.edu.co,usb.edu.co', 'TEXTO',
     'Dominios que cuentan como correo institucional. Alimenta RN-19 e I18'),
    ('URL_BASE',                 'https://catedras.usbmed.edu.co/r/', 'TEXTO',
     'Prefijo de la URL publica de registro'),
    ('VERSION_POLITICA_DATOS',   '2026.1', 'TEXTO',
     'Version vigente de la politica de tratamiento de datos, Ley 1581 de 2012'),
    ('PERMITE_EXTERNOS',         'true', 'BOOLEANO',
     'DECISION ABIERTA §3.1: si es false, solo entra quien tenga ID en el ASIS');

-- ---------------------------------------------------------------------------
-- periodo_academico
-- ---------------------------------------------------------------------------
INSERT INTO periodo_academico (id_periodo, fecha_ini, fecha_fin) VALUES
    ('2025-1', '2025-01-20', '2025-06-07'),
    ('2025-2', '2025-07-21', '2025-12-06'),
    ('2026-1', '2026-01-19', '2026-06-06'),
    ('2026-2', '2026-07-20', '2026-12-05');

-- ---------------------------------------------------------------------------
-- dependencia · arbol
-- ---------------------------------------------------------------------------
INSERT INTO dependencia (id_dependencia, nombre, fk_dependencia_padre) VALUES
    ('VICE_ACAD',  'Vicerrectoria Academica',        NULL),
    ('BIENESTAR',  'Bienestar Institucional',        NULL),
    ('PASTORAL',   'Pastoral Universitaria',         'BIENESTAR'),
    ('DEPORTES',   'Deportes y Recreacion',          'BIENESTAR'),
    ('CULTURA',    'Arte y Cultura',                 'BIENESTAR'),
    ('SALUD',      'Salud Integral',                 'BIENESTAR'),
    ('DESA_HUM',   'Desarrollo Humano',              'BIENESTAR'),
    ('INVESTIG',   'Direccion de Investigaciones',   'VICE_ACAD');

-- ---------------------------------------------------------------------------
-- facultad · arbol
-- ---------------------------------------------------------------------------
INSERT INTO facultad (id_facultad, nombre, fk_facultad_padre) VALUES
    ('USB',      'Universidad de San Buenaventura',        NULL),
    ('F_ING',    'Facultad de Ingenierias',                'USB'),
    ('F_ARTES',  'Facultad de Artes Integradas',           'USB'),
    ('F_PSICO',  'Facultad de Psicologia',                 'USB'),
    ('F_DERECHO','Facultad de Derecho y Ciencias Politicas','USB'),
    ('F_EDU',    'Facultad de Educacion',                  'USB'),
    ('F_CIENCIAS','Facultad de Ciencias Empresariales',    'USB'),
    ('F_SALUD',  'Facultad de Ciencias de la Salud',       'USB'),
    ('F_OTRA',   'Otras unidades academicas',              'USB');

\echo '12 · Catalogos cargados'
