# Registro de Prompts de Elicitación y Desarrollo — Versión 2

> **Versión 2 / Segunda Entrega** · Bitácora completa de los prompts, directivas de contexto y refinamientos utilizados para construir el Spec Kit v2, el modelo relacional y la solución técnica.
> Requerimiento del curso: "Los prompts con los que trabajó inicialmente esos spec kit" (Ponderación: 20%).

---

## 1. Contexto Metodológico

Para la construcción de la Versión 2, se siguió la metodología del curso impartida por el profesor Carlos Castro (*«el documento de requisitos va a ser para la IA… entre menos espacios tenga, más cortico es el prompt»*). 

La premisa central fue **fijar el modelo relacional cerrado y verificado antes de generar código**, impidiendo que la IA alucine tablas, nombres de columna o relaciones arbitrarias.

---

## 2. Bloque de Prompts Iniciales: Elicitación y Análisis de Dominio

### Prompt 1.1 — Delimitación de Relaciones Maestro-Detalle y Cadenas Jerárquicas
```text
Actúa como Arquitecto de Software y Especialista en Bases de Datos Relacionales PostgreSQL.
Tenemos el sistema de Cátedras Abiertas de la Universidad de San Buenaventura Medellín (USBMed).
Basándote en el modelo físico de 37 tablas del esquema 'catedras', clasifica rigurosamente:
1. Las 10 relaciones que son formalmente Maestro-Detalle (1:N), donde la fila hija depende conceptualmente del padre.
2. Identifica las 2 cadenas jerárquicas estrictas de 3 niveles (Padre -> Hijo -> Nieto).
3. Explica detalladamente por qué 'ponencia' NO es una relación Maestro-Detalle pura sino una tabla puente (N:M con atributos), y por qué la relación entre 'sesion' y 'encuesta' es una referencia opcional y no de propiedad fuerte.
Aplica el test metodológico de las tres preguntas: ¿Tiene PK propia? ¿Puede existir sin padre? ¿Qué ocurre con la integridad al borrar al padre?
```

### Prompt 1.2 — Elicitación de Reglas Inviolables del Sistema Académico ASIS
```text
Analiza los archivos de migración institucional y las grabaciones del sistema PeopleSoft ASIS de la USBMed:
1. Define las restricciones de tipo de dato para 'id_asis' (alfanumérico de hasta 15 caracteres, nunca entero).
2. Justifica el tipo de dato y formato de 'id_evento_asis' (char de 9 dígitos con ceros a la izquierda obligatorios, ej: 000035392).
3. Modela la regla del archivo plano de migración que exige exactamente 3 columnas (reunion, id_asis, programa) sin encabezados ni espacios.
4. Explica cómo resolver la búsqueda de programas académicos con errores ortográficos o variantes digitadas por los asistentes mediante la extensión pg_trgm y similitud trigramática en la tabla 'alias_programa'.
```

---

## 3. Bloque de Prompts de Arquitectura y Base de Datos (Disparadores y Procedimientos)

### Prompt 2.1 — Disparador de Consecutivo Automático de Sesión (`trg_sesion_consecutivo`)
```text
Genera la función y el disparador en PL/pgSQL para la tabla 'catedras.sesion':
- Nombre: fn_trg_sesion_consecutivo()
- Evento: BEFORE INSERT ON sesion FOR EACH ROW
- Comportamiento: Si el campo 'numero_reunion' es NULL o 0, debe calcular automáticamente el siguiente consecutivo para la cátedra específica: coalesce(max(numero_reunion), 0) + 1.
- Concurrencia: Aplica bloqueo pesimista 'PERFORM 1 FROM catedra WHERE id_catedra = NEW.fk_catedra FOR UPDATE' para serializar inserciones simultáneas y evitar colisiones de unicidad en (fk_catedra, numero_reunion).
- Explica cómo este disparador permite demostrar en vivo que la interfaz de usuario o la API no necesitan calcular ni enviar el consecutivo.
```

### Prompt 2.2 — Columna Generada Inmutable para ASIS (`nombre_asis`)
```text
En PostgreSQL 16, redacta el DDL para la tabla 'catedras.catedra' incorporando una columna generada 'nombre_asis' de tipo varchar(30):
- Expresión: GENERATED ALWAYS AS (left(nombre, 30)) STORED.
- Justifica por qué se almacena como columna generada en lugar de procesarlo en la capa de aplicación de C# o Python.
- Detalla el impacto en los DTOs de inserción de ASP.NET Core: ¿por qué no debe exponerse en el request body?
```

### Prompt 2.3 — Procedimiento Almacenado de Registro y OTP Antisuplantación
```text
Escribe el Stored Procedure 'sp_solicitar_clave' y 'sp_validar_clave_y_registrar' en PostgreSQL:
- 'sp_solicitar_clave': Recibe identificador (código, cédula o correo), busca al asistente con 'fn_resolver_asistente', genera OTP de 6 dígitos, guarda el hash seguro con sal 'digest(clave || correo, 'sha256')' en 'clave_acceso' con vigencia de 10 minutos y retorna la clave en claro mediante parámetro INOUT únicamente para el despacho del correo.
- Garantiza que la clave nunca se guarde en texto plano en la base de datos.
```

---

## 4. Bloque de Prompts para Frontend y Experiencia de Usuario (UI Maestro-Detalle)

### Prompt 3.1 — Pantalla Única Maestro-Detalle en Flask
```text
Diseña e implementa la vista de Cátedras y Sesiones en Flask ('app.py'):
- Patrón: Maestro-Detalle en una sola pantalla interactiva.
- Panel Maestro: Tabla de cátedras activas con código ASIS de 9 dígitos, nombre institucional, dependencia y botón para seleccionar.
- Panel Detalle: Al seleccionar una cátedra, despliega inmediatamente en el mismo plano visual sus sesiones o reuniones programadas con su horario, modalidad y estado.
- Usabilidad para Claves Foráneas: En los formularios modales de creación, todos los campos foráneos (tipo_evento, dependencia, modalidad, sede, periodo) DEBEN ser menús desplegables (<select>) poblados desde los catálogos de la base de datos. Está estrictamente prohibido que el usuario tenga que escribir manualmente un ID foráneo.
- Estilo: Aplica la paleta corporativa oficial de la Universidad de San Buenaventura Medellín (Naranja #FF6600, tipografía Montserrat).
```

---

## 5. Bloque de Prompts para Interpretabilidad y Defensa Oral

### Prompt 4.1 — Las Cuatro Preguntas de Interpretabilidad por Archivo
```text
Prepara una guía de sustentación oral para el equipo de desarrollo basada en la rúbrica de interpretabilidad del código (4/20 puntos).
Para cada uno de los siguientes archivos nucleares:
1. ApiCatedrasUsbmed/Controllers/CatedraController.cs
2. ApiCatedrasUsbmed/Modelos/Sesion.cs
3. app.py (Rutas de cátedras y sesiones en Flask)
4. SOLUCION/fisico_postgres/10-triggers.sql (Disparador de consecutivo)

Responde con máxima claridad técnica:
a) ¿Qué hace exactamente este archivo en el sistema?
b) ¿Por qué se tomó esta decisión de diseño y no otra?
c) ¿Qué modos de fallo existen y cómo reacciona el sistema ante un error?
d) ¿Qué cambiarías o mejorarías en una siguiente versión?
```
