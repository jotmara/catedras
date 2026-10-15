# Diferencias con ApiEvalFormativaUsbmed

Este proyecto replica la arquitectura de [`ApiEvalFormativaUsbmed`](../../../proyectoEvalFormativa/ApiEvalFormativaUsbmed). Este documento recoge **qué se copió, qué se cambió y por qué** — y sirve de cuaderno de bitácora de los fallos que aparecieron al construirla.

---

## 1 · Lo que se copió, sin tocar

| Aspecto | Detalle |
|---|---|
| **Stack** | .NET 10, ASP.NET Core, **Dapper** (no Entity Framework), Npgsql, BCrypt, JwtBearer, Swashbuckle |
| **Una clase por tabla** | Modelo + interfaz de repositorio + repositorio + interfaz de servicio + servicio + controlador |
| **Sin genéricos ni reflexión en runtime** | La reflexión ocurre al construir el SQL, no por petición |
| **snake_case** | En rutas (`SnakeCaseRouteTransformer`) y en JSON (`JsonNamingPolicy.SnakeCaseLower`) |
| **`[Table]` y `[Column]`** | Con el `CustomPropertyTypeMap` global de Dapper |
| **`DateOnlyTypeHandler`** | Columnas `date` ↔ `DateOnly` |
| **Fail-fast** | Sin `Jwt:Key` la API no arranca; secretos vacíos en `appsettings.json` |
| **CORS por lista** | Sin orígenes configurados no pasa ningún cross-origin |
| **Estructura de carpetas** | `Helpers/ Modelos/ Repositorios/ Servicios/ Controllers/ docs/` |
| **El generador como fuente de verdad** | *«No parchear los controladores a mano»* |

---

## 2 · Lo que se quitó

### 2.1 · El soporte multi-proveedor

La referencia trae un `switch` sobre `DatabaseProvider` con SqlServer, MySQL, Oracle y SQLite en **cada repositorio**.

**Aquí se eliminó, y es deliberado.** El esquema usa `citext`, `inet`, `jsonb`, `uuid`, `tstzrange`, `EXCLUDE USING gist`, índices parciales y columnas generadas. Ninguno de esos motores puede sostener este modelo. Mantener el `switch` sería **código que miente**: anunciaría un soporte que no existe.

> Ese `switch` es un artefacto del generador de la referencia, no un requisito de su arquitectura. Quitarlo no rompe ningún principio: los repositorios siguen siendo específicos y tipados.

### 2.2 · Los módulos `Agente` y `Conocimiento`

No se incluyen en la v1. El hueco queda declarado en el plan.

---

## 3 · Los seis problemas técnicos que no se podían copiar

### 3.1 · `tstzrange` — el tipo que rompe el molde

`enlace_registro.ventana` es un rango de tiempo. Npgsql lo entrega como `NpgsqlRange<DateTimeOffset>`, que no serializa a un JSON que un cliente sepa construir.

**La tentación** era cambiar la base a dos columnas `timestamptz`. Se descartó: el rango es justamente lo que hace **declarativas** dos reglas — el `EXCLUDE USING gist` que impide enlaces solapados (RN-36) y la contención `@>` de la ventana (RN-15). Con dos columnas, las dos volverían a ser código que alguien tendría que mantener.

**Se adapta la API, no el modelo.** `EnlaceRegistro` expone `ventana_inicio` y `ventana_fin`; `EnlaceRegistroRepositorio` es el **único** repositorio con SQL a mano:

```sql
-- lectura
lower(ventana) AS ventana_inicio, upper(ventana) AS ventana_fin
-- escritura
tstzrange(@VentanaInicio, @VentanaFin, '[)')
```

El `'[)'` es el mismo que usa `sp_emitir_enlace`: inicio incluido, fin excluido.

### 3.2 · Columnas generadas

`catedra.nombre_asis` es `GENERATED ALWAYS AS (left(nombre,30)) STORED`. PostgreSQL **rechaza** cualquier `INSERT` que la mencione.

`ConexionHelper` de la referencia solo excluye `[Key]`. **Sin la corrección, todo `POST /api/catedra` fallaba con el error 42601.** Ahora honra `[DatabaseGenerated(DatabaseGeneratedOption.Computed)]`.

### 3.3 · `bigint`, no `int`

La referencia usa `int` porque su esquema usa `serial`. Aquí todas las claves sustitutas son `bigint` → **`long`**, y las rutas llevan `{id:long}`. Copiar `int` habría sido un error silencioso hasta pasar de 2.147.483.647.

### 3.4 · Claves compuestas sin sustituto

Cuatro tablas —`vinculacion_asistente`, `programa_asistente`, `ponencia`, `rol_por_usuario`— tienen clave compuesta. La única tabla de unión de la referencia, `rol_usuario`, tiene un `id` sustituto y se resuelve como cualquier otra.

**No se les añade uno**: `fecha_ini` está en la clave por una razón de negocio —que alguien pueda recuperar un rol o una vinculación que ya tuvo—. Se usan **rutas de varios segmentos**:

```
GET /api/vinculacion_asistente/{fkAsistente}/{fkTipoVinculacion}/{fechaIni}
```

### 3.5 · Las reglas viven en disparadores

`FiltroExcepcionPostgres` traduce `SqlState` a HTTP:

| SqlState | HTTP | |
|---|---|---|
| `23505` | **409** | ya existe |
| `23503` | 400 | referencia inexistente |
| `23514` | **422** | **regla de negocio: se devuelve el mensaje `RN-xx` tal cual** |
| `23P01` | 409 | rangos solapados |
| `42501` | 403 | sin permiso de base de datos |

Los disparadores de esta base ya escriben el mensaje en español y con su número de regla, así que **es la mejor documentación de errores posible y sale gratis**.

### 3.6 · `DELETE` está revocado

`17-usuarios-permisos.sql` revoca `DELETE` en todas las tablas y para todos los roles (RN-32). Los `DELETE` generados devuelven **`405`** con el motivo, en vez de anunciar en Swagger una operación que siempre fallaría con error de permisos.

---

## 4 · Lo que se añadió

### 4.1 · La capa de procesos

La referencia es CRUD puro. Aquí el registro de un asistente **no es un `INSERT`**: es pedir clave → validarla → registrar con instantáneas → dentro de la ventana → respetando el cupo. Todo eso vive en procedimientos, y un `INSERT` directo sobre `registro_asistencia` saltaría la mitad de las reglas.

Tres controladores de proceso —`Acceso`, `Enlace`, `Migracion`— cuyos repositorios **llaman a las rutinas** en vez de componer SQL.

### 4.2 · Un segundo camino de autenticación

La referencia tiene **un** endpoint anónimo. Aquí son tres, porque el QR se proyecta en un auditorio y el asistente no tiene credenciales.

**Y se invierte una decisión de la referencia a propósito.** Su `AutenticacionController` distingue `404 Usuario no encontrado` de `401 Contraseña incorrecta` — correcto para una pantalla interna. En `/api/acceso` eso convertiría el endpoint en un **oráculo para enumerar el maestro de 14.808 personas**, así que la respuesta es siempre neutra.

### 4.3 · Roles en el token

La referencia solo distingue autenticado de anónimo. Aquí el JWT lleva los **roles vigentes** como *claims*, filtrando por `fecha_fin`: `rol_por_usuario` es histórico y un administrador destituido no debe seguir siéndolo.

### 4.4 · Dos cadenas de conexión

`FabricaConexion` expone `Crear()` y `CrearApp()`. El camino público usa el rol mínimo, que **no puede leer `asistente`**.

### 4.5 · Envoltorios `CALL` → `SELECT`

Los procedimientos usan parámetros `INOUT` y se invocan con `CALL`, que no devuelve un conjunto de resultados y que Dapper no puede consumir de forma portable. [`sql/19-funciones-api.sql`](../sql/19-funciones-api.sql) añade cinco funciones que hacen el `CALL` por dentro y **devuelven** el resultado. No duplican lógica: cada una es un `CALL` y un `RETURN`.

---

## 5 · Los fallos que aparecieron al construirla

Ninguno se veía leyendo el código. Los cinco salieron de ejecutar.

| # | Síntoma | Causa | Dónde se corrigió |
|---|---|---|---|
| 1 | `CS0542: los nombres de los miembros no pueden coincidir con sus tipos envolventes` | La tabla `usuario` tiene una columna `usuario` | **En el generador**: `prop_nombre()` antepone `Nombre` y `[Column]` conserva el nombre real |
| 2 | `Unable to resolve service for type 'IVControlVentanaServicio'` | El generador solo añadía a la lista de DI las relaciones saltadas por `OMITIR`, no las saltadas por tipo desconocido | **En el generador** |
| 3 | Un duplicado devolvía **500** en vez de **409** | `IExceptionFilter` solo actúa sobre excepciones **no capturadas**, y el `try/catch` de los controladores se las tragaba | **En el generador**: `catch (PostgresException) { throw; }` |
| 4 | `The ConnectionString property has not been initialized` | `appsettings.json` trae `"PostgresApp": ""` a propósito, y **la cadena vacía no es `null`**: el `?? _admin` no se disparaba | `FabricaConexion` |
| 5 | `no existe la relación «registro_asistencia»` y `no existe el procedimiento «sp_emitir_enlace(...)»` | Las rutinas del modelo referencian las tablas **sin calificar** y se crearon bajo un `SET search_path` de **script**, que no queda horneado en la función | **En la base**: `ALTER FUNCTION … SET search_path` sobre las 22 rutinas, más `Search Path` en la cadena de conexión como cinturón |

> **El número 5 es un fallo latente de la capa de base de datos**, no de la API: existía desde que se escribió el script 11 y solo se manifiesta cuando un cliente llama a las rutinas sin fijar el `search_path`. Los scripts de `psql` lo fijaban al principio del archivo y por eso nunca falló allí.

---

## 6 · Resumen numérico

| | ApiEvalFormativa | **ApiCatedras** |
|---|---:|---:|
| Tablas | 42 | **37** |
| Vistas | 1 | **6** |
| Controladores | 45 | **48** |
| Pares en DI | ~90 | **86** |
| Archivos `.cs` | ~250 | **293** |
| Repositorios con SQL a mano | 0 | **1** |
| Controladores de proceso | 0 | **3** |
| Endpoints anónimos | 1 | **4** |
| Proveedores de base de datos | 5 | **1** |
| Puerto | 7035 | **7045** |
