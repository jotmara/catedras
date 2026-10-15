-- ============================================================================
--  08 · Claves foraneas
--
--  Van todas juntas y despues del DDL para no depender del orden de creacion
--  de las tablas. Cada una lleva NOMBRE y POLITICA DECLARADA: ninguna se deja
--  con el comportamiento por defecto sin haberlo pensado.
--
--  Criterio de las politicas:
--    RESTRICT  -> el dato es evidencia y no debe desaparecer por arrastre
--    CASCADE   -> el hijo no tiene sentido sin el padre (composicion pura)
--    SET NULL  -> la referencia es informativa y el hijo sobrevive sin ella
-- ============================================================================

SET search_path TO catedras, public;

-- ---------------------------------------------------------------- Bloque A --
ALTER TABLE documento_asistente
    ADD CONSTRAINT fk_documento_asistente
        FOREIGN KEY (fk_asistente) REFERENCES asistente (id_asistente)
        ON DELETE CASCADE ON UPDATE CASCADE,
    ADD CONSTRAINT fk_documento_tipo
        FOREIGN KEY (fk_tipo_documento) REFERENCES tipo_documento (id_tipo_documento)
        ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE vinculacion_asistente
    ADD CONSTRAINT fk_vinculacion_asistente
        FOREIGN KEY (fk_asistente) REFERENCES asistente (id_asistente)
        ON DELETE CASCADE ON UPDATE CASCADE,
    ADD CONSTRAINT fk_vinculacion_tipo
        FOREIGN KEY (fk_tipo_vinculacion) REFERENCES tipo_vinculacion (id_tipo_vinculacion)
        ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE consentimiento_datos
    ADD CONSTRAINT fk_consentimiento_asistente
        FOREIGN KEY (fk_asistente) REFERENCES asistente (id_asistente)
        ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE asistente
    ADD CONSTRAINT fk_asistente_lote
        FOREIGN KEY (fk_lote_carga) REFERENCES lote_carga_asistente (id_lote_carga)
        ON DELETE SET NULL ON UPDATE CASCADE;

-- ---------------------------------------------------------------- Bloque B --
ALTER TABLE facultad
    ADD CONSTRAINT fk_facultad_padre
        FOREIGN KEY (fk_facultad_padre) REFERENCES facultad (id_facultad)
        ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE programa_academico
    ADD CONSTRAINT fk_programa_facultad
        FOREIGN KEY (fk_facultad) REFERENCES facultad (id_facultad)
        ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE programa_asistente
    ADD CONSTRAINT fk_progasi_asistente
        FOREIGN KEY (fk_asistente) REFERENCES asistente (id_asistente)
        ON DELETE CASCADE ON UPDATE CASCADE,
    ADD CONSTRAINT fk_progasi_programa
        FOREIGN KEY (fk_programa) REFERENCES programa_academico (codigo)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    ADD CONSTRAINT fk_progasi_periodo
        FOREIGN KEY (fk_periodo) REFERENCES periodo_academico (id_periodo)
        ON DELETE RESTRICT ON UPDATE CASCADE;

-- ---------------------------------------------------------------- Bloque C --
ALTER TABLE dependencia
    ADD CONSTRAINT fk_dependencia_padre
        FOREIGN KEY (fk_dependencia_padre) REFERENCES dependencia (id_dependencia)
        ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE catedra
    ADD CONSTRAINT fk_catedra_tipo_evento
        FOREIGN KEY (fk_tipo_evento) REFERENCES tipo_evento (id_tipo_evento)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    ADD CONSTRAINT fk_catedra_dependencia
        FOREIGN KEY (fk_dependencia) REFERENCES dependencia (id_dependencia)
        ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE sesion
    -- CASCADE: la sesion es entidad DEBIL, no existe sin su catedra
    ADD CONSTRAINT fk_sesion_catedra
        FOREIGN KEY (fk_catedra) REFERENCES catedra (id_catedra)
        ON DELETE CASCADE ON UPDATE CASCADE,
    ADD CONSTRAINT fk_sesion_modalidad
        FOREIGN KEY (fk_modalidad) REFERENCES modalidad (id_modalidad)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    ADD CONSTRAINT fk_sesion_sede
        FOREIGN KEY (fk_sede) REFERENCES sede (id_sede)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    ADD CONSTRAINT fk_sesion_periodo
        FOREIGN KEY (fk_periodo) REFERENCES periodo_academico (id_periodo)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    ADD CONSTRAINT fk_sesion_encuesta
        FOREIGN KEY (fk_encuesta) REFERENCES encuesta (id_encuesta)
        ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE ponencia
    ADD CONSTRAINT fk_ponencia_sesion
        FOREIGN KEY (fk_sesion) REFERENCES sesion (id_sesion)
        ON DELETE CASCADE ON UPDATE CASCADE,
    ADD CONSTRAINT fk_ponencia_asistente
        FOREIGN KEY (fk_asistente) REFERENCES asistente (id_asistente)
        ON DELETE RESTRICT ON UPDATE CASCADE;

-- ---------------------------------------------------------------- Bloque D --
ALTER TABLE enlace_registro
    ADD CONSTRAINT fk_enlace_sesion
        FOREIGN KEY (fk_sesion) REFERENCES sesion (id_sesion)
        ON DELETE CASCADE ON UPDATE CASCADE,
    ADD CONSTRAINT fk_enlace_usuario
        FOREIGN KEY (fk_usuario_crea) REFERENCES usuario (id_usuario)
        ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE clave_acceso
    ADD CONSTRAINT fk_clave_asistente
        FOREIGN KEY (fk_asistente) REFERENCES asistente (id_asistente)
        ON DELETE CASCADE ON UPDATE CASCADE,
    ADD CONSTRAINT fk_clave_enlace
        FOREIGN KEY (fk_enlace) REFERENCES enlace_registro (id_enlace)
        ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE registro_asistencia
    -- RESTRICT en asistente y sesion: el registro es EVIDENCIA de asistencia.
    -- No debe desaparecer por arrastre; para dar de baja se usa activo.
    ADD CONSTRAINT fk_registro_sesion
        FOREIGN KEY (fk_sesion) REFERENCES sesion (id_sesion)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    ADD CONSTRAINT fk_registro_asistente
        FOREIGN KEY (fk_asistente) REFERENCES asistente (id_asistente)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    ADD CONSTRAINT fk_registro_enlace
        FOREIGN KEY (fk_enlace) REFERENCES enlace_registro (id_enlace)
        ON DELETE SET NULL ON UPDATE CASCADE,
    ADD CONSTRAINT fk_registro_clave
        FOREIGN KEY (fk_clave) REFERENCES clave_acceso (id_clave)
        ON DELETE SET NULL ON UPDATE CASCADE,
    -- La instantanea apunta al catalogo, pero NUNCA se actualiza en cascada
    -- de contenido: solo se protege que el codigo exista.
    ADD CONSTRAINT fk_registro_programa_snap
        FOREIGN KEY (fk_programa_snapshot) REFERENCES programa_academico (codigo)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    ADD CONSTRAINT fk_registro_vinculacion_snap
        FOREIGN KEY (fk_vinculacion_snapshot) REFERENCES tipo_vinculacion (id_tipo_vinculacion)
        ON DELETE RESTRICT ON UPDATE CASCADE;

-- ---------------------------------------------------------------- Bloque E --
ALTER TABLE pregunta
    ADD CONSTRAINT fk_pregunta_encuesta
        FOREIGN KEY (fk_encuesta) REFERENCES encuesta (id_encuesta)
        ON DELETE CASCADE ON UPDATE CASCADE,
    ADD CONSTRAINT fk_pregunta_tipo
        FOREIGN KEY (fk_tipo_pregunta) REFERENCES tipo_pregunta (id_tipo_pregunta)
        ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE opcion_pregunta
    ADD CONSTRAINT fk_opcion_pregunta
        FOREIGN KEY (fk_pregunta) REFERENCES pregunta (id_pregunta)
        ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE respuesta_encuesta
    ADD CONSTRAINT fk_respenc_registro
        FOREIGN KEY (fk_registro) REFERENCES registro_asistencia (id_registro)
        ON DELETE CASCADE ON UPDATE CASCADE,
    ADD CONSTRAINT fk_respenc_encuesta
        FOREIGN KEY (fk_encuesta) REFERENCES encuesta (id_encuesta)
        ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE respuesta_item
    ADD CONSTRAINT fk_respitem_respuesta
        FOREIGN KEY (fk_respuesta) REFERENCES respuesta_encuesta (id_respuesta)
        ON DELETE CASCADE ON UPDATE CASCADE,
    ADD CONSTRAINT fk_respitem_pregunta
        FOREIGN KEY (fk_pregunta) REFERENCES pregunta (id_pregunta)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    ADD CONSTRAINT fk_respitem_opcion
        FOREIGN KEY (fk_opcion) REFERENCES opcion_pregunta (id_opcion)
        ON DELETE RESTRICT ON UPDATE CASCADE;

-- ---------------------------------------------------------------- Bloque F --
ALTER TABLE novedad_carga
    ADD CONSTRAINT fk_novedad_lote
        FOREIGN KEY (fk_lote_carga) REFERENCES lote_carga_asistente (id_lote_carga)
        ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE alias_programa
    ADD CONSTRAINT fk_alias_programa
        FOREIGN KEY (fk_programa) REFERENCES programa_academico (codigo)
        ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE lote_migracion
    ADD CONSTRAINT fk_lotemig_sesion
        FOREIGN KEY (fk_sesion) REFERENCES sesion (id_sesion)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    ADD CONSTRAINT fk_lotemig_estado
        FOREIGN KEY (fk_estado_proceso) REFERENCES estado_proceso (id_estado)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    ADD CONSTRAINT fk_lotemig_usuario
        FOREIGN KEY (fk_usuario) REFERENCES usuario (id_usuario)
        ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE detalle_migracion
    ADD CONSTRAINT fk_detmig_lote
        FOREIGN KEY (fk_lote_migracion) REFERENCES lote_migracion (id_lote_migracion)
        ON DELETE CASCADE ON UPDATE CASCADE,
    -- RESTRICT: el detalle es la evidencia de lo enviado al ASIS
    ADD CONSTRAINT fk_detmig_registro
        FOREIGN KEY (fk_registro) REFERENCES registro_asistencia (id_registro)
        ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE lote_carga_asistente
    ADD CONSTRAINT fk_lotecarga_usuario
        FOREIGN KEY (fk_usuario) REFERENCES usuario (id_usuario)
        ON DELETE SET NULL ON UPDATE CASCADE;

-- ---------------------------------------------------------------- Bloque G --
ALTER TABLE usuario
    ADD CONSTRAINT fk_usuario_asistente
        FOREIGN KEY (fk_asistente) REFERENCES asistente (id_asistente)
        ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE rol_por_usuario
    ADD CONSTRAINT fk_rolusr_usuario
        FOREIGN KEY (fk_usuario) REFERENCES usuario (id_usuario)
        ON DELETE CASCADE ON UPDATE CASCADE,
    ADD CONSTRAINT fk_rolusr_rol
        FOREIGN KEY (fk_rol) REFERENCES rol (id_rol)
        ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE parametro
    ADD CONSTRAINT fk_parametro_usuario
        FOREIGN KEY (fk_usuario_modifica) REFERENCES usuario (id_usuario)
        ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE bitacora
    ADD CONSTRAINT fk_bitacora_usuario
        FOREIGN KEY (fk_usuario) REFERENCES usuario (id_usuario)
        ON DELETE SET NULL ON UPDATE CASCADE;

\echo '08 · Claves foraneas creadas'
