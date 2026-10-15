# Análisis y Gestión de Riesgos — Cátedras Abiertas USBMed

Esta guía identifica, evalúa y categoriza los riesgos técnicos, de seguridad, operacionales y de integridad de datos del proyecto **Cátedras Abiertas USBMed**, estableciendo planes de mitigación y contingencia.

---

## 1 · Matriz de Evaluación de Riesgos (Probabilidad vs. Impacto)

La matriz clasifica los riesgos en una escala de 1 a 5 (donde 5 es el valor máximo):

```
IMPACTO ▲
   5    │  [R-02]              [R-01]
   4    │  [R-04]   [R-05]     [R-03]
   3    │           [R-06]     [R-07]
   2    │  [R-08]
   1    │
        └─────────────────────────────► PROBABILIDAD
             1        2     3     4     5
```

---

## 2 · Catálogo Detallado de Riesgos y Controles

| ID | Riesgo | Categoría | Prob. | Imp. | Nivel | Estrategia de Mitigación / Control Implementado |
|---|---|---|---|---|---|---|
| **R-01** | Concurrencia masiva simultánea al escanear QR en auditorio (hasta 500 peticiones en 1 minuto) | Rendimiento / Infraestructura | 4 | 5 | 🔴 **CRÍTICO** | Implementación de `RateLimiter` en ASP.NET Core, pool de conexiones PostgreSQL optimizado, y consultas parametrizadas ligeras en Dapper sin ORM pesado. |
| **R-02** | Alteración o corrupción en el formato del archivo plano exportado para el ASIS | Integridad de Datos | 1 | 5 | 🟠 **ALTO** | Generación estricta vía `ClosedXML` en C#: 3 columnas sin encabezado, forzando texto `@` para preservar ceros a la izquierda e IDs alfanuméricos. |
| **R-03** | Intento de registro fuera de la ventana temporal permitida de la sesión | Regla de Negocio | 4 | 4 | 🟠 **ALTO** | Validación atómica dentro de la base de datos vía tipo `tstzrange` en `enlace_registro` y disparadores en la rutina de almacenamiento. |
| **R-04** | Inyección de SQL mediante parámetros de búsqueda o filtrado | Seguridad | 1 | 4 | 🟡 **MEDIO** | Dapper utiliza consultas SQL 100% parametrizadas. El repositorio valida listas blancas de columnas antes de interpolar. |
| **R-05** | Caducidad o interceptación de Tokens JWT de administración | Seguridad | 2 | 4 | 🟡 **MEDIO** | Firma HMAC-SHA256 con clave secreta de mínimo 32 caracteres, expiración máxima configurable (480 min) y roles incrustados como Claims. |
| **R-06** | Contraseña de administrador insegura o almacenada en texto plano | Seguridad | 2 | 3 | 🟡 **MEDIO** | Hash incondicional mediante `BCrypt.Net-Next` (Work Factor 11). Ninguna contraseña plana se persiste en la BD. |
| **R-07** | Intento de doble registro de asistencia para el mismo estudiante en la misma sesión | Integridad | 4 | 3 | 🟡 **MEDIO** | Restricción `UNIQUE(fk_asistente, fk_sesion)` en la tabla `registro_asistencia`. La base de datos rechaza duplicados a nivel físico. |
| **R-08** | Interrupción o fallo en el envío de correos con la clave OTP | Operativo | 1 | 2 | 🟢 **BAJO** | Diseño fail-closed: la clave se devuelve en el ambiente de desarrollo y se genera registro de log de auditoría. |

---

## 3 · Planes de Contingencia y Recuperación (Disaster Recovery)

> [!WARNING]
> **Contingencia por caída de conexión a PostgreSQL:** La API responde de inmediato con `500 Internal Server Error` estructurado (`{ estado: 500, mensaje: "...", traceId: "..." }`) sin exponer trazas de pila ni información sensible del servidor.

### 3.1 · Plan de Contingencia en Registro de Asistencia (Auditorio)
Si la red Wi-Fi o móvil del auditorio falla durante la cátedra:
1. El enlace de registro permanece activo durante la ventana temporal configurada (ej. hasta 3 horas después del evento).
2. Los estudiantes pueden completar el registro desde cualquier conexión a internet antes del cierre de la ventana.

### 3.2 · Plan de Recuperación de Datos (Backup & Restore)
* **Respaldo Automático:** Script diario mediante `pg_dump` generando archivos `.sql.gz` y `.dump` personalizados.
* **Tiempo Estimado de Recuperación (RTO):** `< 5 minutos` ejecutando `psql -f bdcatedras_completa.sql`.
* **Punto de Recuperación (RPO):** Pérdida máxima de 0 datos gracias al registro de logs WAL en PostgreSQL.
