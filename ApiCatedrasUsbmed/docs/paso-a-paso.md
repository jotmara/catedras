# Paso a paso — probar la API desde Swagger

Guía para recorrer el sistema completo sin escribir código: desde entrar como administrador hasta descargar el archivo plano que se sube al ASIS.

**Cada paso dice qué hacer, qué debe salir y por qué.** Si algo no sale como aquí, está la sección [Si algo falla](#si-algo-falla) al final.

> ⚠️ **Las credenciales de esta guía son de DESARROLLO.** El usuario `admin.catedras` está sembrado por `14-datos-prueba.sql` en la base de pruebas. En producción hay que darlo de baja y crear los administradores reales — ver la advertencia del [README](../README.md#️-advertencia--los-secretos-están-en-claro).

---

## Paso 0 · Arrancar la API

```powershell
cd C:\Users\fcl\OneDrive\Desktop\proyectoCatedras\ApiCatedrasUsbmed
dotnet run
```

Se abre solo el navegador en **http://localhost:7045/swagger**

**Debe salir:** la página de Swagger con el título `ApiCatedrasUsbmed` y, como primera sección, **Autenticacion**.

> Si ves `MSB3026 · el archivo se ha bloqueado`, hay otra instancia corriendo. Ciérrala con `Ctrl+C` en su terminal, o:
>
> ```powershell
> Get-Process ApiCatedrasUsbmed | Stop-Process -Force
> ```

---

# CAMINO A · El administrador prepara la cátedra

## Paso 1 · Entrar como administrador

Sección **Autenticacion** → `POST /api/autenticacion/token` → botón **Try it out**.

Pega en el cuadro:

```json
{
  "email": "admin.catedras@usbmed.edu.co",
  "contrasena": "Catedras2026*"
}
```

→ **Execute**

**Debe salir:**

```json
{
  "estado": 200,
  "mensaje": "Autenticacion exitosa.",
  "usuario": "admin.catedras@usbmed.edu.co",
  "roles": ["ADMIN", "CONSULTA"],
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expiracion": "..."
}
```

**Copia el valor de `token`**, sin las comillas.

> **Fíjate en `roles`.** Salen `ADMIN` y `CONSULTA`, pero **no** un tercer `CONSULTA` que ese mismo usuario tuvo entre enero y junio de 2025. La tabla `rol_por_usuario` es histórica —lleva `fecha_ini` en la clave primaria para que alguien pueda recuperar un rol que ya tuvo—, y el token solo carga los **vigentes**. Un administrador destituido deja de serlo.

## Paso 2 · Autorizar Swagger

Botón verde **Authorize** 🔓, arriba a la derecha.

Pega **solo el token**. No escribas la palabra `Bearer`: Swagger la antepone sola.

→ **Authorize** → **Close**

**Debe salir:** el candado cerrado 🔒.

> **¿Qué es «Bearer»?** Es el nombre del esquema en la cabecera HTTP `Authorization`, definido en el RFC 6750, y significa «al portador»: quien lleve este token, pasa. Aquí no hay que escribirlo porque el esquema de seguridad está declarado como `Http` + `bearer`. Fuera de Swagger —`curl`, el front— **sí** hay que ponerlo:
>
> ```bash
> curl http://localhost:7045/api/catedra -H "Authorization: Bearer eyJ..."
> ```

## Paso 3 · Ver los datos reales del ASIS

Sección **Catedra** → `GET /api/catedra` → **Try it out** → deja `limite` **vacío** → **Execute**.

**Debe salir:** un array de **100 cátedras** —no las 5.501 que hay—, en menos de un segundo.

> **Por qué solo 100.** Ningún `GET` de listado devuelve la tabla entera: 100 por defecto, 1000 como techo duro. Mira las cabeceras de la respuesta: `X-Filas-Devueltas: 100`.
>
> No es solo rendimiento. Sin tope, `GET /api/asistente` devolvía **las 14.811 personas del maestro con sus documentos y correos, 5,3 MB, en una sola petición**.

Fíjate en dos campos de cualquier cátedra:

| Campo              | Qué mirar                                                                                                                                            |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id_evento_asis` | **Nueve caracteres con ceros a la izquierda**: `000035392`. Como número se convertiría en `35392` y dejaría de servir para el ASIS       |
| `nombre_asis`    | Recortado a**30 caracteres**. Es una columna **generada** por la base: se guarda el nombre completo y el corto se deriva, nunca al revés |

## Paso 4 · Ver las sesiones

Sección **Sesion** → `GET /api/sesion` → **Try it out** → `limite`: `5` → **Execute**.

Una sesión es **una reunión concreta** de una cátedra: `numero_reunion`, `inicio`, `fin`, `fk_sede`, `fk_modalidad`, `cupo`.

**Copia un `id_sesion`.** Lo necesitas en el paso siguiente.

> **Por qué `catedra` y `sesion` son dos tablas.** Es la distinción entre *el libro* y *el ejemplar*. Una cátedra puede dictarse muchas veces, y el archivo plano del ASIS exige **el número de reunión**, no el de la cátedra. Sin `sesion` no habría qué enviar.

## Paso 5 · Emitir el enlace — «el botón»

Sección **Enlace** → `POST /api/enlace/emitir` → **Try it out** → pega, con **tu** `id_sesion`:

```json
{
  "id_sesion": 5712,
  "minutos_antes": 180,
  "minutos_despues": 180
}
```

→ **Execute**

**Debe salir:** `{ "mensaje": "Enlace emitido", "id_enlace": 7 }`

Por dentro hizo tres cosas en una sola operación:

1. **Revocó el enlace vigente anterior** de esa sesión, si lo había (RN-14: uno vivo por sesión).
2. Generó un **token aleatorio** que no se puede adivinar.
3. Fijó la **ventana horaria**: desde 3 h antes del inicio hasta 3 h después del fin.

**Copia el `id_enlace`.**

## Paso 6 · Descargar el QR

Sección **Enlace** → `GET /api/enlace/{idEnlace}/qr` → **Try it out**.

En el campo `idEnlace` escribe **el número que devolvió el paso 5**:

```json
{ "mensaje": "Enlace emitido", "id_enlace": 9 }
                                            ↑ ese numero va en idEnlace
```

→ **Execute**

**Debe salir:** un PNG. Swagger ofrece **Download file**.

> **`idEnlace` es obligatorio.** Si lo dejas vacío, Swagger no llama a la API: muestra
> *«For 'idEnlace': Required field is not provided»* en rojo. Cada enlace emitido tiene su
> propio número, y sin él la API no sabe de cuál le hablas.

> El QR lo genera la API, no la base. La base solo guarda la **ruta relativa** en `ruta_imagen_qr`, y una restricción rechaza las rutas absolutas: `C:\...` no entra.

## Paso 7 · Conseguir el token del enlace

El QR lleva dentro un **token UUID**, distinto del JWT. Para verlo:

Sección **EnlaceRegistro** → `GET /api/enlace_registro` → **Try it out** → `limite`: `5` → **Execute**.

Busca tu `id_enlace` y **copia su `token`**. Tiene esta forma: `f88a57b3-58f8-400b-b46e-582fd0275419`

Fíjate también en `url_publica`: **es lo que está codificado dentro del QR.**

> ⚠️ **Esa URL todavía no existe.** Apunta a `https://catedras.usbmed.edu.co/r/{token}`, que sale
> del parámetro `URL_BASE` de la tabla `parametro`. Si escaneas el QR con el celular ahora, no
> carga nada: hace falta desplegar el front y cambiar ese parámetro al dominio real.
>
> ```sql
> UPDATE catedras.parametro SET valor = 'https://el-dominio-real/r/' WHERE clave = 'URL_BASE';
> ```

> Fíjate en `ventana_inicio` y `ventana_fin`. En la base **no son dos columnas**: son un `tstzrange`, un tipo de rango que no existe en C#. El repositorio lo proyecta con `lower()`/`upper()` al leer y lo reconstruye con `tstzrange()` al escribir.
>
> Se hizo así, y no al revés, porque el rango es lo que hace **declarativas** dos reglas: que dos enlaces de la misma sesión no se solapen, y que un instante esté dentro de la ventana. Con dos columnas, las dos volverían a ser código.

---

# CAMINO B · El asistente se registra

**Aquí no hace falta el JWT.** Estos cuatro endpoints son anónimos: el asistente escanea el QR con su celular y no tiene credenciales.

## Paso 8 · La pantalla de bienvenida

Sección **Acceso** → `GET /api/acceso/enlace/{token}` → **Try it out** → pega el **token UUID** del paso 7 → **Execute**.

**Debe salir:** el nombre de la cátedra, la sede, la modalidad, el horario y `ventana_abierta`.

Es la pantalla que ve quien escanea: imagen corporativa y el título de la cátedra a la que asiste.

**Dos cosas para fijarse:**

1. **No hizo falta el JWT.** Aunque tengas Swagger autorizado, este endpoint no lo pide: es lo que ve
   quien escanea el QR, y esa persona no tiene credenciales.
2. Es probable que **`ventana_abierta` salga `false`**, porque las sesiones cargadas del ASIS tienen
   fechas de enero. **No es un error: es RN-15 funcionando.**

### Para que la ventana esté abierta

El flujo solo continúa si la sesión está ocurriendo. Dos opciones:

**a) Reubicar la sesión de prueba a ahora** —lo que hace `flujo-completo.sh`—:

```sql
UPDATE catedras.sesion
   SET inicio = date_trunc('hour', now()),
       fin    = date_trunc('hour', now()) + interval '2 hour'
 WHERE id_sesion = 5712;
```

Y volver a emitir el enlace (paso 5), porque la ventana se calcula al emitirlo.

**b) Crear una sesión nueva** con `POST /api/sesion`, con `inicio` y `fin` de hoy.

## Paso 9 · Pedir la clave al correo

`POST /api/acceso/solicitar-clave` → **Try it out**:

```json
{
  "identificador": "1000090",
  "token": "pega-aqui-el-token-uuid"
}
```

→ **Execute**

**Debe salir:** `id_clave` y el correo **enmascarado**: `as**********@usbmed.edu.co`

> ### Tres cosas que hace este endpoint y conviene entender
>
> **1 · `identificador` acepta tres cosas distintas.** Código del ASIS, número de documento **o** correo. Las tres resuelven a la misma persona. Y busca también en documentos **no vigentes**: las 707 personas del maestro que tienen más de un documento son justamente las que digitan el antiguo.
>
> **2 · La clave nunca se guarda en claro.** La base almacena solo su hash. La clave en claro se devuelve al servicio de correo y no sale de ahí.
>
> **3 · Responde lo mismo aunque el identificador no exista.** Pruébalo con `"identificador": "NO_EXISTE"`: la respuesta es idéntica. Si dijera «no encontrado», este endpoint —que está detrás de un QR proyectado en un auditorio— serviría para **enumerar el maestro de 14.808 personas**.

**Si `Correo:Activo` es `false`** (lo es en desarrollo), la clave se genera y se registra pero **no se envía**. Para verla:

```powershell
psql -U postgres -d catedras -c "SELECT id_clave, enviado_a, es_correo_institucional, expira_en FROM catedras.clave_acceso ORDER BY id_clave DESC LIMIT 1"
```

La clave en claro **no se puede recuperar del hash** — es lo correcto. Para probar el paso 10 hay dos opciones: activar el correo, o reescribir el hash con una clave conocida, que es lo que hace `pruebas/flujo-completo.sh`.

## Paso 10 · Validar y quedar registrado

`POST /api/acceso/validar` → **Try it out**:

```json
{
  "id_clave": 4711,
  "clave": "482913"
}
```

→ **Execute**

**Debe salir:** `{ "mensaje": "Registro exitoso.", "id_registro": ... }`

> **Aquí es donde de verdad pasa todo.** El disparador de la base, en el mismo instante:
>
> - comprueba que estás **dentro de la ventana** (RN-15)
> - guarda las **instantáneas** de programa y vinculación (RN-22)
> - deja el programa **en nulo** si tu vinculación no lo exige, como Rutas de Paz (RN-07)
> - comprueba el **cupo** de la sesión (RN-38)
>
> Nada de eso lo hace la API. Por eso este endpoint llama a un procedimiento y no compone un `INSERT`.

**Pruebas que deben FALLAR** — y que fallan bien:

| Prueba                      | Respuesta                                                   |
| --------------------------- | ----------------------------------------------------------- |
| Repetir el mismo`validar` | **409** · ya está registrado en esa sesión (RN-21) |
| Clave incorrecta            | **422** · con el texto de la regla                   |
| Clave ya usada              | **422** · RN-20                                      |

## Paso 11 · Responder la encuesta

`POST /api/acceso/registro/{idRegistro}/encuesta`:

```json
{
  "respuestas": [
    { "pregunta": 1, "numero": 5 },
    { "pregunta": 2, "numero": 4 },
    { "pregunta": 3, "numero": 1 },
    { "pregunta": 4, "texto": "Todo bien" }
  ]
}
```

Los `id_pregunta` los sacas de `GET /api/pregunta`.

> Cada respuesta llena **una sola** de las tres columnas de valor, según el tipo de la pregunta: `numero` para escalas y sí/no, `texto` para texto libre, `opcion` para opción múltiple. Mandar dos, o ninguna, lo rechaza la base.

---

# CAMINO A otra vez · Migrar al ASIS

Vuelve a hacer falta el JWT.

## Paso 12 · Ver qué falta

Sección **VPendienteMigracion** → `GET /api/v_pendiente_migracion` → **Execute**.

Por cada sesión: cuántos registros hay, cuántos **sin ID del ASIS**, cuántos **sin programa**, cuántos externos y cuántos **migrables**.

Es la cola de trabajo del gestor: quien esté en `sin_id_asis` o `sin_programa` **no puede migrarse** y hay que resolverlo a mano.

## Paso 13 · Previsualizar el archivo

`GET /api/migracion/sesion/{idSesion}/previsualizar` → **Execute**.

**Debe salir:** `{ "filas": 164, "columnas": 3, "datos": [...] }`

**Tres columnas. Ni una más.** Reunión, ID del ASIS y código de programa. Los externos y los que no tienen programa ya vienen filtrados.

## Paso 14 · Generar el lote

`POST /api/migracion/sesion/{idSesion}/generar` → **Execute**.

Crea el lote **y su detalle**: guarda, fila por fila, **lo que se envió** — no lo que hoy diga la tabla. Si el programa de alguien cambia después, los dos valores divergen, y esa es la única forma de auditar un rechazo del ASIS seis meses más tarde.

## Paso 15 · Descargar el archivo plano

`GET /api/migracion/sesion/{idSesion}/archivo` → **Execute** → **Download file**.

**Debe salir** un `.xlsx` que cumple lo que exige el manual de migración:

| Requisito                        | Por qué                                                                                                                             |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Sin fila de encabezado** | El manual:*«únicamente haya información en las tres columnas correspondientes»*                                                |
| **Exactamente 3 columnas** | Reunión · ID · programa                                                                                                           |
| **El ID como TEXTO**       | Como número, Excel destrozaría`1000513C` y los ceros a la izquierda                                                              |
| **Sin espacios sobrantes** | Por eso el código de programa es`varchar(5)` y no `char(5)`: `MCCP` tiene 4 caracteres y `char` lo rellenaría a `MCCP␣` |

**Este archivo es el criterio de aceptación de todo el proyecto.** Hay que compararlo carácter a carácter con uno cargado a mano en el ASIS.

## Paso 16 · Cerrar el ciclo

Se sube el archivo en *Carga Info Cátedra* del ASIS, se ejecuta en `PSUNX01`, y se anota el resultado:

`PUT /api/migracion/lote/{idLote}/resultado`

```json
{
  "estado": "CORRECTO",
  "instancia_proceso_asis": "9284471",
  "observaciones": ""
}
```

Los estados válidos son los cinco del manual: `EN_COLA`, `EN_CURSO`, `ERROR`, `CORRECTO`, `INCORRECTO` — más `GENERADO` para el archivo que existe pero no se ha subido.

---

## Los tres controles que deben dar cero

Estos no devuelven datos: devuelven **la confianza de que las reglas siguen vivas**.

| Endpoint                                                    | Debe dar                                                                                        |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `GET /api/v_control_ventana`                              | `"encontrados": 0` — ningún registro fuera de su ventana                                    |
| `GET /api/v_embudo_registro`                              | Enlaces → claves enviadas → usadas → registros → encuestas. Dónde se cae la gente          |
| `GET /api/clave_acceso/por/es_correo_institucional/false` | Claves enviadas a correo**no** institucional. El asunto que quedó abierto en la reunión |

---

## Si algo falla

| Síntoma                          | Causa                                                                | Solución                                                                                 |
| --------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **401** en todo             | No pulsaste**Authorize**, o el token expiró                   | Repite los pasos 1 y 2. El token dura 8 horas                                             |
| **401** con el token puesto | Escribiste`Bearer` a mano y quedó duplicado                       | En*Authorize*, pega **solo** el token                                             |
| **403**                     | Tu usuario no tiene el rol                                           | `/api/migracion/*` exige `ADMIN`; `/api/enlace/*` exige `ADMIN` o `COORDINADOR` |
| **404** en `/`            | Ya no pasa: hay endpoint raíz                                       | —                                                                                        |
| **409**                     | Ya existe. Es una restricción de unicidad funcionando               | Mira el campo`regla` de la respuesta                                                    |
| **422**                     | **Una regla de negocio.** El mensaje trae su número `RN-xx` | Léelo: está redactado en español a propósito                                          |
| **405** en un `DELETE`    | En este sistema**no se elimina** (RN-32)                       | Usa`PUT` sobre la columna de baja lógica                                               |
| `ventana_abierta: false`        | La sesión no está en su franja                                     | Emite el enlace de una sesión que ocurra ahora                                           |
| `MSB3026 · archivo bloqueado`  | Hay otra instancia corriendo                                         | `Get-Process ApiCatedrasUsbmed \| Stop-Process -Force`                                   |
| La API no arranca                 | Falta`Jwt:Key` o la cadena de conexión                            | Es*fail-fast* a propósito. Ver el README                                               |

---

## Hacerlo todo de un tirón

Los dos scripts recorren esto mismo sin intervención:

```bash
bash pruebas/certificacion.sh     # contrato, tipos, seguridad, barrido de humo
bash pruebas/flujo-completo.sh    # los 16 pasos, de punta a punta
```

`flujo-completo.sh` **reubica la sesión de prueba a la hora actual** antes de empezar, porque si no su ventana estaría cerrada y `solicitar-clave` la rechazaría — que es justo lo que debe hacer.

---

**Volver al** [README](../README.md) · **El modelo de datos:** [`../../SOLUCION/`](../../SOLUCION/)
