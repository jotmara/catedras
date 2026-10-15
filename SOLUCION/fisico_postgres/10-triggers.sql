-- ============================================================================
--  10 · Disparadores
--
--  Aqui viven las reglas que PostgreSQL no puede declarar. Cada una lleva su
--  numero de RN, para que en la revision se vea que no se olvido ninguna:
--  lo que no es declarativo hay que escribirlo Y hay que medirlo.
-- ============================================================================

SET search_path TO catedras, public;

-- ============================================================================
-- RN-10 · El numero de reunion - PROPUESTA del sistema, autoridad del ASIS
--
-- El disparador propone el siguiente consecutivo de la catedra. Eso resuelve
-- el paso 2 del manual - "verificar el ID del evento y la ultima reunion que
-- se llevo a cabo" - para las catedras que nazcan en este sistema.
--
-- PERO NO SE PUEDE DERIVAR PARA LAS EXISTENTES, y el dato lo demuestra:
--
--   * De los 5.481 eventos con UNA sola reunion, solo 588 tienen el numero 1.
--     Los otros 4.893 traen valores arbitrarios, hasta 4348.
--   * Los eventos con muchas reuniones si empiezan en 1, pero CON HUECOS:
--     000035428 tiene 59 reuniones numeradas de 1 a 60.
--
-- Conclusion: el ASIS lleva un contador propio que este sistema no conoce.
-- Por eso sesion.numero_reunion_asis NO es una comodidad de conciliacion:
-- es el valor bueno cuando existe. Esto RESUELVE con dato la decision que el
-- plan dejo abierta en §8.3.
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_trg_sesion_consecutivo()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.numero_reunion IS NULL OR NEW.numero_reunion = 0 THEN
        -- El bloqueo de la catedra serializa dos altas simultaneas
        PERFORM 1 FROM catedra WHERE id_catedra = NEW.fk_catedra FOR UPDATE;

        SELECT coalesce(max(s.numero_reunion), 0) + 1
          INTO NEW.numero_reunion
          FROM sesion s
         WHERE s.fk_catedra = NEW.fk_catedra;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_sesion_consecutivo
    BEFORE INSERT ON sesion
    FOR EACH ROW EXECUTE FUNCTION fn_trg_sesion_consecutivo();

COMMENT ON FUNCTION fn_trg_sesion_consecutivo() IS
    'RN-10. PROPONE el siguiente consecutivo de la catedra cuando no se indica. '
    'El FOR UPDATE serializa dos altas simultaneas: sin el, uq_sesion_reunion '
    'rechazaria una de las dos con un error feo en vez de ordenarlas. '
    'NO sustituye al numero del ASIS: para las catedras que ya existen alli, la '
    'autoridad es numero_reunion_asis. Ver el comentario de arriba y §8.3.';

-- ============================================================================
-- RN-13 · El canal del enlace concuerda con la modalidad de la sesion
--         "cuando es virtual enviamos el enlace; si es presencial, el QR"
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_trg_enlace_canal()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_canal_esperado varchar(10);
BEGIN
    SELECT m.canal_difusion
      INTO v_canal_esperado
      FROM sesion s
      JOIN modalidad m ON m.id_modalidad = s.fk_modalidad
     WHERE s.id_sesion = NEW.fk_sesion;

    IF v_canal_esperado IS DISTINCT FROM 'AMBOS'
       AND NEW.canal IS DISTINCT FROM v_canal_esperado THEN
        RAISE EXCEPTION
            'RN-13: la sesion % es de modalidad que se difunde por %, no por %',
            NEW.fk_sesion, v_canal_esperado, NEW.canal
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_enlace_canal
    BEFORE INSERT OR UPDATE OF canal, fk_sesion ON enlace_registro
    FOR EACH ROW EXECUTE FUNCTION fn_trg_enlace_canal();

-- ============================================================================
-- RN-19 · es_correo_institucional se DERIVA del dominio de destino
--
-- Responde al asunto que el profesor Carlos Castro dejo abierto en 55:32.
-- Si se digitara, alguien lo marcaria mal justo en el caso que hay que vigilar.
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_trg_clave_derivar()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_dominios text;
BEGIN
    SELECT valor INTO v_dominios
      FROM parametro WHERE clave = 'DOMINIOS_INSTITUCIONALES';

    v_dominios := coalesce(v_dominios, 'usbmed.edu.co,usb.edu.co');

    NEW.es_correo_institucional := EXISTS (
        SELECT 1
          FROM unnest(string_to_array(v_dominios, ',')) AS d(dom)
         WHERE lower(NEW.enviado_a::text) LIKE '%@' || lower(trim(d.dom))
    );
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_clave_derivar
    BEFORE INSERT OR UPDATE OF enviado_a ON clave_acceso
    FOR EACH ROW EXECUTE FUNCTION fn_trg_clave_derivar();

-- ============================================================================
-- RN-15, RN-22 y RN-38 · Todo lo que hay que comprobar al registrar
--   RN-15 · dentro de la ventana del enlace
--   RN-22 · instantanea de programa y vinculacion
--   RN-38 · cupo de la sesion
--   RN-07 · programa obligatorio salvo que la vinculacion no lo exija
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_trg_registro_validar()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_ventana        tstzrange;
    v_revocado       timestamptz;
    v_cupo           integer;
    v_registrados    integer;
    v_exige_programa boolean;
BEGIN
    ------------------------------------------------------------------ RN-15 --
    IF NEW.fk_enlace IS NOT NULL AND NEW.origen NOT IN ('MANUAL', 'IMPORTADO') THEN
        SELECT e.ventana, e.revocado_en
          INTO v_ventana, v_revocado
          FROM enlace_registro e
         WHERE e.id_enlace = NEW.fk_enlace;

        IF v_revocado IS NOT NULL THEN
            RAISE EXCEPTION 'RN-15: el enlace % esta revocado', NEW.fk_enlace
                USING ERRCODE = 'check_violation';
        END IF;

        IF NOT (v_ventana @> NEW.registrado_en) THEN
            RAISE EXCEPTION
                'RN-15: % esta fuera de la ventana % del enlace %',
                NEW.registrado_en, v_ventana, NEW.fk_enlace
                USING ERRCODE = 'check_violation';
        END IF;
    END IF;

    ------------------------------------------------------------------ RN-22 --
    -- Instantanea de la VINCULACION vigente
    IF NEW.fk_vinculacion_snapshot IS NULL THEN
        SELECT v.fk_tipo_vinculacion
          INTO NEW.fk_vinculacion_snapshot
          FROM vinculacion_asistente v
         WHERE v.fk_asistente = NEW.fk_asistente
           AND v.fecha_fin IS NULL
         ORDER BY v.fecha_ini DESC
         LIMIT 1;

        IF NEW.fk_vinculacion_snapshot IS NULL THEN
            RAISE EXCEPTION
                'El asistente % no tiene ninguna vinculacion vigente',
                NEW.fk_asistente USING ERRCODE = 'check_violation';
        END IF;
    END IF;

    SELECT tv.exige_programa INTO v_exige_programa
      FROM tipo_vinculacion tv
     WHERE tv.id_tipo_vinculacion = NEW.fk_vinculacion_snapshot;

    -- Instantanea del PROGRAMA vigente, solo si la vinculacion lo exige
    IF NEW.fk_programa_snapshot IS NULL AND v_exige_programa THEN
        SELECT pa.fk_programa
          INTO NEW.fk_programa_snapshot
          FROM programa_asistente pa
          JOIN periodo_academico p ON p.id_periodo = pa.fk_periodo
         WHERE pa.fk_asistente = NEW.fk_asistente
           AND pa.estado = 'ACTIVO'
         ORDER BY p.fecha_ini DESC
         LIMIT 1;
    END IF;

    ------------------------------------------------------------------ RN-07 --
    IF v_exige_programa AND NEW.fk_programa_snapshot IS NULL THEN
        RAISE EXCEPTION
            'RN-07: la vinculacion % exige programa academico y el asistente % no tiene ninguno activo',
            NEW.fk_vinculacion_snapshot, NEW.fk_asistente
            USING ERRCODE = 'check_violation';
    END IF;

    IF NOT v_exige_programa THEN
        -- Rutas de Paz y similares entran SIN programa, a proposito
        NEW.fk_programa_snapshot := NULL;
    END IF;

    ------------------------------------------------------------------ RN-38 --
    SELECT s.cupo INTO v_cupo FROM sesion s WHERE s.id_sesion = NEW.fk_sesion FOR UPDATE;

    IF v_cupo IS NOT NULL THEN
        SELECT count(*) INTO v_registrados
          FROM registro_asistencia r WHERE r.fk_sesion = NEW.fk_sesion;

        IF v_registrados >= v_cupo THEN
            RAISE EXCEPTION 'RN-38: la sesion % alcanzo su cupo de %',
                NEW.fk_sesion, v_cupo USING ERRCODE = 'check_violation';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_registro_validar
    BEFORE INSERT ON registro_asistencia
    FOR EACH ROW EXECUTE FUNCTION fn_trg_registro_validar();

COMMENT ON FUNCTION fn_trg_registro_validar() IS
    'Cuatro reglas en un disparador porque las cuatro se comprueban en el mismo '
    'instante y sobre la misma fila. El FOR UPDATE sobre la sesion serializa el '
    'control de cupo: sin el, dos registros simultaneos podrian pasarse.';

-- ============================================================================
-- RN-25 · El tipo de pregunta decide QUE columna de valor se usa
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_trg_respuesta_item_tipo()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    t record;
BEGIN
    SELECT tp.id_tipo_pregunta, tp.guarda_numero, tp.guarda_texto, tp.guarda_opcion,
           p.valor_min, p.valor_max
      INTO t
      FROM pregunta p
      JOIN tipo_pregunta tp ON tp.id_tipo_pregunta = p.fk_tipo_pregunta
     WHERE p.id_pregunta = NEW.fk_pregunta;

    IF t.guarda_numero AND NEW.valor_numerico IS NULL THEN
        RAISE EXCEPTION 'RN-25: la pregunta % es de tipo % y espera valor_numerico',
            NEW.fk_pregunta, t.id_tipo_pregunta USING ERRCODE = 'check_violation';
    ELSIF t.guarda_texto AND NEW.valor_texto IS NULL THEN
        RAISE EXCEPTION 'RN-25: la pregunta % es de tipo % y espera valor_texto',
            NEW.fk_pregunta, t.id_tipo_pregunta USING ERRCODE = 'check_violation';
    ELSIF t.guarda_opcion AND NEW.fk_opcion IS NULL THEN
        RAISE EXCEPTION 'RN-25: la pregunta % es de tipo % y espera fk_opcion',
            NEW.fk_pregunta, t.id_tipo_pregunta USING ERRCODE = 'check_violation';
    END IF;

    -- El rango declarado de la pregunta
    IF NEW.valor_numerico IS NOT NULL AND t.valor_min IS NOT NULL
       AND NEW.valor_numerico NOT BETWEEN t.valor_min AND t.valor_max THEN
        RAISE EXCEPTION 'RN-25: % esta fuera del rango [%, %] de la pregunta %',
            NEW.valor_numerico, t.valor_min, t.valor_max, NEW.fk_pregunta
            USING ERRCODE = 'check_violation';
    END IF;

    -- RN-24 · la opcion elegida pertenece a ESA pregunta
    IF NEW.fk_opcion IS NOT NULL
       AND NOT EXISTS (SELECT 1 FROM opcion_pregunta o
                        WHERE o.id_opcion = NEW.fk_opcion
                          AND o.fk_pregunta = NEW.fk_pregunta) THEN
        RAISE EXCEPTION 'RN-24: la opcion % no pertenece a la pregunta %',
            NEW.fk_opcion, NEW.fk_pregunta USING ERRCODE = 'check_violation';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_respuesta_item_tipo
    BEFORE INSERT OR UPDATE ON respuesta_item
    FOR EACH ROW EXECUTE FUNCTION fn_trg_respuesta_item_tipo();

-- ============================================================================
-- RN-35 · Bitacora sobre las tablas sensibles
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_trg_bitacora()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_antes   jsonb;
    v_despues jsonb;
    v_llave   text;
BEGIN
    -- Se convierte a jsonb PRIMERO y la llave se extrae de ahi.
    -- No se usa CASE sobre NEW.<columna> porque PL/pgSQL planifica la
    -- expresion COMPLETA contra el tipo de registro que dispara: una rama
    -- que nombre una columna de otra tabla revienta aunque no se ejecute.
    IF TG_OP IN ('UPDATE', 'DELETE') THEN v_antes   := to_jsonb(OLD); END IF;
    IF TG_OP IN ('INSERT', 'UPDATE') THEN v_despues := to_jsonb(NEW); END IF;

    v_llave := coalesce(v_despues, v_antes) ->> ('id_' || replace(TG_TABLE_NAME, '_asistencia', ''));

    INSERT INTO bitacora (nombre_tabla, operacion, llave, datos_antes, datos_despues)
    VALUES (TG_TABLE_NAME, TG_OP, v_llave, v_antes, v_despues);

    RETURN CASE WHEN TG_OP = 'DELETE' THEN OLD ELSE NEW END;
END;
$$;

CREATE TRIGGER trg_bitacora_registro
    AFTER INSERT OR UPDATE OR DELETE ON registro_asistencia
    FOR EACH ROW EXECUTE FUNCTION fn_trg_bitacora();

CREATE TRIGGER trg_bitacora_asistente
    AFTER UPDATE OR DELETE ON asistente
    FOR EACH ROW EXECUTE FUNCTION fn_trg_bitacora();

\echo '10 · Disparadores creados - 6 funciones, 8 disparadores'
