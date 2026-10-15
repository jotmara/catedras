# Quickstart — Sistema Cátedras USBMed (37 Tablas)

> **Guía Rápida de Despliegue, Validación y Smoke Test Integral**
> Cubre el arranque con Docker Compose, verificación relacional en PostgreSQL y pruebas de extremo a extremo con cURL / PowerShell.

---

## 1. Arranque con Docker en un solo comando

Desde la raíz del proyecto, ejecuta:

```powershell
docker compose up -d --build
```

### Servicios expuestos:
- **API REST Cátedras (.NET 8):** `http://localhost:7045/`
- **Documentación Swagger UI:** `http://localhost:7045/swagger`
- **Portal Web Flask / Front:** `http://localhost:5173/`
- **PostgreSQL 16 Alpine:** `localhost:5432` / Contenedor: `catedras_postgres` (Usuario: `postgres`, BD: `catedras`, Clave: `1064`)

---

## 2. Verificación de Integridad de la Base de Datos

Comprueba que las **37 tablas base** y **6 vistas** se hayan creado e inicializado correctamente dentro del contenedor Docker:

```powershell
# Contar tablas base en el esquema catedras (debe retornar 37)
docker exec catedras_postgres psql -U postgres -d catedras -c "SELECT count(*) AS total_tablas FROM information_schema.tables WHERE table_schema = 'catedras' AND table_type = 'BASE TABLE';"

# Contar vistas de reporte (debe retornar 6)
docker exec catedras_postgres psql -U postgres -d catedras -c "SELECT count(*) AS total_vistas FROM information_schema.tables WHERE table_schema = 'catedras' AND table_type = 'VIEW';"
```

---

## 3. Smoke Test de Endpoints Clave (PowerShell)

### A. Diagnóstico de la API
```powershell
curl.exe http://localhost:7045/
```

### B. Módulo de Catálogos (Sedes y Modalidades)
```powershell
# Listar sedes maestras
curl.exe http://localhost:7045/api/sede

# Obtener sede San Benito
curl.exe http://localhost:7045/api/sede/SAN_BENITO

# Crear nueva sede
curl.exe -X POST http://localhost:7045/api/sede `
  -H "Content-Type: application/json" `
  -d '{"id_sede":"ENVIGADO","nombre":"Campus Envigado","direccion":"Transversal 38 # 25-10","es_virtual":false}'

# Validar 422 en caso de omisión de atributos requeridos
curl.exe -i -X POST http://localhost:7045/api/sede `
  -H "Content-Type: application/json" `
  -d '{"id_sede":"","nombre":""}'
```

### C. Módulo de Cátedras y Sesiones
```powershell
# Listar cátedras registradas
curl.exe http://localhost:7045/api/catedra

# Crear cátedra con evento ASIS (9 dígitos)
curl.exe -X POST http://localhost:7045/api/catedra `
  -H "Content-Type: application/json" `
  -d '{"id_evento_asis":"000035400","nombre":"Cátedra de Innovación y Tecnología","fk_tipo_evento":"CAAB","fk_dependencia":1}'
```

### D. Módulo de Asistencia (OTP y Registro)
```powershell
# Solicitar clave temporal al correo
curl.exe -X POST http://localhost:7045/api/proceso/solicitar_clave `
  -H "Content-Type: application/json" `
  -d '{"token_enlace":"TOKEN_SESION_ACTIVA","identificador":"30000141979"}'
```

### E. Vistas de Monitoreo y Reporte
```powershell
# Consultar asistencia completa
curl.exe http://localhost:7045/api/vista/asistencia_completa?limite=10

# Consultar pendientes por migrar al ASIS
curl.exe http://localhost:7045/api/vista/pendiente_migracion
```

---

## 4. Ejecución de Pruebas Unitarias y de Capas

Para validar el desacoplamiento arquitectónico sin requerir conexión a base de datos externa:

```powershell
dotnet run --project ApiCatedrasUsbmed/pruebas/PruebaCapas.csproj
```
o dentro del contenedor Docker:
```powershell
docker compose exec api-catedras dotnet run --project pruebas
```
