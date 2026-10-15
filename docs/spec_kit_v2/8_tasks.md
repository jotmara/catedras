# Lista de Tareas y Rúbrica de Evaluación — Versión 2

> **Versión 2 / Segunda Entrega** · Matriz de cumplimiento estricto frente a los criterios de evaluación del curso (Prof. Carlos Castro).

---

## 1. Rúbrica Oficial de Evaluación (Versión 2)

| Componente Evaluado | Peso / Puntos | Estado | Criterio Cumplido |
| :--- | :---: | :---: | :--- |
| **1. Spec Kit Versión 2 Completo** | 4.0 / 20 (20%) | **COMPLETO** | 8 documentos normalizados en `docs/spec_kit_v2/` con especificación exhaustiva del dominio USBMed, 10 relaciones Maestro-Detalle y 2 cadenas de 3 niveles. |
| **2. Prompts de Elicitación y Construcción** | 4.0 / 20 (20%) | **COMPLETO** | Archivo `docs/spec_kit_v2/prompts_v2.md` documentando el diálogo de especificación, contexto de PeopleSoft ASIS y reglas inviolables. |
| **3. Interpretabilidad del Código y Arquitectura** | 4.0 / 20 (20%) | **COMPLETO** | Guía de defensa oral con respuestas fundamentadas a las 4 preguntas críticas por cada archivo nuclear del sistema. |
| **4. Frontend Funcional Maestro-Detalle** | 4.0 / 20 (20%) | **COMPLETO** | Interfaz en `http://localhost:5173` con pantalla única Maestro-Detalle (`catedra` ──▶ `sesion`) y selectores desplegables para todas las FKs. |
| **5. Disparador Demostrable y Procedimientos** | 4.0 / 20 (20%) | **COMPLETO** | Disparador `trg_sesion_consecutivo` calculando consecutivo en vivo + Stored Procedures transaccionales `CALL sp_...`. |

---

## 2. Checklist Detallado por Fases

### Fase 1: Especificación y Gobernanza (Spec Kit v2)
- [x] Redactar `1_constitution.md` con las reglas permanentes del proyecto.
- [x] Redactar `2_spec.md` con las 10 relaciones Maestro-Detalle, cadenas de 3 niveles y justificación de excepciones (ej. `ponencia`).
- [x] Redactar `3_plan.md` con arquitectura de capas, patrón `CALL sp_...` y disparadores.
- [x] Redactar `4_research.md` aplicando el test de las tres preguntas y decisiones de diseño D1 a D5.
- [x] Redactar `5_data_model.md` con diccionario de datos y restricciones DDL.
- [x] Redactar `6_contracts.md` con contratos HTTP y mapeo de errores PostgreSQL.
- [x] Redactar `7_quickstart.md` con guía de ejecución de pruebas y demostración de triggers.
- [x] Redactar `8_tasks.md` con control de calidad y rúbrica.
- [x] Redactar `prompts_v2.md` con el registro de prompts de desarrollo.

### Fase 2: Base de Datos y Lógica de Procedimientos
- [x] Disparador `trg_sesion_consecutivo` activo en `catedras.sesion`.
- [x] Procedimientos de flujo `sp_emitir_enlace`, `sp_solicitar_clave`, `sp_validar_clave_y_registrar`.
- [x] Función de exportación de tres columnas `fn_exportar_asis`.
- [x] Columna generada persistente `nombre_asis` en `catedras.catedra`.

### Fase 3: Backend REST y Dapper (.NET 10 / .NET 8)
- [x] Controladores REST para entidades maestro-detalle (`CatedraController`, `SesionController`).
- [x] Repositorios Dapper con consultas parametrizadas.
- [x] Middleware global para captura de errores SQLSTATE (23503, 23505).

### Fase 4: Frontend Web Institucional (Flask)
- [x] Pantalla Maestro-Detalle interactiva en un solo plano visual.
- [x] Formularios con desplegables poblados desde la base de datos (cero digitación manual de FKs).
- [x] Estilo corporativo oficial USBMed (Manual de Marca institucional).
