# Respaldo de la base `catedras`

**Generado el 13 de agosto de 2026**, desde la base de desarrollo local.

---

## ⚠️ Estos archivos contienen DATOS PERSONALES REALES

> `catedras_completo_*.dump` y `catedras_completo_*.sql.gz` incluyen las **14.811 personas** del maestro del ASIS, con sus **números de documento y correos**.
>
> **Ley 1581 de 2012.** El repositorio tiene que seguir siendo privado. No los suba a ningún sitio público, no los envíe por correo sin cifrar, y no los deje en una carpeta compartida.
>
> Si necesita el modelo pero no los datos —para montar un entorno de pruebas, para una demostración, para compartir con alguien—, use **`catedras_esquema_*.sql`**, que trae la estructura completa y **ninguna fila**.

---

## Los cuatro archivos

| Archivo | Qué trae | Tamaño | ¿Datos personales? |
|---|---|---:|:---:|
| **`catedras_esquema_*.sql`** | Tablas, vistas, rutinas, restricciones, disparadores e índices. **Sin una sola fila** | 120 KB | **No** |
| `catedras_roles_*.sql` | Los cuatro roles de base de datos y sus permisos | 2,7 KB | No |
| **`catedras_completo_*.dump`** | Todo, en formato `custom` comprimido. **Permite restaurar tablas sueltas** | 795 KB | **Sí** |
| `catedras_completo_*.sql.gz` | Todo, en SQL plano comprimido. Legible con un editor | 625 KB | **Sí** |

> **Por qué dos formatos del completo.** El `.dump` en formato *custom* es el que se usa para restaurar: permite paralelizar con `-j` y recuperar **una sola tabla**. El `.sql.gz` es para poder **leerlo** —revisar una definición, buscar un valor— sin restaurar nada.

---

## Restaurar

### Todo, desde cero

```bash
dropdb -U postgres catedras
createdb -U postgres catedras
pg_restore -U postgres -d catedras -j 4 catedras_completo_2026-08-13.dump
```

Después, las funciones envoltorio de la API:

```bash
psql -U postgres -d catedras -f ../19-funciones-api.sql
```

### Solo la estructura, sin datos

Para un entorno de pruebas o una demostración:

```bash
createdb -U postgres catedras_demo
psql -U postgres -d catedras_demo -f catedras_esquema_2026-08-13.sql
psql -U postgres -d catedras_demo -f ../../../SOLUCION/fisico_postgres/12-datos-catalogos.sql
```

Quedan las 37 tablas con sus reglas y los catálogos poblados, **sin ninguna persona**.

### Desde pgAdmin, sin tocar la consola

**1 · Crear la base vacía**

Clic derecho en **Databases** → *Create* → *Database…* → nombre `catedras` → **Save**.

**2 · Restaurar**

Clic derecho sobre la base `catedras` → **Restore…**

| Campo | Valor |
|---|---|
| *Format* | **Custom or tar** |
| *Filename* | `catedras_completo_2026-08-13.dump` |
| *Number of jobs* | `4` — acelera la restauración |
| Pestaña **Data Options** → *Clean before restore* | Actívelo **solo** si la base ya tenía contenido |

→ **Restore**

**3 · Las funciones envoltorio de la API**

Abra el *Query Tool* sobre `catedras`, pegue el contenido de [`../19-funciones-api.sql`](../19-funciones-api.sql) y ejecute (**F5**).

> #### Si sale «pg_restore not found» o «utility not found»
>
> pgAdmin necesita saber dónde están los ejecutables de PostgreSQL. Vaya a
> **File → Preferences → Paths → Binary paths**, y en *PostgreSQL Binary Path*
> ponga la ruta de su versión:
>
> ```
> C:\Program Files\PostgreSQL\18\bin
> ```

> #### Cuál de los cuatro archivos usar en pgAdmin
>
> | Archivo | En pgAdmin |
> |---|---|
> | `catedras_completo_*.dump` | ✅ **Restore…** — es el que sirve |
> | `catedras_esquema_*.sql` | *Query Tool* (es SQL plano, no `Restore…`) |
> | `catedras_roles_*.sql` | *Query Tool*, conectado a `postgres` |
> | `catedras_completo_*.sql.gz` | Hay que descomprimirlo primero; después, *Query Tool* |
>
> **`Restore…` solo entiende los formatos `custom` y `tar`.** Si le da un `.sql`
> plano, falla. Los `.sql` se ejecutan desde el *Query Tool*.

### Una sola tabla

```bash
pg_restore -U postgres -d catedras -t registro_asistencia --data-only \
           catedras_completo_2026-08-13.dump
```

### Los roles

`pg_dump` **no incluye los roles**: son objetos del clúster, no de la base. Si restaura en un servidor nuevo, aplíquelos antes:

```bash
psql -U postgres -f catedras_roles_2026-08-13.sql
```

---

## Evidencia de que este respaldo sirve

> **Un respaldo que no se ha restaurado nunca no es un respaldo: es un archivo.**

Este se restauró en una base aparte el 13 de agosto de 2026, y se comprobó que **no solo volvieron los datos, sino las reglas**:

| Comprobación | Resultado |
|---|---:|
| Tablas | **37** |
| Vistas | **6** |
| Rutinas (funciones y procedimientos) | **22** |
| **Disparadores activos** | **7** |
| Asistentes | 14.811 |
| Cátedras | 5.502 |
| Registros de asistencia | 168 |
| Personas con más de un documento | **707** |
| Control RN-15 · registros fuera de ventana | **0** |
| Pares (cátedra, reunión) duplicados | **0** |

Los **disparadores** son la parte que más importa comprobar: si volvieran los datos pero no ellos, la base parecería correcta y dejaría de hacer cumplir la mitad de las reglas — la ventana horaria, las instantáneas, el cupo. Por eso la verificación no se queda en contar filas.

```bash
# el guion que lo comprueba
createdb -U postgres catedras_prueba
pg_restore -U postgres -d catedras_prueba -j 4 catedras_completo_2026-08-13.dump
psql -U postgres -d catedras_prueba -c "
SELECT (SELECT count(*) FROM information_schema.tables
         WHERE table_schema='catedras' AND table_type='BASE TABLE') AS tablas,
       (SELECT count(*) FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid
          JOIN pg_namespace n ON n.oid=c.relnamespace
         WHERE n.nspname='catedras' AND NOT t.tgisinternal) AS disparadores,
       (SELECT count(*) FROM catedras.v_control_ventana) AS debe_ser_cero"
dropdb -U postgres catedras_prueba
```

---

## Volver a generarlos

```bash
cd ApiCatedrasUsbmed/sql/backup
FECHA=$(date +%Y-%m-%d)

pg_dump -U postgres -d catedras --schema-only --no-owner --no-privileges \
        -f "catedras_esquema_${FECHA}.sql"

pg_dump -U postgres -d catedras -F c -Z 9 --no-owner \
        -f "catedras_completo_${FECHA}.dump"

pg_dump -U postgres -d catedras --no-owner --no-privileges \
    | gzip -9 > "catedras_completo_${FECHA}.sql.gz"

pg_dumpall -U postgres --roles-only | grep -E "rol_|u_gestor|u_app" \
    > "catedras_roles_${FECHA}.sql"
```

---

## Esto NO es la estrategia de respaldo de producción

Estos archivos son una **foto de la base de desarrollo**, útiles para levantar el proyecto en otra máquina.

La estrategia real —tres capas, archivado de WAL, objetivo de recuperación de 5 minutos y prueba trimestral— está en **[`../../../SOLUCION/fisico_postgres/18-backup-restore.md`](../../../SOLUCION/fisico_postgres/18-backup-restore.md)**.

La diferencia importa: con un volcado diario, un fallo a las 4 de la tarde pierde todo lo registrado ese día. **Y los registros de asistencia son irrecuperables: nadie va a volver a escanear el QR.**
