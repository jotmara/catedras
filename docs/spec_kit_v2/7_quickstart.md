# Guía de Inicio Rápido y Demostración en Vivo — Versión 2

> **Versión 2 / Segunda Entrega** · Protocolo de ejecución y verificación paso a paso para la sustentación oral (Prof. Carlos Castro).
> Frontend Flask: `http://localhost:5173` · Backend .NET: `http://localhost:7045/swagger` · BD: PostgreSQL 16 (puerto 5432).

---

## 1. Verificación de Servicios en Ejecución

Antes de iniciar la demostración oral, verificar que los tres servicios estén activos:

```bash
# 1. Base de datos PostgreSQL
psql -U postgres -h localhost -p 5432 -d catedras -c "SELECT count(*) FROM catedras.catedra;"

# 2. Backend ASP.NET Core (Swagger)
curl -s http://localhost:7045/swagger/index.html | head -n 5

# 3. Frontend Web Institucional (Flask)
curl -s http://localhost:5173/ | head -n 5
```

---

## 2. Demostración 1: El Disparador en Vivo (`trg_sesion_consecutivo`)

Este paso demuestra el requerimiento obligatorio de **"Al menos un disparador (trigger) corriendo en vivo y demostrable desde la UI o API sin que el cliente envíe el dato"**.

### Procedimiento:
1. Abrir una terminal o cliente HTTP (Swagger / cURL).
2. Crear una nueva sesión para una cátedra existente **omitiendo deliberadamente el campo `numeroReunion`** (o enviándolo en `0`):
   ```bash
   curl -s -X POST http://localhost:7045/api/sesion \
     -H "Content-Type: application/json" \
     -d '{
       "fkCatedra": 1,
       "titulo": "Sesión Demostrativa de Disparador",
       "inicio": "2026-11-10T14:00:00Z",
       "fin": "2026-11-10T16:00:00Z",
       "fkModalidad": "PRESENCIAL",
       "fkSede": "SAN_BENITO",
       "fkPeriodo": "2026-2",
       "lugar": "Aula Magna",
       "cupo": 80
     }'
   ```
3. **Resultado Demostrable:**
   - La respuesta del servidor y la base de datos devuelven `numeroReunion` calculado automáticamente por la función `fn_trg_sesion_consecutivo()`:
     ```sql
     SELECT id_sesion, fk_catedra, numero_reunion, titulo
     FROM catedras.sesion
     WHERE titulo = 'Sesión Demostrativa de Disparador';
     ```
   - Si la cátedra ya tenía 2 sesiones, el valor asignado es exactamente **3**.

---

## 3. Demostración 2: Frontend Maestro-Detalle en Pantalla Única

Este paso demuestra el requerimiento obligatorio de **"Frontend funcional con pantalla única Maestro-Detalle y dropdowns para claves foráneas"**.

### Procedimiento:
1. Abrir en el navegador: `http://localhost:5173/catedras` (o ingresar como administrador).
2. **Observar la estructura en pantalla única:**
   - **Panel Superior / Izquierdo (Maestro):** Listado interactivo de Cátedras con código ASIS de 9 dígitos, nombre institucional y dependencia.
   - **Panel Inferior / Derecho (Detalle):** Al hacer clic sobre cualquier cátedra de la lista, el detalle de sus reuniones o sesiones programadas se despliega en la misma pantalla.
3. **Validación de Usabilidad (No digitación manual de IDs):**
   - Abrir el modal o formulario de "Nueva Cátedra" o "Nueva Sesión".
   - Constatar que `Tipo de Evento`, `Dependencia`, `Modalidad`, `Sede` y `Período Académico` son menús desplegables (`<select>`) alimentados en tiempo real desde la base de datos.
   - Ningún campo exige escribir a mano un identificador foráneo crudo.

---

## 4. Demostración 3: Protección de Integridad Referencial (`409 Conflict / 422`)

Este paso demuestra el manejo de errores relacionales frente al docente:

1. **Intento de Violación de FK Saliente:**
   - Intentar insertar una cátedra con una dependencia ficticia `DEP-INEXISTENTE`.
   - **Resultado:** La API rechaza la petición con código `422 Unprocessable Entity` o `400 Bad Request` indicando que la dependencia no existe.
2. **Intento de Eliminación de un Padre con Hijos (`ON DELETE RESTRICT`):**
   - Intentar eliminar la Cátedra #1 (que tiene sesiones asociadas).
   - **Resultado:** PostgreSQL aborta la eliminación con código SQLSTATE `23503` y la API retorna error controlado impidiendo la pérdida de registros.
