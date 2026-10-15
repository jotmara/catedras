# ApiCatedrasUsbmed

> **API REST 100% específica y tipada** para el sistema de cátedras abiertas de la Universidad de San Buenaventura Medellín.
> **48 controladores** generados desde el esquema real de `catedras` (PostgreSQL). **Sin clases genéricas. Sin reflexión en runtime.**

![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?logo=dotnet)
![ASP.NET Core](https://img.shields.io/badge/ASP.NET_Core-10.0-512BD4?logo=dotnet)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17%2F18-336791?logo=postgresql)
![Dapper](https://img.shields.io/badge/Dapper-2.1.66-ff6b35)
![Auth](https://img.shields.io/badge/Auth-JWT_%2B_BCrypt_%2B_OTP-gold?logo=jsonwebtokens)
![Puerto](https://img.shields.io/badge/puerto-7045-blue)
![Controllers](https://img.shields.io/badge/controladores-48-green)
![Certificación](https://img.shields.io/badge/certificaci%C3%B3n-19%2F19_%C2%B7_flujo_18%2F18-brightgreen)

---

## ¿Qué es y por qué existe?

Cátedras Abiertas USB Med sustituye un formulario anónimo de Microsoft Forms y una migración manual al sistema académico **ASIS** (PeopleSoft) que hoy cuesta seis pasos y el cruce a mano de 16.093 filas.

Esta API es la capa de datos y de proceso del sistema: expone las **37 tablas y 6 vistas** de la base [`catedras`](../SOLUCION/), y **además** el flujo que la base no puede exponer sola — el QR, la clave al correo, el registro y la generación del archivo plano del ASIS.

**La decisión de diseño fundamental**, heredada de [`ApiEvalFormativaUsbmed`](../../proyectoEvalFormativa/ApiEvalFormativaUsbmed): cada tabla produce su propio controlador, servicio, repositorio y modelo, con tipos y SQL propios. Y el código **sale de un generador que lee los catálogos de PostgreSQL**: cuando el esquema cambia, se regenera en segundos en vez de parchearse a mano.

---

## Inicio rápido

### 1 · Levantar la base

**Lo más rápido: restaurar el respaldo.** Tres líneas y queda lista, con los datos reales del ASIS y los de prueba:

```bash
dropdb -U postgres catedras && createdb -U postgres catedras
pg_restore -U postgres -d catedras -j 4 sql/backup/catedras_completo_2026-08-13.dump
psql -U postgres -d catedras -f sql/19-funciones-api.sql
```

> La tercera línea **no es opcional**: `19-funciones-api.sql` crea los envoltorios que la capa de procesos invoca, y además fija el `search_path` de las rutinas. Sin ella, `/api/enlace/emitir` y todo el flujo de `/api/acceso` fallan con *«no existe el procedimiento»*.

<details>
<summary><b>¿Prefiere construirla desde cero?</b> — también vale</summary>

```bash
cd ../SOLUCION/fisico_postgres
python preparar-datos.py                     # genera los CSV desde los Excel del ASIS
psql -U postgres -f ejecutar-todo.sql        # 37 tablas + carga real, ~30 s
cd ../../ApiCatedrasUsbmed
psql -U postgres -d catedras -f sql/19-funciones-api.sql
```
</details>

<details>
<summary><b>¿Con pgAdmin, sin consola?</b></summary>

1. Clic derecho en *Databases* → **Create → Database…** → `catedras`
2. Clic derecho sobre `catedras` → **Restore…** → *Format*: **Custom or tar** → el archivo `.dump` → **Restore**
3. *Query Tool* sobre `catedras` → pegue `sql/19-funciones-api.sql` → **F5**

Si sale *«pg_restore not found»*: **File → Preferences → Paths → Binary paths** → `C:\Program Files\PostgreSQL\18\bin`

Detalle completo en [`sql/backup/README.md`](sql/backup/README.md).
</details>

### 2 · Arrancar

```bash
dotnet run
# → http://localhost:7045/swagger
```

No hace falta configurar nada más: `appsettings.json` ya trae los valores de desarrollo.

**Credenciales para entrar** — en `POST /api/autenticacion/token`:

```json
{ "email": "admin.catedras@usbmed.edu.co", "contrasena": "Catedras2026*" }
```

> ⚠️ Son de desarrollo. Ver la advertencia de abajo y la [guía paso a paso](docs/paso-a-paso.md).

---

## ⚠️ ADVERTENCIA · los secretos están en claro

> **`appsettings.json` contiene ahora mismo, en texto plano y versionados en el repositorio:**
>
> - la contraseña de PostgreSQL
> - la clave de firma del JWT
>
> **Es una comodidad temporal de desarrollo. NO puede salir así a producción.**

### Por qué importa

| Riesgo | Consecuencia |
|---|---|
| La clave de PostgreSQL está en el repositorio | Cualquiera con acceso al código entra a la base con **todos los datos personales**: 14.808 documentos, nombres y correos |
| `Jwt:Key` está en el repositorio | Con esa clave se pueden **falsificar tokens** y entrar como `ADMIN` sin contraseña |
| Git guarda el historial | Quitarlas después **no las borra**: siguen en los commits anteriores |
| La API se conecta como `postgres` | Se pierde el diseño de cuatro roles de `17-usuarios-permisos.sql`, incluido que la aplicación **no pueda leer `asistente`** |

### Qué hay que hacer antes de desplegar

**1 · Vaciar los tres valores de `appsettings.json`:**

```json
"ConnectionStrings": { "Postgres": "", "PostgresApp": "" },
"Jwt": { "Key": "" }
```

La API tiene *fail-fast*: **no arranca** si están vacíos y no se aportan por otra vía. Eso es a propósito.

**2 · Pasarlos por variables de entorno.** En la unidad de `systemd`:

```ini
Environment=ConnectionStrings__Postgres=Host=...;Username=u_gestor_catedras;Password=...
Environment=ConnectionStrings__PostgresApp=Host=...;Username=u_app_web;Password=...
Environment=Jwt__Key=<clave nueva, aleatoria, de 32+ caracteres>
Environment=Correo__Activo=true
Environment=Correo__Smtp__Usuario=...
```

El doble guion bajo `__` es el separador de secciones de .NET: `ConnectionStrings__Postgres` equivale a `ConnectionStrings:Postgres`.

**3 · En local, si prefiere no tocar `appsettings.json`**, use los *user-secrets*, que se guardan **fuera del repositorio**:

```bash
dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:Postgres" "Host=localhost;Database=catedras;Username=postgres;Password=..."
dotnet user-secrets set "Jwt:Key" "una-clave-de-al-menos-32-caracteres..."
```

**4 · Dar de baja el usuario de prueba** `admin.catedras`, cuya contraseña está en claro en este README, y crear los administradores reales con su correo institucional y un hash BCrypt de coste 12.

**5 · Cambiar la `Jwt:Key`.** La que está en el repositorio se considera comprometida desde el momento en que se subió: hay que generar una nueva para producción.

**6 · Usar los dos roles de base de datos**, no `postgres`. `PostgresApp` debe apuntar a `rol_app_registro`, que **no puede leer la tabla `asistente`** — así, si la aplicación web se ve comprometida, no puede volcarse el maestro de personas.

---

## El flujo, de principio a fin

Hay **dos caminos distintos** y conviene no confundirlos: uno lo recorre el administrador desde su escritorio, el otro lo recorre el asistente desde su celular en el auditorio.

### Camino A · El ADMINISTRADOR prepara la cátedra

Entra con **usuario y contraseña**. Todo lo suyo exige token JWT.

```
1.  POST /api/autenticacion/token
    { "email": "admin.catedras@usbmed.edu.co", "contrasena": "Catedras2026*" }
    → token JWT  +  sus roles vigentes        ↑ credenciales de DESARROLLO
                                    │
2.  POST /api/catedra               │  crea la cátedra (o ya viene del ASIS)
    POST /api/sesion                │  crea la sesión: fecha, sede, modalidad, cupo
                                    │  numero_reunion lo pone el disparador
                                    ▼
3.  POST /api/enlace/emitir         EL BOTÓN
    { "id_sesion": 5712, "minutos_antes": 30, "minutos_despues": 30 }
    → id_enlace  ·  revoca el enlace anterior  ·  fija la ventana horaria
                                    │
4.  GET /api/enlace/{id}/qr         → el PNG del QR, listo para proyectar
                                    │
                            ┌───────┴───────────────────────────┐
                            │  Presencial → se proyecta el QR   │
                            │  Virtual    → se envía la URL     │
                            └───────────────────────────────────┘
```

### Camino B · El ASISTENTE se registra

**No tiene usuario ni contraseña.** Escanea el QR y entra. Los cuatro endpoints son anónimos.

```
5.  GET /api/acceso/enlace/{token}          ← el token viene dentro del QR
    → nombre de la cátedra, sede, modalidad, si la ventana está abierta
    Es la pantalla de bienvenida con la imagen corporativa
                                    │
6.  POST /api/acceso/solicitar-clave
    { "identificador": "...", "token": "..." }
       └── acepta CUALQUIERA de las tres:  código del ASIS · cédula · correo
    → el sistema envía una clave de 6 dígitos al correo de la persona
    → devuelve el correo ENMASCARADO: as**********@usbmed.edu.co
                                    │
7.  POST /api/acceso/validar
    { "id_clave": 4711, "clave": "482913" }
    → QUEDA REGISTRADA LA ASISTENCIA
    → el disparador guarda las instantáneas de programa y vinculación
                                    │
8.  POST /api/acceso/registro/{id}/encuesta
    → la encuesta rápida de calidad
```

### Camino A otra vez · El ADMINISTRADOR migra al ASIS

```
9.  GET  /api/v_pendiente_migracion         quién falta, quién no se puede migrar
10. GET  /api/migracion/sesion/{id}/previsualizar    lo que va a salir, en JSON
11. POST /api/migracion/sesion/{id}/generar          crea el lote y su detalle
12. GET  /api/migracion/sesion/{id}/archivo          EL ARCHIVO PLANO (.xlsx)
                                    │
                            se sube a Carga Info Cátedra del ASIS
                                    │
13. PUT /api/migracion/lote/{id}/resultado
    { "estado": "CORRECTO", "instancia_proceso_asis": "9284471" }
    → cierra el ciclo con el Monitor Procesos
```

### Por qué la clave al correo

**No es autenticación: es evitar que una persona registre a otra.** Sin ella, cualquiera podría escanear el QR y digitar el código de un compañero que no fue.

Tiene un límite conocido y aceptado: alguien puede pedirle el código a otro por teléfono. Se mitiga con la ventana horaria corta y se vigila con el informe de embudo (`/api/v_embudo_registro`).

### Las tres defensas del camino anónimo

| Defensa | Por qué |
|---|---|
| **Límite de tasa por IP** | El QR está proyectado en público: sin límite, sería fuerza bruta sobre la clave de 6 dígitos |
| **Respuesta uniforme** aunque el identificador no exista | Si contestara «no existe», serviría para **enumerar el maestro de 14.808 personas** |
| **Correo enmascarado** en la respuesta | Devolver la dirección completa a un anónimo sería filtrar el directorio institucional |

### Quién puede llamar a qué

| Endpoint | Quién |
|---|---|
| `GET /` · `GET /salud` | Cualquiera |
| `POST /api/autenticacion/token` | Cualquiera — es el emisor de tokens |
| **`/api/acceso/*`** (4 endpoints) | **Cualquiera** — es el asistente con el QR |
| Las 43 tablas y vistas | Requiere JWT |
| `/api/enlace/*` | Requiere JWT con rol `ADMIN` o `COORDINADOR` |
| `/api/migracion/*` | Requiere JWT con rol `ADMIN` |

---

## Cómo usar Swagger

> 📖 **Hay una guía completa paso a paso:** [`docs/paso-a-paso.md`](docs/paso-a-paso.md) — los 16 pasos, de arrancar la API a descargar el archivo del ASIS, con qué debe salir en cada uno y qué hacer si falla.

Casi todos los endpoints llevan `[Authorize]`, así que lo primero es conseguir el JWT.

### 0 · Arrancar la API

```powershell
cd C:\Users\fcl\OneDrive\Desktop\proyectoCatedras\ApiCatedrasUsbmed
dotnet run
```

Se abre solo el navegador en **http://localhost:7045/swagger**

### 1 · Pedir el token

Sección **Autenticacion**, la **primera** de la página → **`POST /api/autenticacion/token`** → botón **Try it out**.

Aparece un cuadro editable con la plantilla:

```json
{
  "email": "string",
  "contrasena": "string"
}
```

Reemplace los `"string"` por **estas credenciales de desarrollo** y pulse **Execute**:

```json
{
  "email": "admin.catedras@usbmed.edu.co",
  "contrasena": "Catedras2026*"
}
```

> ### ⚠️ Estas credenciales son SOLO de desarrollo
>
> El usuario `admin.catedras` y su contraseña **están sembrados en la base de pruebas** por `14-datos-prueba.sql`, y aparecen aquí en claro para que cualquiera pueda levantar el proyecto y probarlo en dos minutos.
>
> **En producción no pueden existir.** Antes de desplegar:
>
> | Qué | Cómo |
> |---|---|
> | **Borrar el usuario de prueba** | `UPDATE catedras.usuario SET activo = false WHERE usuario = 'admin.catedras';` |
> | **Crear los administradores reales** | Con su correo institucional y un hash BCrypt de **coste 12** en `clave_hash`. Nunca la contraseña en claro |
> | **La contraseña la elige la persona**, no el repositorio | Y no se escribe en ningún archivo del proyecto |
> | **La cadena de conexión y `Jwt:Key`** | Por **variables de entorno**, no en `appsettings.json` — ver la advertencia del principio de este README |
>
> ```ini
> # unidad de systemd
> Environment=ConnectionStrings__Postgres=Host=...;Username=u_gestor_catedras;Password=...
> Environment=ConnectionStrings__PostgresApp=Host=...;Username=u_app_web;Password=...
> Environment=Jwt__Key=<clave nueva, aleatoria, de 32+ caracteres>
> ```
>
> **La regla:** en este README las credenciales están en claro **a propósito**, para que arranque sin fricción. En el servidor **nada de esto puede estar escrito en un archivo versionado.**

En *Response body* sale la respuesta. **Copie el valor de `token`.**

```json
{
  "estado": 200,
  "mensaje": "Autenticacion exitosa.",
  "usuario": "admin.catedras",
  "roles": ["ADMIN", "CONSULTA"],
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expiracion": "..."
}
```

> **`POST /api/autenticacion/token` es el ÚNICO sitio donde se digitan usuario y contraseña.**
> El botón **Authorize** no los pide: solo recibe el token que devuelve este endpoint.

### 2 · Autorizar la sesión de Swagger

Botón verde **Authorize** 🔓, arriba a la derecha. Pegue **solo el JWT**, sin comillas y sin nada más:

```
eyJhbGciOiJIUzI1NiIs...
```

→ **Authorize** → **Close**. El candado pasa a cerrado 🔒 y ya funcionan los 48 controladores.

> #### ¿Qué es «Bearer» y por qué no hay que escribirlo?
>
> La cabecera HTTP `Authorization` lleva siempre **el nombre del esquema** y después la credencial:
>
> ```
> Authorization: Basic  dXN1YXJpbzpjbGF2ZQ==
> Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
>                └──┬─┘ └────────┬──────────┘
>                esquema      credencial
> ```
>
> **`Bearer` significa «al portador»**: quien lleve este token, pasa — no hace falta demostrar nada más. Está definido en el **RFC 6750** y es el esquema que espera `AddJwtBearer` en `Program.cs`. Si falta la palabra, el servidor no sabe cómo interpretar lo que recibe y responde `401` con la cabecera `www-authenticate: Bearer`, que es su forma de decir *«use el esquema Bearer»*.
>
> **No hay que escribirla a mano.** El esquema de seguridad está declarado como `Http` + `bearer` en `Program.cs`, así que **Swagger antepone la palabra sola**. Basta con pegar el token.
>
> *(La API de referencia lo declara como `ApiKey`, y ahí sí hay que escribir `Bearer ` delante. Se cambió a propósito: olvidarlo produce un 401 desconcertante.)*
>
> Fuera de Swagger —desde `curl`, desde el front— **sí hay que ponerla**, porque ahí no hay nadie que la añada:
>
> ```bash
> curl http://localhost:7045/api/catedra -H "Authorization: Bearer eyJhbGciOi..."
> ```

### 3 · Probar

Cualquier endpoint, por ejemplo **`GET /api/tipo_evento`** → **Execute** → devuelve los ocho tipos de evento del ASIS.

### El flujo del asistente, desde Swagger

`GET /api/acceso/enlace/{token}` **no** pide `Authorize` —es la pantalla que ve quien escanea el QR—, pero necesita un **token de enlace**, que es un UUID, no el JWT. Para obtener uno:

1. **`GET /api/enlace_registro`** → **Execute** (esto sí requiere estar autorizado).
2. En la respuesta, copie el campo `token` de cualquier enlace.
3. Péguelo en `/api/acceso/enlace/{token}` → **Execute**.

Si `ventana_abierta` sale `false`, ese enlace está fuera de su franja horaria: es el comportamiento correcto de RN-15. Emita uno nuevo con `POST /api/enlace/emitir`.

> **Las secciones no van en orden alfabético.** `Helpers/OrdenSwagger.cs` pone arriba lo que se usa primero —Autenticacion, Acceso, Enlace, Migracion, Raiz, Estructura— y deja las 41 tablas detrás. Con 48 grupos, el alfabeto dejaba `Autenticacion` enterrado justo cuando es por donde hay que empezar.

> **Swagger solo se publica en `Development`**, igual que en la API de referencia. En producción la interfaz no se expone.

---

## Regenerar tras un cambio de esquema

```bash
python generador/generar.py     # relee los catálogos y reemite las 43 relaciones
dotnet build
```

---

## Los 48 controladores

| Grupo | Cantidad | Qué hacen |
|---|---:|---|
| **Tablas** | 36 | CRUD tipado generado |
| **Tablas a mano** | 1 | `enlace_registro` — lleva un `tstzrange` |
| **Vistas** | 6 | Solo lectura. Tres de ellas son **controles** |
| `Autenticacion` | 1 | Camino A · administrador: **JWT + BCrypt por correo**, con roles vigentes |
| **`Acceso`** | 1 | **Camino B · asistente: QR → clave al correo → registro** |
| `Enlace` | 1 | Emite el enlace y genera el QR en PNG |
| `Migracion` | 1 | **El archivo plano del ASIS** |
| `Estructura` | 1 | Metadata de columnas |
| `Raiz` | 1 | `GET /` con la ficha de la API y `GET /salud` como sonda de vida |

---

## El contrato

- **Rutas en snake_case** iguales al nombre real de la tabla: `/api/registro_asistencia`, `/api/programa_academico`
- **JSON en snake_case** igual a las columnas: `fk_asistente`, `numero_reunion`, `es_correo_institucional`
- **PK real en la ruta**, incluida la compuesta: `/api/vinculacion_asistente/{asistente}/{tipo}/{fecha_ini}`
- Respuestas de escritura: `{ "mensaje": "Registro creado|actualizado" }`
- **JWT obligatorio en todo** salvo `/`, `/salud`, el emisor de tokens y los tres endpoints de `/api/acceso`
- **Los `GET` de listado están topados**: 100 filas por defecto, 1000 como máximo. El tope viaja en las cabeceras `X-Limite-Aplicado` y `X-Filas-Devueltas`
- `Jwt:Key` y las cadenas de conexión **no van hardcodeadas**: la API no arranca sin ellas

### Autenticación · camino A, administrador

```http
POST /api/autenticacion/token
{ "email": "admin.catedras@usbmed.edu.co", "contrasena": "****" }

→ { "estado": 200, "roles": ["ADMIN","CONSULTA"], "token": "eyJ...", "expiracion": "..." }
```

Se entra con el **correo institucional**; también valen el correo personal y el login de `usuario`. El token lleva **solo los roles vigentes**: `rol_por_usuario` es histórico y un administrador destituido no debe seguir siéndolo.

### Autenticación · camino B, asistente

```http
GET  /api/acceso/enlace/{token}          → la cátedra y si la ventana está abierta
POST /api/acceso/solicitar-clave         { "identificador": "...", "token": "..." }
POST /api/acceso/validar                 { "id_clave": 4711, "clave": "482913" }
POST /api/acceso/registro/{id}/encuesta
```

`identificador` acepta **las tres vías**: código del ASIS, número de documento o correo.

---

## Tope de los listados

Ningún `GET` de listado devuelve la tabla entera.

| | Sin tope | Con tope |
|---|---:|---:|
| `GET /api/asistente` | 14.811 filas · **5,3 MB** | 100 filas · **35 KB** |
| `GET /api/catedra` | 5.501 filas · **1,3 MB** | 100 filas · **24 KB** |

**Por defecto 100 filas; el techo duro son 1000.** Ni pidiendo `?limite=99999` se devuelven más. Está en [`Helpers/Paginacion.cs`](Helpers/Paginacion.cs) y lo aplica el repositorio, no el controlador: así no hay forma de saltárselo.

Son dos problemas en uno:

1. **Protección de datos.** Sin tope, **una sola petición vuelca el maestro de personas** con sus documentos y correos. El plan lo anotó como riesgo (§7.2, punto 3).
2. **Rendimiento del cliente.** La API sirve 1,3 MB en 45 ms —la base no es el cuello de botella—, pero el navegador tarda varios segundos en pintar ese JSON en Swagger.

El tope **no sustituye a la autorización por rol**: la complementa.

---

## Arquitectura

```
Cliente ──JWT──► Controller ──► IServicio ──► IRepositorio ──Dapper──► PostgreSQL
                 [Authorize]     lógica        SQL fijo por tabla       catedras
                 try/catch                     [Column] real
                 traceId
                     │
                     └── FiltroExcepcionPostgres:  23505→409 · 23514→422 · 23503→400
```

Y la capa que la API de referencia no tiene:

```
Controller de proceso ──► IServicio ──► IRepositorio ──► catedras.fn_*_api()
                                                              └─► CALL sp_*
```

**Principios:** SRP (controlador enruta / servicio decide / repositorio consulta), DIP (todo por interfaces, **86 pares en DI**), OCP (tabla nueva = clases nuevas, regeneradas).

---

## Lo que este proyecto añade a la arquitectura de referencia

`ApiEvalFormativaUsbmed` es **CRUD puro más autenticación**. Aquí eso no basta, y seis problemas no se podían copiar. Están documentados en [`docs/diferencias_con_evalformativa.md`](docs/diferencias_con_evalformativa.md).

| # | Problema | Solución |
|---|---|---|
| 1 | **`tstzrange`** no tiene equivalente en C# | Se expone como `ventana_inicio` / `ventana_fin`; el repositorio reconstruye el rango. **No se toca la base**: el rango es lo que hace declarativas dos reglas |
| 2 | **Columnas generadas** rompen `ConexionHelper` | Honra `[DatabaseGenerated(Computed)]`. Sin esto, *todo* `POST /api/catedra` fallaba |
| 3 | Las claves son **`bigint`**, no `int` | `long` en todo el modelo y `{id:long}` en las rutas |
| 4 | **Cuatro tablas con clave compuesta** sin sustituto | Rutas de varios segmentos. No se les añade una PK artificial |
| 5 | Las reglas viven en **disparadores** | `FiltroExcepcionPostgres` traduce `SqlState` a HTTP y devuelve el mensaje `RN-xx` tal cual |
| 6 | **`DELETE` está revocado** en la base (RN-32) | Devuelve `405` con el motivo, en vez de anunciar en Swagger algo que siempre fallaría |

Y **un segundo camino de autenticación**, público, con límite de tasa y **respuesta uniforme ante identificador inexistente**: sin eso, el endpoint del QR sería un oráculo para enumerar el maestro de 14.808 personas.

---

## El endpoint más delicado

`GET /api/migracion/sesion/{id}/archivo` produce el archivo que se sube al ASIS. El manual de migración es explícito: *«únicamente haya información en las tres columnas correspondientes»*.

**Se verifica automáticamente** en [`pruebas/flujo-completo.sh`](pruebas/flujo-completo.sh):

- 3 columnas exactas · sin fila de encabezado
- ID **como texto** — como número, Excel destrozaría `1000513C` y los ceros a la izquierda
- Sin espacios sobrantes — por eso el código de programa es `varchar(5)` y no `char(5)`

---

## Certificación

```bash
bash pruebas/certificacion.sh       # 19/19 · contrato, tipos, seguridad, barrido de humo
bash pruebas/flujo-completo.sh      # 18/18 · el recorrido de punta a punta
```

**Última ejecución:** contrato **19/19**, flujo **18/18**, **0 controladores con error 500**.

El flujo completo ejercita: emitir enlace → QR en PNG → clave al correo → rechazo de clave incorrecta (`422`) → registro → **instantáneas puestas por el disparador** → doble registro rechazado (`409`) → encuesta → lote → archivo plano.

---

## Seguridad

| Medida | Dónde |
|---|---|
| Fail-fast sin `Jwt:Key` (y mínimo 32 caracteres) | `Program.cs` |
| Secretos **vacíos** en `appsettings.json` | — |
| CORS por lista; nunca `AllowAnyOrigin` | `Program.cs` |
| `clave_hash` **nunca** se serializa | `[JsonIgnore]` en los modelos |
| Límite de tasa en el camino público | `RateLimiter` nativo |
| Respuesta uniforme ante identificador inexistente | `AccesoController` |
| Correo del destinatario **enmascarado** | `ProcesoAccesoServicio` |
| **Dos cadenas de conexión** con roles distintos | `FabricaConexion` |
| Listas blancas de columnas | Todos los repositorios |

> **Sobre las dos cadenas.** `17-usuarios-permisos.sql` creó cuatro roles con permisos comprobados —incluido que la aplicación **no puede leer `asistente`**—. Si la API se conectara siempre como superusuario, ese diseño no serviría de nada. Configure `ConnectionStrings:PostgresApp` con el rol `rol_app_registro`.

---

## Mantenimiento: el generador es la fuente de verdad

Ante un cambio de esquema:

1. `python generador/generar.py`
2. Pegar `generador/di.generado.txt` en `Program.cs`
3. `dotnet build` y correr las dos baterías

**No parchear los controladores a mano**: cualquier corrección va al generador. Durante la construcción de esta API el generador se corrigió tres veces —colisión de nombre con `usuario.usuario`, DI de las relaciones escritas a mano, y el rethrow de `PostgresException`— y las tres quedaron para todas las regeneraciones futuras.

Las relaciones que el generador **salta a propósito** están en `OMITIR`: `enlace_registro` y `v_control_ventana`, por el `tstzrange`.

---

## Documentación

| Documento | Contenido |
|---|---|
| **[docs/paso-a-paso.md](docs/paso-a-paso.md)** | **Los 16 pasos para probar el sistema entero desde Swagger** |
| [docs/diferencias_con_evalformativa.md](docs/diferencias_con_evalformativa.md) | Qué se copió, qué cambió y por qué |
| [sql/19-funciones-api.sql](sql/19-funciones-api.sql) | Envoltorios `CALL`→`SELECT` y el arreglo de `search_path` |
| **[sql/backup/](sql/backup/)** | **Respaldo de la base**, con evidencia de restauración. ⚠️ Contiene datos personales |
| [../PLAN-API-CATEDRAS-USBMED.md](../PLAN-API-CATEDRAS-USBMED.md) | El plan que originó este proyecto |
| [../SOLUCION/](../SOLUCION/) | El diseño de la base: conceptual, lógico y físico |

## Despliegue

- Servicio `systemd`: `catedras-api-usbmed`, puerto **7045**, solo localhost
- **Los puertos 7035 y 7102 no se tocan**: la producción de EvalFormativa corre en paralelo
- Secretos por variables de entorno en la unidad, **nunca** en `appsettings.json`
- `Restart=always` y `RestartSec=5`

---

*Universidad de San Buenaventura Medellín — Proyecto Cátedras Abiertas — Carlos Arturo Castro Castro*
