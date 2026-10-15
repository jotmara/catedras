# Requisitos No Funcionales (RNF) — Cátedras Abiertas USBMed

Este documento define las especificaciones técnicas de calidad, rendimiento, seguridad, escalabilidad, disponibilidad, mantenibilidad e integridad de datos del sistema **Cátedras Abiertas USBMed**.

---

## 1 · Rendimiento y Eficiencia de Tiempos de Respuesta (RNF-01)

| Criterio | Métrica Objetivo | Solución Arquitectónica Implementada |
|---|---|---|
| **Tiempo de respuesta en registro de asistencia** | `< 200 ms` (p95) | Procesamiento directo mediante procedimiento almacenado PostgreSQL `sp_registrar_asistencia` y micro-ORM Dapper. |
| **Tiempo de respuesta en consultas de catálogo** | `< 50 ms` (p95) | Consultas optimizadas sobre vistas con índices B-Tree y Trigram (`pg_trgm`). |
| **Carga inicial de la interfaz móvil (QR)** | `< 1.0 segundo` | HTML/CSS minimalista sin marcos pesados de frontend. |
| **Consumo de memoria en servidor** | `< 150 MB RAM` | API REST compilada en C# .NET 8 sin reflexión en tiempo de ejecución. |

---

## 2 · Seguridad y Protección de Datos (RNF-02)

> [!IMPORTANT]
> **Cumplimiento de Hábeas Data:** Los datos personales de los asistentes (nombres, documentos, correos) se manejan bajo consentimiento explícito según la tabla `consentimiento_datos` (RN-35).

1. **Autenticación y Autorización:**
   * Tokens JWT (JSON Web Tokens) firmados con algoritmos **HMAC-SHA256**.
   * Las claves secretas se leen desde variables de entorno (`Jwt__Key`) con validación fail-fast (mínimo 32 caracteres).
   * Control de acceso basado en roles (`[Authorize(Roles="ADMIN")]`).
2. **Cifrado de Contraseñas:**
   * Uso incondicional del algoritmo **BCrypt** (work factor 11).
   * Ninguna clave de usuario o código OTP se almacena en texto claro en la base de datos.
3. **Seguridad en Capa de Red y Transporte:**
   * Comunicación obligatoria mediante **HTTPS (TLS 1.3)**.
   * Política estricta de CORS (`Cors:AllowedOrigins`) sin permitir orígenes anónimos (`*`).
4. **Protección contra Inyección SQL y XSS:**
   * Uso exclusivo de consultas parametrizadas con Dapper.
   * Listas blancas estrictas de columnas en ordenamientos y filtros.

---

## 3 · Escalabilidad y Alta Disponibilidad (RNF-03)

1. **Limitador de Tasa de Peticiones (Rate Limiting):**
   * Configuración de middleware `UseRateLimiter` para prevenir ataques de denegación de servicio (DoS) durante los picos de escaneo del código QR en los auditorios.
2. **Disponibilidad:**
   * **Target:** `99.9%` de tiempo de actividad en periodo académico.
   * Ejecución desacoplada en servicio `systemd` en Linux o proceso administrado en Windows Server.
3. **Concurrencia de Base de Datos:**
   * Pool de conexiones asignado en Npgsql (hasta 100 conexiones simultáneas por instancia).

---

## 4 · Mantenibilidad y Calidad del Código (RNF-04)

```
Cliente REST ──► Controller ──► IServicio ──► IRepositorio ──Dapper──► PostgreSQL
```

1. **Regla de Diseño Arquitectónico:**
   * **Una clase por tabla:** Cada entidad produce exactamente 6 archivos (Modelo, IRepositorio, Repositorio, IServicio, Servicio y Controller).
   * Tipado 100% en tiempo de compilación. No se utilizan clases genéricas ni reflexión dinámica en runtime para garantizar trazabilidad estática en el IDE.
2. **Generador Automático de Código:**
   * Script [`generador/generar.py`](file:///c:/Users/jotma/Downloads/proyectoCatedras/proyectoCatedras/ApiCatedrasUsbmed/generador/generar.py) como fuente de verdad: cualquier cambio en el esquema PostgreSQL regenera el código C# respetando las reglas del proyecto.

---

## 5 · Integridad de Datos y Reglas de Negocio en BD (RNF-05)

El sistema garantiza que las **38 reglas de negocio (RN-01 a RN-38)** se cumplan físicamente en la base de datos PostgreSQL mediante:

* **52 Claves Foráneas (FKs)** con borrado/actualización restringida.
* **47 Restricciones Check** (ejemplo: `CHECK (fin > inicio)` en sesiones).
* **7 Disparadores (Triggers)** para auditoría e inmutabilidad.
* **Tipos de datos avanzados:** `tstzrange` para control de ventanas temporales, `citext` para correos insensibles a mayúsculas/minúsculas, e `inet` para direcciones IP de registro.
