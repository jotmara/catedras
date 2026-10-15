# Cátedras Abiertas — base de datos

Diseño de la base de datos para el registro y control de asistencia a cátedras abiertas de la **Universidad de San Buenaventura, Medellín**.

Reemplaza el proceso manual actual: formulario anónimo en Microsoft Forms → cruce a mano contra el maestro del ASIS → armado de un archivo plano de tres columnas → carga en *Carga Info Cátedra*.

**Repositorio privado.** Contiene material de trabajo interno y datos operativos de la universidad.

---

## Estado

| Fase | Entregable | Estado |
|---|---|---|
| 0 | Levantamiento y perfilado de fuentes | ✅ Hecha |
| 1 | Diseño conceptual — [`SOLUCION/MER/`](SOLUCION/MER/) | ✅ 11 documentos, 6 diagramas de Chen y el Excel de entidades |
| 2 | Diseño lógico — [`SOLUCION/MR/`](SOLUCION/MR/) | ✅ 6 documentos, todo en BCNF |
| 3 | Diseño físico — [`SOLUCION/fisico_postgres/`](SOLUCION/fisico_postgres/) | ✅ 19 scripts, **ejecutados sin errores** |
| 4 | Validación del archivo plano contra uno real del ASIS | ⬜ Falta un archivo de ejemplo |
| 5 | Entrega y prompt para IA | ✅ [`PROMPT-PARA-IA.md`](SOLUCION/PROMPT-PARA-IA.md) |

**La base se construye entera con un comando** y da código de salida 0:

```bash
cd SOLUCION/fisico_postgres
python preparar-datos.py
psql -U postgres -f ejecutar-todo.sql
```

| tablas | vistas | claves foráneas | checks | disparadores | filas reales |
|---:|---:|---:|---:|---:|---:|
| 37 | 6 | 52 | 47 | 7 | ~41.000 |

Los **cuatro controles de integridad dan cero** y las **tres pruebas de permisos deniegan** como deben.

**Motor:** PostgreSQL 14+ · UTF-8 · esquema `catedras`
**Modelo:** 33 entidades → 37 tablas · MVP de 25

---

## Por dónde empezar

👉 **[`SOLUCION/README.md`](SOLUCION/README.md)** — la solución construida: qué hay en cada nivel, los seis hallazgos y cómo revisarla.

👉 **[`PLAN-BD-CATEDRAS-ABIERTAS.md`](PLAN-BD-CATEDRAS-ABIERTAS.md)** — el plan que originó todo, en trece secciones: fuentes, método, reglas del negocio con su cita de origen, perfilado de datos, el modelo, las 38 reglas, los 20 informes y las decisiones defendibles.

👉 **[`SOLUCION/MODELO-INTEGRADO.md`](SOLUCION/MODELO-INTEGRADO.md)** — el modelo en una página.

👉 **[`PLAN-API-CATEDRAS-USBMED.md`](PLAN-API-CATEDRAS-USBMED.md)** — el plan de la API REST que expondrá esta base, replicando la arquitectura de `ApiEvalFormativaUsbmed`.

---

## Las fuentes

| Archivo | Qué es | Autoridad |
|---|---|---|
| `trascripción del video.txt` | Reunión con el profesor Carlos Arturo Castro. Método, reglas y acuerdos | **Normativa** |
| `USBME_LCONTROL_CATEDRAS_*.xlsx` | Listado de reuniones del ASIS: evento, reunión, descripción, tipo | Estructural |
| `PRIMERA VERSIÓN Ideas software.docx` | Acta de la reunión. Escrita como *prompt* para la IA | Requisitos |
| `Cätedras abiertas DIagrama Entidad -relación.xlsx` | Punto de partida del MER, construido en vivo durante la reunión | Modelo |
| `Documentación de migración… .pdf` | El proceso manual que se reemplaza y los cinco estados del ASIS | Apoyo |
| `USBME_EMPLID_CATED_V1_*.xlsx` | Maestro de personas del ASIS. **Se reemplazará** por un informe de seis columnas | Apoyo |
| `Pedagogía Electoral(1-164).xlsx` | Volcado del formulario actual. Evidencia de por qué el sistema hace falta | Apoyo |

---

## Convenciones

Fijadas por el director técnico durante la reunión y de obligado cumplimiento:

- Nombres de entidades y atributos **sin tildes y sin espacios**.
- Diagramas conceptuales en **notación de Chen**, no en pata de gallina.
- Las relaciones se nombran con **verbos**; se evita *haber* y *tener*.
- **Cardinalidad y opcionalidad** se documentan por separado, con min-max.
- Toda entidad y todo atributo llevan **descripción escrita**, y se ajusta a medida que cambia el entendimiento.

En el diseño físico se usa `snake_case` en minúscula, que cumple la misma regla y es la convención de PostgreSQL. La equivalencia entre las etiquetas del MER y los nombres físicos queda en el diccionario de datos.

---

## Protección de datos

Este repositorio maneja datos personales de estudiantes, docentes y público externo: números de documento, códigos institucionales, nombres y correos.

**Ley 1581 de 2012 (Habeas Data, Colombia).** El modelo incluye la tabla `consentimiento_datos` desde el diseño, no como parche posterior. Ver §11, riesgo 7 del plan.

- El repositorio es **privado** y debe seguir siéndolo.
- No publicar extractos con datos reales en documentación, capturas ni ejemplos.
- Los datos de prueba del diseño físico son **sintéticos**.
