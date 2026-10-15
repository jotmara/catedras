# Diseño físico — PostgreSQL

**Fase 3** · Motor: **PostgreSQL 14 o superior** · UTF-8 · esquema `catedras`
**Estado: ejecutado de punta a punta sin errores.** Ver §5.

---

## 1 · Cómo ejecutarlo

```bash
cd SOLUCION/fisico_postgres

# 1 · generar los CSV desde los Excel reales del ASIS
python preparar-datos.py

# 2 · construirlo todo
psql -U postgres -f ejecutar-todo.sql
```

En Windows con PowerShell:

```powershell
$env:PGPASSWORD = "..."
python preparar-datos.py
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -f ejecutar-todo.sql
```

**Requisitos:** las extensiones `pgcrypto`, `btree_gist`, `citext`, `unaccent` y `pg_trgm`. Vienen en `postgresql-contrib`, que la mayoría de los instaladores incluye.

---

## 2 · Los diecinueve archivos

| Script | Contenido |
|---|---|
| `preparar-datos.py` | Lee los dos Excel del ASIS y escribe `datos/*.csv`. **Los CSV no se versionan** |
| `00-crear-bd.sql` | Base, codificación, 5 extensiones, esquema y `fn_normalizar` |
| `01-ddl-asistentes.sql` | Bloque A — 6 tablas |
| `02-ddl-academico.sql` | Bloque B — 4 tablas |
| `03-ddl-catedras.sql` | Bloque C — 7 tablas, con la columna generada `nombre_asis` |
| `04-ddl-registro.sql` | Bloque D — 3 tablas, con `tstzrange` y el `EXCLUDE` |
| `05-ddl-encuesta.sql` | Bloque E — 6 tablas, con el `CHECK` de un solo valor |
| `06-ddl-integracion.sql` | Bloque F — 6 tablas |
| `07-ddl-seguridad.sql` | Bloque G — 5 tablas |
| `08-constraints-fk.sql` | Las **52 claves foráneas**, con nombre y política declarada una por una |
| `09-indices.sql` | 30 índices, **cada uno justificado por un informe o una regla** |
| `10-triggers.sql` | 6 funciones y 7 disparadores, con su número de RN |
| `11-funciones-procedimientos.sql` | 4 funciones y 6 procedimientos |
| `12-datos-catalogos.sql` | Catálogos, todos con fuente verificable |
| `13-carga-asis.sql` | **Carga REAL**: 5.496 cátedras, 5.711 sesiones, 14.808 personas |
| `14-datos-prueba.sql` | El flujo completo: enlace → clave → registro → encuesta → migración |
| `15-vistas.sql` | 6 vistas, tres de ellas de **control** |
| `16-consultas-informes.sql` | Los 20 informes |
| `17-usuarios-permisos.sql` | 4 roles, 2 usuarios y **tres pruebas que deben fallar** |
| `18-backup-restore.md` | Respaldo, retención y evidencia de restauración |
| `ejecutar-todo.sql` | Todo en orden, con verificaciones finales |

**Por qué el orden de `ejecutar-todo` no es 00, 01, 02…:** los **índices van al final**, con los datos ya cargados, porque un índice sobre una tabla vacía no dice nada y su plan de ejecución es inútil. Y los **datos de prueba van después de las vistas**, porque algunas comprobaciones las usan.

---

## 3 · Lo específico de PostgreSQL que este proyecto sí aprovecha

Ninguna extensión está por costumbre. Cada una resuelve una regla concreta.

| Necesidad | Mecanismo | Qué costaría en otro motor |
|---|---|---|
| **RN-36** · dos enlaces de una sesión no se solapan | `EXCLUDE USING gist` sobre `tstzrange` | Disparador con bloqueo explícito |
| **RN-05, 14, 29** y el vigente · unicidad condicional | **Índice único parcial** (4 casos) | En MySQL **no existen**: columna generada + `UNIQUE` |
| **RN-11** · el nombre corto del ASIS | Columna **generada** `STORED` | Disparador |
| **RN-06** · acceso por tres identificadores | `citext` + tres índices | Índices sobre expresiones `lower()` |
| **H17** · texto libre → código de programa | `pg_trgm` + `unaccent` + índice `GIN` | Tabla de equivalencias exactas, o trabajo manual |
| **RN-18** · hash de la clave | `pgcrypto` · `digest()` con sal | Se resuelve en la aplicación |
| **RN-35** · bitácora | `jsonb` con el antes y el después | Una tabla espejo por tabla — **37 más** |
| **I3, I20** · jerarquías | `WITH RECURSIVE` | `CONNECT BY` en Oracle |
| **I2, I5** · agregados condicionales | `FILTER (WHERE …)` | `SUM(CASE WHEN … END)` |

> **La conclusión que hay que poder defender:** en un motor sin `EXCLUDE` ni índices parciales, **cinco reglas dejan de ser garantía del motor y pasan a ser código que alguien tiene que mantener**. El modelo no cambia de forma; cambia **quién responde**.

---

## 4 · Qué mirar primero al revisar

| Archivo | Qué demuestra |
|---|---|
| `01`, `chk_asistente_idasis` | El dominio **corregido contra el dato**: alfanumérico de 15, no 10 dígitos |
| `02`, `codigo varchar(5)` | Por qué `char(5)` habría metido un espacio en el archivo del ASIS |
| `04`, `ex_enlace_sin_solape` | La única regla que un motor sin `EXCLUDE` no puede declarar |
| `04`, los dos `_snapshot` | La decisión más importante del modelo |
| `05`, `chk_respuesta_item_un_valor` | La regla condicional, en su parte declarativa |
| `10`, `fn_trg_registro_validar` | Cuatro reglas en un disparador, y por qué van juntas |
| `11`, `fn_resolver_asistente` | Las tres puertas de acceso de `57:27` |
| `11`, `fn_exportar_asis` | **Tres columnas exactas.** Ni una más |
| `17`, el bloque de pruebas | Los permisos, aprobados **demostrando un fallo** |

---

## 5 · Evidencia de la última ejecución

```
$ psql -U postgres -f ejecutar-todo.sql
código de salida: 0        errores: 0
```

**Objetos creados**

| tablas | vistas | claves foráneas | checks | disparadores |
|---:|---:|---:|---:|---:|
| 37 | 6 | 52 | 47 | 7 |

**Volúmenes cargados, contra lo medido en los Excel**

| objeto | filas | esperado |
|---|---:|---:|
| catedras | 5.497 | 5.497 |
| sesiones | 5.714 | 5.714 |
| programas | 105 | 105 |
| asistentes | 14.811 | 14.811 |
| documentos | 15.517 | 15.517 |
| registros | 166 | 166 |

*Los totales incluyen la cátedra y los tres asistentes de prueba que añade el script 14.*

**Los cuatro controles — todos en cero**

| control | resultado |
|---|---:|
| Registros fuera de ventana (RN-15) | **0** |
| Pares (cátedra, reunión) duplicados (RN-10) | **0** |
| Encuestas completas sin ningún ítem (R29) | **0** |
| Externos colados en el archivo del ASIS (RN-08) | **0** |

**Las tres pruebas de permisos — las tres deniegan**

```
CORRECTO: permiso denegado sobre asistente
CORRECTO: DELETE denegado
CORRECTO: UPDATE sobre bitacora denegado
```

**Comprobación del archivo plano (I7)**

| filas | id con espacios | programa con espacios |
|---:|---:|---:|
| 164 | **0** | **0** |

---

## 6 · Los dos hallazgos que solo aparecieron al ejecutar

Ninguno se veía en el papel. Los dos están documentados en el código, con su evidencia.

### 6.1 · `MCCP` tiene cuatro caracteres

De los 105 códigos de programa reales, 103 tienen la forma `M`+4 dígitos, **`MCDER` tiene cinco caracteres y `MCCP` tiene cuatro**. Con `char(5)`, `MCCP` se rellena a `MCCP␣` y ese espacio viaja al archivo plano — justo lo que el manual prohíbe. → `varchar(5)`.

### 6.2 · El número de reunión **no** es un consecutivo por cátedra

Se creía que empezaba en 1 y crecía de uno en uno dentro de cada evento. El dato dice otra cosa:

- De los **5.481 eventos con una sola reunión, solo 588 tienen el número 1**. Los otros 4.893 traen valores arbitrarios, hasta **4348**.
- Los eventos con muchas reuniones sí empiezan en 1, pero **con huecos**: `000035428` tiene 59 reuniones numeradas de 1 a 60.

**El ASIS lleva un contador propio que este sistema no conoce.** Esto **resuelve con dato** la decisión que el plan había dejado abierta en §8.3: la autoridad del consecutivo es el ASIS. El disparador `fn_trg_sesion_consecutivo` **propone** un número para las cátedras nuevas; `sesion.numero_reunion_asis` manda cuando existe.

> La restricción `UNIQUE (fk_catedra, numero_reunion)` **sí se sostiene**: se verificó sobre las 5.711 filas reales y da cero duplicados. Lo que falla no es el modelo, es la regla de derivación.

---

## 7 · Nota sobre los datos

`preparar-datos.py` **sintetiza nombres y correos** a partir del ID, porque el informe actual del ASIS solo entrega tres columnas. No es un atajo: es la evidencia del **riesgo número 1** del plan. Cuando Carlos amplíe el informe a seis columnas —nombre, correo institucional y correo personal, acordado en `1:50:43`—, basta con cambiar las dos funciones marcadas `SINTETICO` y volver a cargar.

Los **164 nombres y cédulas reales** del formulario de Pedagogía Electoral **no se reproducen** en los datos de prueba. El modelo se demuestra igual de bien sin ellos.

---

**Nivel anterior:** [`../MR/`](../MR/) · **El modelo en una página:** [`../MODELO-INTEGRADO.md`](../MODELO-INTEGRADO.md)
