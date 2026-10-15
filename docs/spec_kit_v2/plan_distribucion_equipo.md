# Plan de Distribución y Commits por Integrante — Versión 2

> **Equipo:** Johan, Kevin, Andrés y Valentina  
> **Estrategia:** Cada integrante tendrá asignada una rama (`feature/...`), su conjunto de archivos y sus commits progresivos en el nuevo repositorio para que el historial refleje trabajo colaborativo real, equilibrado y alineado con los 4 pilares evaluados por el profesor Carlos Castro.

---

## 1. Matriz de Asignación por Integrante

```
┌──────────────┬───────────────────────────────────────────┬────────────────────────────────────────┐
│ Integrante   │ Rol en el Proyecto                        │ Responsabilidad y Archivos Entregables │
├──────────────┼───────────────────────────────────────────┼────────────────────────────────────────┤
│ **Johan**    │ Líder de Arquitectura y Base de Datos     │ Base de Datos: Triggers, SPs, Esquema, │
│              │ (PostgreSQL / Core Relacional)            │ 10 Relaciones M-D y Spec Kit Central   │
├──────────────┼───────────────────────────────────────────┼────────────────────────────────────────┤
│ **Kevin**    │ Ingeniero Backend API                     │ Controladores REST .NET, DTOs, Dapper, │
│              │ (ASP.NET Core / Dapper / Integración)     │ Manejo de Códigos HTTP (409, 422)      │
├──────────────┼───────────────────────────────────────────┼────────────────────────────────────────┤
│ **Valentina**│ Ingeniera Frontend y Experiencia Usuario │ Interfaz Web Flask, Pantalla Única     │
│              │ (Flask / UI Maestro-Detalle / CSS USBMed) │ Maestro-Detalle, Dropdowns de FKs      │
├──────────────┼───────────────────────────────────────────┼────────────────────────────────────────┤
│ **Andrés**   │ Ingeniero de Calidad, QA y Documentación  │ Batería de Pruebas Smoke Test, Guía de │
│              │ (Testing / Elicitación / Interpretabilidad)│ Interpretabilidad y Prompts de la IA   │
└──────────────┴───────────────────────────────────────────┴────────────────────────────────────────┘
```

---

## 2. Detalle de Archivos, Tareas y Commits por Persona

### 👤 1. Johan (Arquitectura, Base de Datos y Spec Kit Núcleo)
- **Rama:** `feature/db-triggers-stored-procedures`
- **Archivos que le corresponden:**
  - `SOLUCION/fisico_postgres/03-ddl-catedras.sql` (Columna generada `nombre_asis` de 30 caracteres).
  - `SOLUCION/fisico_postgres/10-triggers.sql` (Disparador `trg_sesion_consecutivo` y `trg_enlace_canal`).
  - `SOLUCION/fisico_postgres/11-funciones-procedimientos.sql` (`sp_solicitar_clave`, `sp_validar_clave_y_registrar`, `fn_exportar_asis`).
  - `docs/spec_kit_v2/1_constitution.md`
  - `docs/spec_kit_v2/2_spec.md` (Las 10 relaciones Maestro-Detalle y cadenas de 3 niveles).
  - `docs/spec_kit_v2/5_data_model.md`
- **Mensajes de commit sugeridos:**
  1. `feat(db): definir esquema relacional y columna generada nombre_asis en catedra`
  2. `feat(db): implementar disparador trg_sesion_consecutivo con bloqueo pesimista`
  3. `feat(db): agregar procedimientos almacenados sp_solicitar_clave y validacion de registro`
  4. `docs(spec-kit): especificar 10 relaciones maestro-detalle y modelo de datos v2`

---

### 👤 2. Kevin (Backend API y Capa de Persistencia .NET)
- **Rama:** `feature/backend-api-master-detail`
- **Archivos que le corresponden:**
  - `ApiCatedrasUsbmed/Controllers/CatedraController.cs`
  - `ApiCatedrasUsbmed/Controllers/SesionController.cs`
  - `ApiCatedrasUsbmed/Modelos/Catedra.cs`
  - `ApiCatedrasUsbmed/Modelos/Sesion.cs`
  - `ApiCatedrasUsbmed/Repositorios/` (Mapeo Dapper con exclusión de `nombre_asis`).
  - `docs/spec_kit_v2/3_plan.md` (Patrón técnico de Dapper, capas y endpoints).
  - `docs/spec_kit_v2/6_contracts.md` (Contratos HTTP REST y traducción de errores 23503 a 422).
- **Mensajes de commit sugeridos:**
  1. `feat(api): crear modelos y DTOs para catedra y sesion con soporte de campos anulables`
  2. `feat(api): implementar repositorios Dapper para operaciones relacionales`
  3. `feat(api): agregar controladores REST CatedraController y SesionController`
  4. `feat(api): configurar middleware para mapeo de excepciones SQLSTATE 23503 y 23505`
  5. `docs(contracts): documentar contratos OpenAPI y codigos de error en spec kit`

---

### 👤 3. Valentina (Frontend Web Institucional y Pantalla Maestro-Detalle)
- **Rama:** `feature/frontend-maestro-detalle`
- **Archivos que le corresponden:**
  - `app.py` (Rutas `/catedras`, `/sesiones` con vista única Maestro-Detalle).
  - `static/` (Estilos corporativos oficiales USBMed, paleta institucional, Montserrat).
  - Plantillas de modales de creación con etiquetas `<select>` para las FKs.
  - `docs/spec_kit_v2/8_tasks.md` (Checklist de avance y validación de componentes de UI).
- **Mensajes de commit sugeridos:**
  1. `feat(ui): estructurar vista maestro-detalle para catedras y sesiones en pantalla unica`
  2. `feat(ui): implementar selectores dinamicos para claves foraneas en modales de creacion`
  3. `style(ui): aplicar guia de estilo y manual de marca corporativo USBMed`
  4. `fix(ui): manejar respuestas de error flash ante conflictos 409 y violaciones de FK`
  5. `docs(tasks): actualizar matriz de tareas y checklist de interfaz de usuario`

---

### 👤 4. Andrés (Calidad, Prompts de IA, Interpretabilidad y Testing)
- **Rama:** `feature/qa-prompts-interpretabilidad`
- **Archivos que le corresponden:**
  - `docs/spec_kit_v2/prompts_v2.md` (Registro histórico de prompts de desarrollo e IA).
  - `docs/spec_kit_v2/guia_interpretabilidad.md` (Respuestas a las 4 preguntas críticas de oralidad).
  - `docs/spec_kit_v2/4_research.md` (Test de las 3 preguntas y justificación de decisiones).
  - `docs/spec_kit_v2/7_quickstart.md` (Guía de Smoke Test y demostración del disparador en vivo).
  - `SOLUCION/PROMPT-PARA-IA.md`
- **Mensajes de commit sugeridos:**
  1. `docs(prompts): documentar prompts iniciales de elicitacion y reglas inviolables de ASIS`
  2. `docs(research): formalizar test de tres preguntas para relaciones dependientes y decisiones D1-D5`
  3. `docs(qa): elaborar guia de interpretabilidad del codigo para sustentacion oral`
  4. `test(smoke): redactar script y protocolo de validacion del disparador en vivo`

---

## 3. Flujo de Trabajo en Git para el Nuevo Repositorio

Para que el nuevo repositorio quede limpio y profesional:

```bash
# 1. Crear el nuevo repositorio en GitHub (ej: proyecto-catedras-v2)
git remote add origin-nuevo https://github.com/TU_USUARIO/NUEVO_REPOSITORIO.git

# 2. Paso 1: Johan sube la base inicial
git checkout -b feature/db-triggers-stored-procedures
git commit -m "feat(db): inicializar esquema, procedimientos y disparadores"
git push origin-nuevo feature/db-triggers-stored-procedures

# 3. Paso 2: Kevin sube la API
git checkout -b feature/backend-api-master-detail
git commit -m "feat(api): controladores REST y persistencia Dapper"
git push origin-nuevo feature/backend-api-master-detail

# 4. Paso 3: Valentina sube el Frontend
git checkout -b feature/frontend-maestro-detalle
git commit -m "feat(ui): interfaz maestro-detalle y selectores FK"
git push origin-nuevo feature/frontend-maestro-detalle

# 5. Paso 4: Andrés sube las pruebas y la documentación de IA
git checkout -b feature/qa-prompts-interpretabilidad
git commit -m "docs(qa): prompts de IA, guia de interpretabilidad y smoke test"
git push origin-nuevo feature/qa-prompts-interpretabilidad

# 6. Integración en main (Pull Requests aprobados)
git checkout main
git merge feature/db-triggers-stored-procedures
git merge feature/backend-api-master-detail
git merge feature/frontend-maestro-detalle
git merge feature/qa-prompts-interpretabilidad
git push origin-nuevo main
```
