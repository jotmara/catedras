# Plan Técnico — Versión 2: Procedimientos Almacenados, Disparadores y Frontend Maestro-Detalle

> **Versión 2 / Segunda Entrega** · Arquitectura de software, patrones de diseño y estrategia de implementación para cumplir con la rúbrica oficial (Prof. Carlos Castro).
> Relaciones del dominio: [2_spec.md](2_spec.md) · Decisiones técnicas: [4_research.md](4_research.md) · Esquema relacional: [5_data_model.md](5_data_model.md) · Contratos: [6_contracts.md](6_contracts.md).

---

## 1. Stack Tecnológico y Arquitectura de Capas

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                               CAPA DE PRESENTACIÓN                            │
│   Frontend Web Institucional Flask (Python / HTML5 Semántico / CSS3 USBMed)   │
│   - Patrón Maestro-Detalle en pantalla única (Cátedra ──▶ Sesiones)          │
│   - Selectores desplegables dinámicos (Dropdowns FK sin digitación manual)    │
│   - Puerto: 5173 (http://localhost:5173)                                      │
└──────────────────────────────────────┬────────────────────────────────────────┘
                                       │ HTTP / REST / JSON
┌──────────────────────────────────────▼────────────────────────────────────────┐
│                              CAPA DE SERVICIOS REST                           │
│   Backend Web API (.NET 10 / .NET 8 C#)                                       │
│   - Controladores REST fuertemente tipados con DataAnnotations                │
│   - Filtro de excepciones globales para códigos PostgreSQL (23503, 23505)    │
│   - Puerto: 7045 (http://localhost:7045/swagger)                              │
└──────────────────────────────────────┬────────────────────────────────────────┘
                                       │ ADO.NET / Npgsql / Dapper
┌──────────────────────────────────────▼────────────────────────────────────────┐
│                              CAPA DE BASE DE DATOS                            │
│   PostgreSQL 16 (Esquema: catedras)                                           │
│   - Procedimientos Almacenados transaccionales (CALL sp_...)                  │
│   - Disparadores automáticos de negocio (trg_sesion_consecutivo, etc.)        │
│   - Integridad referencial con restricciones FOREIGN KEY y EXCLUDE            │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Patrón de Procedimientos Almacenados (`CALL sp_...`)

Siguiendo el estándar fijado para la versión 2, las operaciones transaccionales y de mutación de entidades se delegan al motor de base de datos a través de procedimientos con parámetros de retorno `INOUT`:

### 2.1 Estructura Estándar de Procedimiento en PostgreSQL
```sql
CREATE OR REPLACE PROCEDURE catedras.sp_crear_sesion(
    p_fk_catedra        bigint,
    p_titulo            varchar(200),
    p_inicio            timestamptz,
    p_fin               timestamptz,
    p_fk_modalidad      varchar(15),
    p_fk_sede           varchar(15),
    p_fk_periodo        char(6),
    p_lugar             varchar(200),
    p_cupo              integer,
    INOUT p_id_sesion   bigint DEFAULT NULL,
    INOUT p_num_reunion smallint DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO catedras.sesion (
        fk_catedra, titulo, inicio, fin, fk_modalidad, fk_sede, fk_periodo, lugar, cupo
    )
    VALUES (
        p_fk_catedra, p_titulo, p_inicio, p_fin, p_fk_modalidad, p_fk_sede, p_fk_periodo, p_lugar, p_cupo
    )
    RETURNING id_sesion, numero_reunion INTO p_id_sesion, p_num_reunion;
END;
$$;
```

### 2.2 Consumo desde Dapper / C#
```csharp
var parametros = new DynamicParameters();
parametros.Add("p_fk_catedra", peticion.FkCatedra, DbType.Int64);
parametros.Add("p_titulo", peticion.Titulo, DbType.String);
parametros.Add("p_inicio", peticion.Inicio, DbType.DateTimeOffset);
parametros.Add("p_fin", peticion.Fin, DbType.DateTimeOffset);
parametros.Add("p_fk_modalidad", peticion.FkModalidad, DbType.String);
parametros.Add("p_fk_sede", peticion.FkSede, DbType.String);
parametros.Add("p_fk_periodo", peticion.FkPeriodo, DbType.String);
parametros.Add("p_lugar", peticion.Lugar, DbType.String);
parametros.Add("p_cupo", peticion.Cupo, DbType.Int32);
parametros.Add("p_id_sesion", dbType: DbType.Int64, direction: ParameterDirection.InputOutput);
parametros.Add("p_num_reunion", dbType: DbType.Int16, direction: ParameterDirection.InputOutput);

await conexion.ExecuteAsync(
    "CALL catedras.sp_crear_sesion(@p_fk_catedra, @p_titulo, @p_inicio, @p_fin, @p_fk_modalidad, @p_fk_sede, @p_fk_periodo, @p_lugar, @p_cupo, @p_id_sesion, @p_num_reunion);",
    parametros
);

long idGenerado = parametros.Get<long>("p_id_sesion");
short numeroAsignado = parametros.Get<short>("p_num_reunion");
```

---

## 3. Demostración del Disparador en Vivo (`trg_sesion_consecutivo`)

El disparador de consecutivo de reunión es el caso demostrativo central para la evaluación oral:

1. **Definición en Base de Datos:**
   ```sql
   CREATE OR REPLACE FUNCTION catedras.fn_trg_sesion_consecutivo()
   RETURNS trigger LANGUAGE plpgsql AS $$
   BEGIN
       IF NEW.numero_reunion IS NULL OR NEW.numero_reunion = 0 THEN
           -- Serialización para evitar condiciones de carrera entre dos altas concurrentes
           PERFORM 1 FROM catedras.catedra WHERE id_catedra = NEW.fk_catedra FOR UPDATE;

           SELECT coalesce(max(s.numero_reunion), 0) + 1
             INTO NEW.numero_reunion
             FROM catedras.sesion s
            WHERE s.fk_catedra = NEW.fk_catedra;
       END IF;
       RETURN NEW;
   END;
   $$;

   CREATE TRIGGER trg_sesion_consecutivo
       BEFORE INSERT ON catedras.sesion
       FOR EACH ROW EXECUTE FUNCTION catedras.fn_trg_sesion_consecutivo();
   ```
2. **Comportamiento en UI / API:**
   - La API no envía `numero_reunion` (o envía `null`).
   - El formulario de creación de sesión no exige ni calcula el campo.
   - Tras el `INSERT`, el valor devuelto y renderizado en pantalla es el consecutivo exacto (ej. 1 si es la primera, 2 si es la segunda).

---

## 4. Diseño del Frontend Maestro-Detalle en Pantalla Única

Para cumplir con el criterio de evaluación de UI:
- **Ruta:** `/catedras` o `/admin/maestro_detalle` en Flask (`app.py`).
- **Comportamiento:**
  1. En el lado izquierdo/superior se lista la tabla de **Cátedras (Maestro)**.
  2. Al hacer clic en una cátedra, sin recargar toda la página (o mediante parámetro `?catedra_id=X`), se despliega en el panel derecho/inferior la tabla de **Sesiones (Detalle)** de dicha cátedra.
  3. El modal/formulario de creación de sesión ya tiene precargado y bloqueado el ID de la cátedra seleccionada.
  4. Los campos de relaciones foráneas (`fk_modalidad`, `fk_sede`, `fk_periodo`) se presentan obligatoriamente en etiquetas `<select>` con las opciones reales extraídas de la base de datos (`PRESENCIAL`, `VIRTUAL`, `SAN_BENITO`, `BELLO`, etc.).
