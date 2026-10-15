# -*- coding: utf-8 -*-
"""
Generador de ApiCatedrasUsbmed.

Lee el esquema REAL de la base `catedras` desde los catalogos de PostgreSQL y emite,
por cada tabla: modelo, interfaz de repositorio, repositorio, interfaz de servicio,
servicio y controlador. Por cada vista: los mismos, en version de solo lectura.

    python generador/generar.py

ESTE GENERADOR ES LA FUENTE DE VERDAD. Igual que en ApiEvalFormativaUsbmed: si algo
esta mal en el codigo emitido, se corrige AQUI y se regenera. No se parchea a mano.

Las excepciones estan declaradas en OMITIR: son las tablas cuyo repositorio se escribe
a mano por llevar un tipo que no cabe en el molde.
"""
import os
import re
import subprocess
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PSQL = r'C:\Program Files\PostgreSQL\18\bin\psql.exe'
CONN = ['-U', 'postgres', '-h', 'localhost', '-d', 'catedras']
NS = 'ApiCatedrasUsbmed'

# Tablas cuyo repositorio se escribe a mano. Se generan igual el modelo y las interfaces
# NO: se omiten por completo y se escriben los seis archivos a mano.
OMITIR = {
    # enlace_registro.ventana es tstzrange: no tiene equivalente en C# y el repositorio
    # tiene que construir el rango con tstzrange(). Ver §4.2 del plan.
    'enlace_registro',
    # v_control_ventana proyecta la misma columna tstzrange.
    'v_control_ventana',
}

# El orden de las secciones de Swagger NO lo toca el generador: vive en
# Helpers/OrdenSwagger.cs, escrito a mano, porque es una decision de usabilidad
# y no depende del esquema.

# ---------------------------------------------------------------------------
# Mapa de tipos PostgreSQL -> C#
# ---------------------------------------------------------------------------
TIPOS = {
    'bigint': 'long', 'integer': 'int', 'smallint': 'short',
    'boolean': 'bool', 'date': 'DateOnly',
    'timestamp with time zone': 'DateTimeOffset',
    'timestamp without time zone': 'DateTime',
    'uuid': 'Guid', 'bytea': 'byte[]',
    'numeric': 'decimal', 'real': 'float', 'double precision': 'double',
}
# Todos estos se exponen como string
TIPOS_TEXTO = ('character varying', 'character', 'citext', 'text', 'name', 'jsonb', 'json', 'inet')
VALOR = {'long', 'int', 'short', 'bool', 'DateOnly', 'DateTimeOffset', 'DateTime', 'Guid',
         'decimal', 'float', 'double'}

# Columnas que NUNCA deben salir en el JSON de respuesta (§7.2 del plan)
OCULTAR = {('clave_acceso', 'clave_hash'), ('usuario', 'clave_hash')}


def sql(consulta):
    r = subprocess.run([PSQL] + CONN + ['-tAF', '|', '-c', consulta],
                       capture_output=True, text=True, encoding='utf-8',
                       env={**os.environ, 'PGPASSWORD': 'postgres'})
    if r.returncode:
        sys.exit('psql fallo:\n' + r.stderr)
    return [l for l in r.stdout.splitlines() if l.strip()]


def pascal(s):
    return ''.join(p.capitalize() for p in re.split(r'[_\s]+', s) if p)


def prop_nombre(tabla, col):
    """
    Nombre de la propiedad C#.

    C# PROHIBE que un miembro se llame igual que su tipo envolvente (CS0542), y eso pasa
    cuando una tabla tiene una columna con su mismo nombre: catedras.usuario.usuario.
    Se antepone 'Nombre' y el atributo [Column] conserva el nombre REAL, que es lo que
    Dapper usa gracias al CustomPropertyTypeMap de Program.cs.
    """
    p = pascal(col)
    return 'Nombre' + p if p == pascal(tabla) else p


def tipo_cs(pg, nullable):
    base = None
    for k, v in TIPOS.items():
        if pg == k or pg.startswith(k + '('):
            base = v
            break
    if base is None:
        base = 'string' if any(pg.startswith(t) for t in TIPOS_TEXTO) else None
    if base is None:
        return None                       # tipo desconocido -> tabla a mano
    if base == 'byte[]':
        return 'byte[]'
    if nullable:
        return base + '?'
    return base


def longitud(pg):
    m = re.search(r'\((\d+)\)', pg)
    return int(m.group(1)) if m and pg.startswith(('character', 'citext')) else None


# ---------------------------------------------------------------------------
# Lectura del esquema
# ---------------------------------------------------------------------------
def leer(relkind):
    filas = sql("""
        SELECT c.relname, a.attname, format_type(a.atttypid, a.atttypmod),
               (NOT a.attnotnull)::text,
               CASE WHEN a.attgenerated <> '' THEN 'GEN'
                    WHEN a.attidentity  <> '' THEN 'IDENT' ELSE '-' END,
               a.attnum
          FROM pg_class c
          JOIN pg_namespace n ON n.oid = c.relnamespace
          JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum > 0 AND NOT a.attisdropped
         WHERE n.nspname = 'catedras' AND c.relkind = '%s'
         ORDER BY c.relname, a.attnum""" % relkind)
    rel = {}
    for f in filas:
        t, col, pg, nul, gen, _ = f.split('|')
        rel.setdefault(t, []).append({
            'col': col, 'pg': pg, 'nul': nul == 'true', 'gen': gen,
            'prop': prop_nombre(t, col), 'cs': tipo_cs(pg, nul == 'true'), 'len': longitud(pg),
        })
    return rel


def leer_pks():
    filas = sql("""
        SELECT c.relname, a.attname, array_position(i.indkey::int2[], a.attnum)
          FROM pg_index i
          JOIN pg_class c ON c.oid = i.indrelid
          JOIN pg_namespace n ON n.oid = c.relnamespace
          JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = ANY(i.indkey)
         WHERE i.indisprimary AND n.nspname = 'catedras'
         ORDER BY c.relname, 3""")
    pks = {}
    for f in filas:
        t, col, _ = f.split('|')
        pks.setdefault(t, []).append(col)
    return pks


# ---------------------------------------------------------------------------
# Plantillas
# ---------------------------------------------------------------------------
def gen_modelo(tabla, cols, pks, vista=False):
    cuerpo = []
    for c in cols:
        a = [f'    [Column("{c["col"]}")]']
        if c['col'] in pks and not vista:
            a.insert(0, '    [Key]')
        if c['gen'] == 'GEN':
            a.append('    [DatabaseGenerated(DatabaseGeneratedOption.Computed)]')
        if (tabla, c['col']) in OCULTAR:
            a.append('    [JsonIgnore]   // nunca sale en el JSON de respuesta')
        if not c['nul'] and c['cs'] == 'string':
            a.append('    [Required]')
        if c['len'] and c['cs'] and c['cs'].startswith('string'):
            a.append(f'    [MaxLength({c["len"]})]')
        ini = ' = string.Empty;' if c['cs'] == 'string' else (' = Array.Empty<byte>();' if c['cs'] == 'byte[]' else '')
        a.append(f'    public {c["cs"]} {c["prop"]} {{ get; set; }}{ini}')
        cuerpo.append('\n'.join(a))
    return f'''using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace {NS}.Modelos;

[Table("{tabla}")]
public class {pascal(tabla)}
{{
{chr(10).join(cuerpo)}
}}
'''


def firma_pk(pks, cols):
    """Parametros C# de la clave: (long id) o (long fkAsistente, string fkTipoVinculacion, ...)"""
    out = []
    for k in pks:
        c = next(x for x in cols if x['col'] == k)
        base = c['cs'].rstrip('?')
        nombre = c['prop'][0].lower() + c['prop'][1:]
        out.append((base, nombre, k, c['prop']))
    return out


def gen_irepo(tabla, cols, pks, vista):
    C, P = pascal(tabla), pascal(tabla)
    if vista:
        return f'''using {NS}.Modelos;

namespace {NS}.Repositorios.Abstracciones;

/// <summary>Vista de solo lectura.</summary>
public interface I{C}Repositorio
{{
    Task<List<{P}>> ObtenerTodosAsync(int? limite = null);
    Task<List<{P}>> ObtenerPorColumnaAsync(string columna, string valor);
}}
'''
    fp = firma_pk(pks, cols)
    args = ', '.join(f'{t} {n}' for t, n, _, _ in fp)
    return f'''using {NS}.Modelos;

namespace {NS}.Repositorios.Abstracciones;

public interface I{C}Repositorio
{{
    Task<List<{P}>> ObtenerTodosAsync(int? limite = null);
    Task<{P}?> ObtenerPorIdAsync({args});
    Task<bool> CrearAsync({P} entidad);
    Task<bool> ActualizarAsync({P} entidad);
    Task<bool> EliminarAsync({args});
    Task<List<{P}>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<{P}> entidades);
    Task<int> ActualizarLoteAsync(List<{P}> entidades);
}}
'''


def gen_repo(tabla, cols, pks, vista):
    C, P = pascal(tabla), pascal(tabla)
    lista = ', '.join(f'"{c["col"]}"' for c in cols)
    if vista:
        return f'''using Dapper;
using {NS}.Helpers;
using {NS}.Modelos;
using {NS}.Repositorios.Abstracciones;

namespace {NS}.Repositorios;

public class {C}Repositorio : I{C}Repositorio
{{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.{tabla}";

    public {C}Repositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) {{ {lista} }};

    private static void ValidarColumna(string columna)
    {{
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{{columna}}'.");
    }}

    public async Task<List<{P}>> ObtenerTodosAsync(int? limite = null)
    {{
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {{Tabla}} LIMIT {{Paginacion.Resolver(limite)}}";
        return (await con.QueryAsync<{P}>(sql)).AsList();
    }}

    public async Task<List<{P}>> ObtenerPorColumnaAsync(string columna, string valor)
    {{
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {{Tabla}} WHERE CAST({{columna}} AS TEXT) = @Valor";
        return (await con.QueryAsync<{P}>(sql, new {{ Valor = valor }})).AsList();
    }}
}}
'''
    fp = firma_pk(pks, cols)
    args = ', '.join(f'{t} {n}' for t, n, _, _ in fp)
    where = ' AND '.join(f'{k} = @{p}' for _, _, k, p in fp)
    anon = ', '.join(f'{p} = {n}' for _, n, _, p in fp)
    pk_ident = any(c['gen'] == 'IDENT' for c in cols if c['col'] in pks)
    pk_cols = ', '.join(f'"{k}"' for k in pks)
    return f'''using Dapper;
using {NS}.Helpers;
using {NS}.Modelos;
using {NS}.Repositorios.Abstracciones;

namespace {NS}.Repositorios;

public class {C}Repositorio : I{C}Repositorio
{{
    private readonly IFabricaConexion _cx;
    private const string Tabla = "catedras.{tabla}";
    private static readonly string[] Pk = {{ {pk_cols} }};

    public {C}Repositorio(IFabricaConexion cx) => _cx = cx;

    private static readonly HashSet<string> _columnas =
        new(StringComparer.OrdinalIgnoreCase) {{ {lista} }};

    private static void ValidarColumna(string columna)
    {{
        if (!_columnas.Contains(columna))
            throw new ArgumentException($"Columna no permitida: '{{columna}}'.");
    }}

    public async Task<List<{P}>> ObtenerTodosAsync(int? limite = null)
    {{
        using var con = _cx.Crear();
        // Tope SIEMPRE, tambien cuando el cliente no pide limite: ver Helpers/Paginacion.cs
        var sql = $"SELECT * FROM {{Tabla}} LIMIT {{Paginacion.Resolver(limite)}}";
        return (await con.QueryAsync<{P}>(sql)).AsList();
    }}

    public async Task<{P}?> ObtenerPorIdAsync({args})
    {{
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {{Tabla}} WHERE {where}";
        return await con.QueryFirstOrDefaultAsync<{P}>(sql, new {{ {anon} }});
    }}

    public async Task<bool> CrearAsync({P} entidad)
    {{
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarInsertSQL<{P}>(Tabla, pkAutogenerada: {str(pk_ident).lower()});
        return await con.ExecuteAsync(sql, entidad) > 0;
    }}

    public async Task<bool> ActualizarAsync({P} entidad)
    {{
        using var con = _cx.Crear();
        var sql = ConexionHelper.GenerarUpdateSQL<{P}>(Tabla, Pk);
        return await con.ExecuteAsync(sql, entidad) > 0;
    }}

    public async Task<bool> EliminarAsync({args})
    {{
        using var con = _cx.Crear();
        var sql = $"DELETE FROM {{Tabla}} WHERE {where}";
        return await con.ExecuteAsync(sql, new {{ {anon} }}) > 0;
    }}

    public async Task<List<{P}>> ObtenerPorColumnaAsync(string columna, string valor)
    {{
        ValidarColumna(columna);
        using var con = _cx.Crear();
        var sql = $"SELECT * FROM {{Tabla}} WHERE CAST({{columna}} AS TEXT) = @Valor";
        return (await con.QueryAsync<{P}>(sql, new {{ Valor = valor }})).AsList();
    }}

    public async Task<int> CrearMasivoAsync(List<{P}> entidades)
    {{
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarInsertSQL<{P}>(Tabla, pkAutogenerada: {str(pk_ident).lower()});
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }}

    public async Task<int> ActualizarLoteAsync(List<{P}> entidades)
    {{
        if (entidades is null || entidades.Count == 0) return 0;
        using var con = _cx.Crear();
        con.Open();
        using var tx = con.BeginTransaction();
        var sql = ConexionHelper.GenerarUpdateSQL<{P}>(Tabla, Pk);
        var n = 0;
        foreach (var e in entidades) n += await con.ExecuteAsync(sql, e, tx);
        tx.Commit();
        return n;
    }}
}}
'''


def gen_iserv(tabla, cols, pks, vista):
    C, P = pascal(tabla), pascal(tabla)
    if vista:
        return f'''using {NS}.Modelos;

namespace {NS}.Servicios.Abstracciones;

public interface I{C}Servicio
{{
    Task<List<{P}>> ObtenerTodosAsync(int? limite = null);
    Task<List<{P}>> ObtenerPorColumnaAsync(string columna, string valor);
}}
'''
    fp = firma_pk(pks, cols)
    args = ', '.join(f'{t} {n}' for t, n, _, _ in fp)
    return f'''using {NS}.Modelos;

namespace {NS}.Servicios.Abstracciones;

public interface I{C}Servicio
{{
    Task<List<{P}>> ObtenerTodosAsync(int? limite = null);
    Task<{P}?> ObtenerPorIdAsync({args});
    Task<bool> CrearAsync({P} entidad);
    Task<bool> ActualizarAsync({P} entidad);
    Task<bool> EliminarAsync({args});
    Task<List<{P}>> ObtenerPorColumnaAsync(string columna, string valor);
    Task<int> CrearMasivoAsync(List<{P}> entidades);
    Task<int> ActualizarLoteAsync(List<{P}> entidades);
}}
'''


def gen_serv(tabla, cols, pks, vista):
    C, P = pascal(tabla), pascal(tabla)
    if vista:
        return f'''using {NS}.Modelos;
using {NS}.Repositorios.Abstracciones;
using {NS}.Servicios.Abstracciones;

namespace {NS}.Servicios;

public class {C}Servicio : I{C}Servicio
{{
    private readonly I{C}Repositorio _repo;
    public {C}Servicio(I{C}Repositorio repo) => _repo = repo;

    public Task<List<{P}>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<List<{P}>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
}}
'''
    fp = firma_pk(pks, cols)
    args = ', '.join(f'{t} {n}' for t, n, _, _ in fp)
    pase = ', '.join(n for _, n, _, _ in fp)
    return f'''using {NS}.Modelos;
using {NS}.Repositorios.Abstracciones;
using {NS}.Servicios.Abstracciones;

namespace {NS}.Servicios;

public class {C}Servicio : I{C}Servicio
{{
    private readonly I{C}Repositorio _repo;
    public {C}Servicio(I{C}Repositorio repo) => _repo = repo;

    public Task<List<{P}>> ObtenerTodosAsync(int? limite = null) => _repo.ObtenerTodosAsync(limite);
    public Task<{P}?> ObtenerPorIdAsync({args}) => _repo.ObtenerPorIdAsync({pase});
    public Task<bool> CrearAsync({P} entidad) => _repo.CrearAsync(entidad);
    public Task<bool> ActualizarAsync({P} entidad) => _repo.ActualizarAsync(entidad);
    public Task<bool> EliminarAsync({args}) => _repo.EliminarAsync({pase});
    public Task<List<{P}>> ObtenerPorColumnaAsync(string columna, string valor) =>
        _repo.ObtenerPorColumnaAsync(columna, valor);
    public Task<int> CrearMasivoAsync(List<{P}> entidades) => _repo.CrearMasivoAsync(entidades);
    public Task<int> ActualizarLoteAsync(List<{P}> entidades) => _repo.ActualizarLoteAsync(entidades);
}}
'''


# El rethrow de PostgresException NO es decorativo: IExceptionFilter solo actua sobre
# excepciones NO capturadas. Sin esta linea el try/catch se traga el 23505 y el filtro
# nunca llega a traducirlo a 409, ni el 23514 de los disparadores a 422.
CATCH = ('        catch (ArgumentException ex) {{ return BadRequest(new {{ mensaje = ex.Message }}); }}\n'
         '        catch (Npgsql.PostgresException) {{ throw; }}\n'
         '        catch (Exception ex) {{ _log.LogError(ex, "Error en {t}"); '
         'return StatusCode(500, new {{ mensaje = "Error interno del servidor.", '
         'traceId = HttpContext.TraceIdentifier }}); }}')


def gen_ctrl(tabla, cols, pks, vista):
    C, P = pascal(tabla), pascal(tabla)
    cat = CATCH.format(t=tabla)
    if vista:
        return f'''using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using {NS}.Helpers;
using {NS}.Servicios.Abstracciones;

namespace {NS}.Controllers;

/// <summary>Vista de solo lectura: no expone POST, PUT ni DELETE.</summary>
[Route("api/{tabla}")]
[ApiController]
[Authorize]
public class {C}Controller : ControllerBase
{{
    private readonly I{C}Servicio _svc;
    private readonly ILogger<{C}Controller> _log;

    public {C}Controller(I{C}Servicio svc, ILogger<{C}Controller> log) {{ _svc = svc; _log = log; }}

    /// <summary>
    /// Devuelve como maximo {{Paginacion.Maximo}} filas; sin `limite`, {{Paginacion.PorDefecto}}.
    /// El tope aplicado viaja en la cabecera X-Limite-Aplicado.
    /// </summary>
    [HttpGet]
    public async Task<IActionResult> ObtenerTodos([FromQuery] int? limite = null)
    {{
        try
        {{
            var filas = await _svc.ObtenerTodosAsync(limite);
            Response.Headers["X-Limite-Aplicado"] = Paginacion.Resolver(limite).ToString();
            Response.Headers["X-Filas-Devueltas"] = filas.Count.ToString();
            return Ok(filas);
        }}
{cat}
    }}

    [HttpGet("por/{{columna}}/{{valor}}")]
    public async Task<IActionResult> ObtenerPorColumna(string columna, string valor)
    {{
        try {{ return Ok(await _svc.ObtenerPorColumnaAsync(columna, valor)); }}
{cat}
    }}
}}
'''
    fp = firma_pk(pks, cols)
    ruta = '/'.join('{' + n + '}' for _, n, _, _ in fp)
    args = ', '.join(f'{t} {n}' for t, n, _, _ in fp)
    pase = ', '.join(n for _, n, _, _ in fp)
    return f'''using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using {NS}.Helpers;
using {NS}.Modelos;
using {NS}.Servicios.Abstracciones;

namespace {NS}.Controllers;

[Route("api/{tabla}")]
[ApiController]
[Authorize]
public class {C}Controller : ControllerBase
{{
    private readonly I{C}Servicio _svc;
    private readonly ILogger<{C}Controller> _log;

    public {C}Controller(I{C}Servicio svc, ILogger<{C}Controller> log) {{ _svc = svc; _log = log; }}

    /// <summary>
    /// Devuelve como maximo {{Paginacion.Maximo}} filas; sin `limite`, {{Paginacion.PorDefecto}}.
    /// El tope aplicado viaja en la cabecera X-Limite-Aplicado.
    /// </summary>
    [HttpGet]
    public async Task<IActionResult> ObtenerTodos([FromQuery] int? limite = null)
    {{
        try
        {{
            var filas = await _svc.ObtenerTodosAsync(limite);
            Response.Headers["X-Limite-Aplicado"] = Paginacion.Resolver(limite).ToString();
            Response.Headers["X-Filas-Devueltas"] = filas.Count.ToString();
            return Ok(filas);
        }}
{cat}
    }}

    [HttpGet("{ruta}")]
    public async Task<IActionResult> ObtenerPorId({args})
    {{
        try
        {{
            var r = await _svc.ObtenerPorIdAsync({pase});
            return r is null ? NotFound(new {{ mensaje = "Registro no encontrado" }}) : Ok(r);
        }}
{cat}
    }}

    [HttpPost]
    public async Task<IActionResult> Crear([FromBody] {P} entidad)
    {{
        try
        {{
            var ok = await _svc.CrearAsync(entidad);
            return ok ? Ok(new {{ mensaje = "Registro creado" }})
                      : BadRequest(new {{ mensaje = "No se pudo crear" }});
        }}
{cat}
    }}

    [HttpPut("{ruta}")]
    public async Task<IActionResult> Actualizar({args}, [FromBody] {P} entidad)
    {{
        try
        {{
            var ok = await _svc.ActualizarAsync(entidad);
            return ok ? Ok(new {{ mensaje = "Registro actualizado" }})
                      : NotFound(new {{ mensaje = "Registro no encontrado" }});
        }}
{cat}
    }}

    /// <summary>
    /// RN-32: en esta base DELETE esta revocado para todos los roles. El endpoint existe
    /// para que el contrato sea honesto y explique el motivo, en vez de anunciar en Swagger
    /// una operacion que siempre fallaria con error de permisos.
    /// </summary>
    [HttpDelete("{ruta}")]
    public IActionResult Eliminar({args}) =>
        StatusCode(405, new {{ mensaje = "RN-32: en este sistema no se elimina. Use PUT sobre la columna de baja logica." }});

    [HttpGet("por/{{columna}}/{{valor}}")]
    public async Task<IActionResult> ObtenerPorColumna(string columna, string valor)
    {{
        try {{ return Ok(await _svc.ObtenerPorColumnaAsync(columna, valor)); }}
{cat}
    }}

    [HttpPost("masivo")]
    public async Task<IActionResult> CrearMasivo([FromBody] List<{P}> entidades)
    {{
        try {{ var n = await _svc.CrearMasivoAsync(entidades); return Ok(new {{ mensaje = $"{{n}} registro(s) creado(s)", filas = n }}); }}
{cat}
    }}

    [HttpPut("lote")]
    public async Task<IActionResult> ActualizarLote([FromBody] List<{P}> entidades)
    {{
        try {{ var n = await _svc.ActualizarLoteAsync(entidades); return Ok(new {{ mensaje = $"{{n}} registro(s) actualizado(s)", filas = n }}); }}
{cat}
    }}
}}
'''


# ---------------------------------------------------------------------------
def escribir(ruta, texto):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(texto)


def main():
    tablas = leer('r')
    vistas = leer('v')
    pks = leer_pks()

    generadas, saltadas, di = [], [], []

    for nombre, cols in sorted(list(tablas.items()) + list(vistas.items())):
        vista = nombre in vistas
        if nombre in OMITIR:
            saltadas.append((nombre, 'a mano: tipo sin equivalente en C#'))
            di.append(pascal(nombre))
            continue
        desconocidos = [c['col'] for c in cols if c['cs'] is None]
        if desconocidos:
            saltadas.append((nombre, 'tipo desconocido: ' + ', '.join(desconocidos)))
            di.append(pascal(nombre))     # la implementacion va a mano, pero el DI hace falta
            continue
        clave = pks.get(nombre, [])
        if not vista and not clave:
            saltadas.append((nombre, 'sin clave primaria'))
            continue

        C = pascal(nombre)
        escribir(f'{RAIZ}/Modelos/{C}.cs', gen_modelo(nombre, cols, clave, vista))
        escribir(f'{RAIZ}/Repositorios/Abstracciones/I{C}Repositorio.cs', gen_irepo(nombre, cols, clave, vista))
        escribir(f'{RAIZ}/Repositorios/{C}Repositorio.cs', gen_repo(nombre, cols, clave, vista))
        escribir(f'{RAIZ}/Servicios/Abstracciones/I{C}Servicio.cs', gen_iserv(nombre, cols, clave, vista))
        escribir(f'{RAIZ}/Servicios/{C}Servicio.cs', gen_serv(nombre, cols, clave, vista))
        escribir(f'{RAIZ}/Controllers/{C}Controller.cs', gen_ctrl(nombre, cols, clave, vista))
        generadas.append(nombre)
        di.append(C)

    # Fragmento de inyeccion de dependencias, para pegar en Program.cs
    lineas = [f'builder.Services.AddScoped<I{c}Repositorio, {c}Repositorio>();\n'
              f'builder.Services.AddScoped<I{c}Servicio,    {c}Servicio>();' for c in sorted(di)]
    escribir(f'{RAIZ}/generador/di.generado.txt', '\n'.join(lineas) + '\n')

    sys.stdout.write('Generadas   %d relaciones (%d archivos)\n' % (len(generadas), len(generadas) * 6))
    sys.stdout.write('  tablas    %d\n' % len([g for g in generadas if g in tablas]))
    sys.stdout.write('  vistas    %d\n' % len([g for g in generadas if g in vistas]))
    for n, m in saltadas:
        sys.stdout.write('  SALTADA   %-24s %s\n' % (n, m))
    sys.stdout.write('DI: %d pares -> generador/di.generado.txt\n' % len(di))


if __name__ == '__main__':
    main()
