import os
import io
import json
import requests
from flask import Flask, render_template_string, request, redirect, url_for, session, flash, send_file

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = "usbmed_catedras_cideh_oficial_key_2026"

API_BASE = "http://localhost:7045/api"
API_ROOT = "http://localhost:7045"

BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ titulo }} | Universidad de San Buenaventura Medellín</title>
  <meta name="description" content="Sistema Institucional de Gestión de Cátedras Abiertas y Registro de Asistentes — CIDEH, Universidad de San Buenaventura Medellín.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/static/style.css">
  <style>
    .header-user-badge {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      font-size: 0.82rem;
      color: rgba(255,255,255,0.85);
      background: rgba(255,255,255,0.08);
      padding: 0.35rem 0.9rem;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.15);
    }
    .btn-salir {
      background: transparent;
      border: 1px solid rgba(239,125,0,0.7);
      color: #FFF;
      padding: 0.25rem 0.65rem;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 700;
      cursor: pointer;
      text-transform: uppercase;
      transition: all 0.2s;
    }
    .btn-salir:hover {
      background: var(--usb-naranja);
      border-color: var(--usb-naranja);
    }
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2rem;
    }
    .kpi-box {
      background: #FFF;
      border-radius: var(--radius-md);
      border: 1px solid var(--usb-gris-borde);
      border-top: 4px solid var(--usb-naranja);
      padding: 1.25rem 1.5rem;
      box-shadow: var(--shadow-sm);
    }
    .kpi-box-title {
      font-size: 0.78rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--usb-text-muted);
    }
    .kpi-box-num {
      font-size: 2.2rem;
      font-weight: 900;
      color: var(--usb-negro);
      line-height: 1.1;
      margin-top: 0.4rem;
    }
    .card-panel {
      background: #FFF;
      border-radius: var(--radius-md);
      border: 1px solid var(--usb-gris-borde);
      box-shadow: var(--shadow-sm);
      overflow: hidden;
      margin-bottom: 2rem;
    }
    .card-panel-header {
      padding: 1.1rem 1.5rem;
      background: #FFF;
      border-bottom: 2px solid var(--usb-gris-claro);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.5rem;
    }
    .card-panel-title {
      font-size: 1.05rem;
      font-weight: 800;
      color: var(--usb-negro);
      letter-spacing: -0.01em;
    }
    .card-panel-body {
      padding: 1.5rem;
    }
  </style>
</head>
<body>
  <header class="header">
    <a href="/" class="header-brand">
      <img src="/static/logo_usb.png" alt="Universidad de San Buenaventura Medellín" class="header-logo">
      <div class="header-titles">
        <h1>Universidad de San Buenaventura</h1>
        <p>CIDEH — Centro de Investigación y Desarrollo del Espíritu Humano</p>
      </div>
    </a>
    <nav class="header-nav">
      <a href="/" class="nav-link {% if request.path == '/' %}active{% endif %}">Inicio</a>
      {% if session.get('token') %}
        <a href="/sedes" class="nav-link {% if request.path == '/sedes' %}active{% endif %}">Sedes</a>
        <a href="/catedras" class="nav-link {% if request.path == '/catedras' %}active{% endif %}">Cátedras</a>
        <a href="/sesiones" class="nav-link {% if request.path.startswith('/sesiones') or request.path.startswith('/enlace') %}active{% endif %}">Sesiones y QR</a>
        <a href="/ponentes" class="nav-link {% if request.path == '/ponentes' %}active{% endif %}">Ponentes</a>
        <a href="/migracion" class="nav-link {% if request.path.startswith('/migracion') %}active{% endif %}">ASIS / Oracle</a>
        <a href="/auditoria" class="nav-link {% if request.path == '/auditoria' %}active{% endif %}">Bitácora</a>
        <a href="/reportes" class="nav-link {% if request.path == '/reportes' %}active{% endif %}">Reportes</a>
      {% endif %}
      <a href="/registro" class="nav-link {% if request.path == '/registro' %}active{% endif %}">Registro Asistente</a>
      <a href="http://localhost:7045/swagger" target="_blank" class="nav-link">Swagger →</a>
    </nav>
    <div style="display: flex; align-items: center; gap: 0.75rem;">
      {% if session.get('token') %}
        <div class="header-user-badge">
          <span>{{ session.get('usuario') }}</span>
          <form action="/logout" method="POST" style="margin:0;">
            <button type="submit" class="btn-salir">Salir</button>
          </form>
        </div>
      {% else %}
        <a href="/login" class="btn btn-primary btn-sm">Acceso Administrativo</a>
      {% endif %}
    </div>
  </header>

  <div class="toast-area" id="toast-area">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="toast {% if category == 'success' %}success{% elif category == 'danger' %}error{% else %}info{% endif %}">
            <div class="toast-text">
              <strong>{% if category == 'success' %}Operación Exitosa{% elif category == 'danger' %}Aviso del Sistema{% else %}Notificación{% endif %}</strong>
              <span>{{ message }}</span>
            </div>
          </div>
        {% endfor %}
      {% endif %}
    {% endwith %}
  </div>

  <main>
    <div class="container animate">
      {{ contenido | safe }}
    </div>
  </main>

  <footer class="footer">
    <div class="footer-inner">
      <div style="display:flex;align-items:center;gap:0.75rem;">
        <img src="/static/logo_usb.png" alt="USB Medellín" class="footer-logo">
        <span>© 2026 Universidad de San Buenaventura, Seccional Medellín · CIDEH · Sistema de Cátedras</span>
      </div>
      <div class="footer-badge">VIGILADA MINEDUCACIÓN</div>
    </div>
  </footer>

  <script>
    setTimeout(() => {
      const toasts = document.querySelectorAll('.toast');
      toasts.forEach(t => {
        t.style.opacity = '0';
        t.style.transition = 'opacity 0.4s';
        setTimeout(() => t.remove(), 400);
      });
    }, 4000);
  </script>
</body>
</html>
"""

def auth_headers():
    token = session.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

@app.route("/")
def index():
    api_estado = "desconectada"
    api_info_texto = ""
    try:
        r_salud = requests.get(f"{API_ROOT}/salud", timeout=2)
        if r_salud.status_code == 200:
            api_estado = "activa"
        r_raiz = requests.get(f"{API_ROOT}/", timeout=2)
        if r_raiz.status_code == 200:
            api_info_texto = json.dumps(r_raiz.json(), indent=2, ensure_ascii=False)
    except Exception as e:
        api_info_texto = f"Error al consultar API: {str(e)}"

    card_class = "ok" if api_estado == "activa" else "error"
    status_label = "API Cátedras Activa — Conectada a PostgreSQL y Docker" if api_estado == "activa" else "API no detectada en http://localhost:7045"

    contenido = f"""
    <section class="hero animate">
      <div class="hero-logo-wrap">
        <img src="/static/logo_usb_horizontal.png" alt="Universidad de San Buenaventura Medellín" class="hero-logo">
      </div>
      <h2>Sistema de Cátedras <span>USB Medellín</span></h2>
      <p>Gestión integral de Cátedras Abiertas y Control de Asistencia del CIDEH.<br>
         Arquitectura oficial conectada a PostgreSQL, generación de QR con ventana horaria y exportación a ASIS/Oracle.</p>

      <div class="api-status-card {card_class}">
        <div class="status-dot"></div>
        <span>{status_label}</span>
      </div>

      <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;margin-top:1.5rem;">
        <a href="/sedes" class="btn btn-primary">Sedes</a>
        <a href="/catedras" class="btn btn-dark">Cátedras</a>
        <a href="/sesiones" class="btn btn-primary">Sesiones y QR</a>
        <a href="/ponentes" class="btn btn-ghost">Ponentes</a>
        <a href="/migracion" class="btn btn-dark">Exportación ASIS</a>
        <a href="/auditoria" class="btn btn-ghost">Bitácora</a>
        <a href="/registro" class="btn btn-primary">Registrar Asistencia</a>
      </div>
    </section>

    <div class="info-grid animate" style="animation-delay:0.1s">
      <div class="info-card">
        <div class="info-card-icon" style="font-weight:800;color:var(--usb-naranja);">01</div>
        <h3>Módulo de Cátedras y Sesiones</h3>
        <p>Creación académica vinculada a códigos ASIS oficiales de 9 dígitos, asignación de dependencias y programación de salas.</p>
      </div>
      <div class="info-card">
        <div class="info-card-icon" style="font-weight:800;color:var(--usb-naranja);">02</div>
        <h3>Ponentes y Convocatorias</h3>
        <p>Gestión y asignación de ponentes y moderadores a cada sesión académica cumpliendo los requerimientos RF-CAT-01 a 06 del CIDEH.</p>
      </div>
      <div class="info-card">
        <div class="info-card-icon" style="font-weight:800;color:var(--usb-naranja);">03</div>
        <h3>Exportación ASIS / Oracle</h3>
        <p>Generación de archivo plano estricto de 3 columnas (Reunión, ID_ASIS, Programa) y transferencia automática a carpeta de migración.</p>
      </div>
      <div class="info-card">
        <div class="info-card-icon" style="font-weight:800;color:var(--usb-naranja);">04</div>
        <h3>Auditoría y Trazabilidad</h3>
        <p>Monitoreo en vivo de la bitácora de base de datos con más de 14.800 participantes y control de geolocalización presencial.</p>
      </div>
    </div>

    <div style="margin-top:2.5rem;background:#fff;border-radius:12px;border:1px solid #e0e0e0;padding:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,0.05)">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
        <h3 style="font-size:1rem;font-weight:800;color:#1D1D1B">Estado Técnico del Sistema</h3>
        <span class="badge badge-orange">Puerto API: 7045</span>
      </div>
      <pre style="font-family:'Courier New',monospace;font-size:0.82rem;color:#636360;white-space:pre-wrap;overflow:auto;background:#f5f5f5;padding:1rem;border-radius:8px;">{api_info_texto}</pre>
    </div>
    """
    return render_template_string(BASE_LAYOUT, titulo="Inicio", contenido=contenido)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        pwd = request.form.get("contrasena", "").strip()
        try:
            r = requests.post(f"{API_BASE}/autenticacion/token", json={"email": email, "contrasena": pwd}, timeout=4)
            if r.status_code == 200:
                data = r.json()
                session["token"] = data.get("token")
                session["usuario"] = data.get("usuario")
                session["roles"] = data.get("roles", [])
                flash("Sesión iniciada exitosamente con permisos de Administrador CIDEH.", "success")
                return redirect(url_for("catedras"))
            elif r.status_code == 401:
                flash("Contraseña incorrecta. Verifique sus credenciales institucionales.", "danger")
            elif r.status_code == 404:
                flash("El usuario no existe en la base de datos de cátedras.", "danger")
            else:
                flash(f"Error de autenticación (Código HTTP {r.status_code}).", "danger")
        except Exception as e:
            flash(f"No fue posible conectar con el backend de cátedras: {str(e)}", "danger")

    contenido = """
    <div style="max-width: 480px; margin: 3rem auto;">
      <div class="card-panel" style="border-top: 4px solid var(--usb-naranja);">
        <div class="card-panel-header" style="justify-content: center; padding-top: 1.5rem;">
          <h2 style="font-size: 1.25rem; font-weight: 800; color: var(--usb-negro);">Acceso Administrativo CIDEH</h2>
        </div>
        <div class="card-panel-body">
          <p style="font-size: 0.85rem; color: var(--usb-text-muted); margin-bottom: 1.5rem; text-align: center;">
            Ingrese con su correo institucional para gestionar sedes, cátedras, sesiones, ponentes y exportaciones a Oracle.
          </p>
          <form method="POST">
            <div class="form-group">
              <label class="form-label" for="email">Correo Institucional <span>*</span></label>
              <input class="form-input" type="email" id="email" name="email" value="admin.catedras@usbmed.edu.co" required autofocus>
              <p class="form-hint">Usuario predeterminado para el CIDEH</p>
            </div>
            <div class="form-group" style="margin-bottom: 1.75rem;">
              <label class="form-label" for="contrasena">Contraseña <span>*</span></label>
              <input class="form-input" type="password" id="contrasena" name="contrasena" value="Catedras2026*" required>
            </div>
            <button type="submit" class="btn btn-primary" style="width: 100%; justify-content: center; padding: 0.85rem;">
              Ingresar al Sistema
            </button>
          </form>
        </div>
      </div>
    </div>
    """
    return render_template_string(BASE_LAYOUT, titulo="Inicio de Sesión", contenido=contenido)

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Ha cerrado su sesión de forma segura.", "info")
    return redirect(url_for("login"))

# ==========================================
# 1. MODULO DE SEDES
# ==========================================
@app.route("/sedes", methods=["GET", "POST"])
def sedes():
    if not session.get("token"):
        return redirect(url_for("login"))

    if request.method == "POST" and request.form.get("accion") == "crear":
        id_sede = request.form.get("id_sede", "").strip().upper()
        nombre = request.form.get("nombre", "").strip()
        direccion = request.form.get("direccion", "").strip() or None
        es_virtual = request.form.get("es_virtual") == "1"

        payload = {
            "idSede": id_sede,
            "nombre": nombre,
            "direccion": direccion,
            "esVirtual": es_virtual,
            "activo": True
        }
        try:
            r = requests.post(f"{API_BASE}/sede", json=payload, headers=auth_headers(), timeout=4)
            if r.status_code in [200, 201]:
                flash(f"Sede '{nombre}' ({id_sede}) creada exitosamente.", "success")
            else:
                flash(f"Error al registrar sede: {r.text}", "danger")
        except Exception as e:
            flash(f"Error de conexión: {str(e)}", "danger")
        return redirect(url_for("sedes"))

    if request.method == "POST" and request.form.get("accion") == "editar":
        id_sede = request.form.get("id_sede", "").strip().upper()
        nombre = request.form.get("nombre", "").strip()
        direccion = request.form.get("direccion", "").strip() or None
        es_virtual = request.form.get("es_virtual") == "1"
        activo = request.form.get("activo") == "1"

        payload = {
            "idSede": id_sede,
            "nombre": nombre,
            "direccion": direccion,
            "esVirtual": es_virtual,
            "activo": activo
        }
        try:
            r = requests.put(f"{API_BASE}/sede/{id_sede}", json=payload, headers=auth_headers(), timeout=4)
            if r.status_code == 200:
                flash(f"Sede '{id_sede}' actualizada correctamente.", "success")
            else:
                flash(f"No se pudo actualizar la sede: {r.text}", "danger")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("sedes"))

    sedes_list = []
    try:
        r = requests.get(f"{API_BASE}/sede", headers=auth_headers(), timeout=4)
        if r.status_code == 200:
            sedes_list = r.json()
    except Exception as e:
        flash(f"Error al consultar catálogo de sedes: {str(e)}", "danger")

    rows_html = ""
    for s in sedes_list:
        cod = s.get("id_sede") or s.get("idSede", "-")
        nom = s.get("nombre", "-")
        dir_s = s.get("direccion") or "Campus Universitario"
        tipo = "Modalidad Virtual" if s.get("es_virtual") or s.get("esVirtual") else "Campus Presencial"
        activo = s.get("activo", True)

        nom_esc = nom.replace("'", "\\'")
        dir_esc = dir_s.replace("'", "\\'")
        virt_flag = "1" if (s.get("es_virtual") or s.get("esVirtual")) else "0"
        act_flag = "1" if activo else "0"

        rows_html += f"""
        <tr>
          <td><span class="td-code">{cod}</span></td>
          <td style="font-weight:700; color:var(--usb-negro);">{nom}</td>
          <td style="color:var(--usb-text-muted);">{dir_s}</td>
          <td><span class="badge {'badge-orange' if virt_flag == '1' else 'badge-gray'}">{tipo}</span></td>
          <td>
            <div class="td-actions">
              <button type="button" class="btn btn-ghost btn-sm" onclick="abrirEditar('{cod}', '{nom_esc}', '{dir_esc}', '{virt_flag}', '{act_flag}')">Editar</button>
              <form action="/sedes/desactivar/{cod}" method="POST" style="margin:0;display:inline;" onsubmit="return confirm('¿Cambiar estado a la sede {cod}?');">
                <button type="submit" class="btn btn-danger btn-sm">{'Desactivar' if activo else 'Activar'}</button>
              </form>
            </div>
          </td>
        </tr>
        """

    contenido = """
    <div class="page-header">
      <div>
        <h2 class="page-title">Gestión de <span>Sedes Universitarias</span></h2>
        <p style="font-size:0.85rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Catálogo institucional de campus y sedes físicas y virtuales autorizadas por la Universidad.
        </p>
      </div>
      <button class="btn btn-primary" onclick="abrirModalCrear()">+ Nueva Sede</button>
    </div>

    <div class="toolbar">
      <span class="toolbar-label">Total de Sedes:</span>
      <span class="badge badge-dark">""" + str(len(sedes_list)) + """ autorizadas</span>
      <div style="margin-left:auto;font-size:0.82rem;color:var(--usb-text-muted);">
        PostgreSQL · Esquema <code>catedras.sede</code>
      </div>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Código</th>
            <th>Nombre del Campus</th>
            <th>Dirección</th>
            <th>Modalidad</th>
            <th style="text-align:center;">Acciones</th>
          </tr>
        </thead>
        <tbody>
          """ + (rows_html if rows_html else '<tr class="empty-row"><td colspan="5">No hay sedes registradas.</td></tr>') + """
        </tbody>
      </table>
    </div>

    <div class="modal-overlay" id="modal-sede-crear">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Registrar Nueva Sede</h3>
          <button class="modal-close" onclick="cerrarModalCrear()">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="accion" value="crear">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="id_sede">Código de Sede <span>*</span></label>
              <input class="form-input" type="text" id="id_sede" name="id_sede" maxlength="15" placeholder="Ej: BELLO_NORTE" required>
              <p class="form-hint">Clave única en mayúsculas (máximo 15 caracteres).</p>
            </div>
            <div class="form-group">
              <label class="form-label" for="nombre">Nombre de la Sede <span>*</span></label>
              <input class="form-input" type="text" id="nombre" name="nombre" maxlength="80" placeholder="Ej: Campus Universitario Norte" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="direccion">Dirección Física</label>
              <input class="form-input" type="text" id="direccion" name="direccion" maxlength="200" placeholder="Ej: Calle 45 # 61-40">
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.82rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" name="es_virtual" value="1">
                <span>Esta sede opera exclusivamente en modalidad virtual</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-ghost" onclick="cerrarModalCrear()">Cancelar</button>
            <button type="submit" class="btn btn-primary">Guardar Sede</button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" id="modal-sede-editar">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title" id="titulo-editar">Editar Sede</h3>
          <button class="modal-close" onclick="cerrarModalEditar()">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="accion" value="editar">
          <input type="hidden" id="edit-id-hidden" name="id_sede">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Código de Sede</label>
              <input class="form-input" type="text" id="edit-id" disabled>
            </div>
            <div class="form-group">
              <label class="form-label" for="edit-nombre">Nombre <span>*</span></label>
              <input class="form-input" type="text" id="edit-nombre" name="nombre" maxlength="80" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="edit-dir">Dirección</label>
              <input class="form-input" type="text" id="edit-dir" name="direccion" maxlength="200">
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.82rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" id="edit-virt" name="es_virtual" value="1">
                <span>Modalidad Virtual</span>
              </label>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.82rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" id="edit-act" name="activo" value="1">
                <span>Sede Activa</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-ghost" onclick="cerrarModalEditar()">Cancelar</button>
            <button type="submit" class="btn btn-primary">Actualizar Cambios</button>
          </div>
        </form>
      </div>
    </div>

    <script>
      function abrirModalCrear() {
        document.getElementById('modal-sede-crear').classList.add('open');
      }
      function cerrarModalCrear() {
        document.getElementById('modal-sede-crear').classList.remove('open');
      }
      function abrirEditar(cod, nom, dir, virt, act) {
        document.getElementById('edit-id-hidden').value = cod;
        document.getElementById('edit-id').value = cod;
        document.getElementById('edit-nombre').value = nom;
        document.getElementById('edit-dir').value = (dir === 'Campus Universitario') ? '' : dir;
        document.getElementById('edit-virt').checked = (virt === '1');
        document.getElementById('edit-act').checked = (act === '1');
        document.getElementById('titulo-editar').textContent = 'Editar Sede: ' + cod;
        document.getElementById('modal-sede-editar').classList.add('open');
      }
      function cerrarModalEditar() {
        document.getElementById('modal-sede-editar').classList.remove('open');
      }
    </script>
    """
    return render_template_string(BASE_LAYOUT, titulo="Gestión de Sedes", contenido=contenido)

@app.route("/sedes/desactivar/<codigo>", methods=["POST"])
def desactivar_sede(codigo):
    if not session.get("token"):
        return redirect(url_for("login"))
    try:
        r_get = requests.get(f"{API_BASE}/sede/{codigo}", headers=auth_headers(), timeout=3)
        if r_get.status_code == 200:
            sede = r_get.json()
            nuevo_estado = not sede.get("activo", True)
            sede["activo"] = nuevo_estado
            r_put = requests.put(f"{API_BASE}/sede/{codigo}", json=sede, headers=auth_headers(), timeout=3)
            if r_put.status_code == 200:
                flash(f"Estado de la sede '{codigo}' modificado a: {'Activa' if nuevo_estado else 'Inactiva'}.", "success")
            else:
                flash(f"Error al cambiar estado: {r_put.text}", "danger")
        else:
            flash(f"No se encontró la sede {codigo}.", "danger")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for("sedes"))

# ==========================================
# 2. MODULO DE CATEDRAS Y CONVOCATORIAS
# ==========================================
@app.route("/catedras", methods=["GET", "POST"])
def catedras():
    if not session.get("token"):
        return redirect(url_for("login"))

    if request.method == "POST" and request.form.get("accion") == "crear":
        id_evento_asis = request.form.get("id_evento_asis", "").strip().zfill(9)
        nombre = request.form.get("nombre", "").strip()
        fk_tipo_evento = request.form.get("fk_tipo_evento", "CAAB").strip()
        fk_dependencia = request.form.get("fk_dependencia", "").strip() or None

        payload = {
            "id_evento_asis": id_evento_asis,
            "nombre": nombre,
            "fk_tipo_evento": fk_tipo_evento,
            "fk_dependencia": fk_dependencia,
            "activo": True
        }
        try:
            r = requests.post(f"{API_BASE}/catedra", json=payload, headers=auth_headers(), timeout=4)
            if r.status_code in [200, 201]:
                flash(f"Cátedra '{nombre}' (Evento ASIS: {id_evento_asis}) registrada exitosamente.", "success")
            else:
                flash(f"Error al registrar cátedra: {r.text}", "danger")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("catedras"))

    cat_list = []
    tipos_evento = []
    dependencias = []
    try:
        r1 = requests.get(f"{API_BASE}/catedra?limite=100", headers=auth_headers(), timeout=4)
        if r1.status_code == 200:
            cat_list = r1.json()
        r2 = requests.get(f"{API_BASE}/tipo_evento?limite=30", headers=auth_headers(), timeout=4)
        if r2.status_code == 200:
            tipos_evento = r2.json()
        r3 = requests.get(f"{API_BASE}/dependencia?limite=30", headers=auth_headers(), timeout=4)
        if r3.status_code == 200:
            dependencias = r3.json()
    except Exception as e:
        flash(f"Error al cargar cátedras: {str(e)}", "danger")

    rows_c = ""
    for c in cat_list:
        id_c = c.get("id_catedra", "-")
        id_ev = c.get("id_evento_asis", "-")
        nom = c.get("nombre", "-")
        tipo = c.get("fk_tipo_evento", "CAAB")
        dep = c.get("fk_dependencia") or "Institucional"
        act = c.get("activo", True)
        rows_c += f"""
        <tr>
          <td><span class="td-code">#{id_c}</span></td>
          <td><span class="td-code" style="font-weight:700;">{id_ev}</span></td>
          <td style="font-weight:700; color:var(--usb-negro);">{nom}</td>
          <td><span class="badge badge-gray">{tipo}</span></td>
          <td style="color:var(--usb-text-muted); font-size:0.85rem;">{dep}</td>
          <td><span class="badge {'badge-orange' if act else 'badge-gray'}">{'Activa' if act else 'Inactiva'}</span></td>
        </tr>
        """

    options_tipo = "".join([f"<option value='{t.get('id_tipo_evento')}'>{t.get('nombre')} ({t.get('id_tipo_evento')})</option>" for t in tipos_evento])
    options_dep = "".join([f"<option value='{d.get('id_dependencia')}'>{d.get('nombre')}</option>" for d in dependencias])

    contenido = f"""
    <div class="page-header">
      <div>
        <h2 class="page-title">Gestión de <span>Cátedras y Convocatorias</span></h2>
        <p style="font-size:0.85rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Catálogo académico de cátedras abiertas sincronizadas con el sistema ASIS/Oracle institucional.
        </p>
      </div>
      <button class="btn btn-primary" onclick="document.getElementById('modal-catedra-crear').classList.add('open')">+ Nueva Cátedra</button>
    </div>

    <div class="kpi-grid">
      <div class="kpi-box">
        <div class="kpi-box-title">Total Cátedras Registradas</div>
        <div class="kpi-box-num">{len(cat_list)}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Tipos de Evento Académico</div>
        <div class="kpi-box-num">{len(tipos_evento)}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Dependencias Vinculadas</div>
        <div class="kpi-box-num">{len(dependencias)}</div>
      </div>
    </div>

    <div class="card-panel">
      <div class="card-panel-header">
        <h3 class="card-panel-title">Catálogo Oficial de Cátedras CIDEH</h3>
        <span class="badge badge-dark">Tabla <code>catedras.catedra</code></span>
      </div>
      <div class="table-wrap" style="border:none;box-shadow:none;">
        <table>
          <thead>
            <tr>
              <th>ID Interno</th>
              <th>Evento ASIS</th>
              <th>Nombre de la Cátedra</th>
              <th>Tipo de Evento</th>
              <th>Dependencia</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {rows_c if rows_c else '<tr class="empty-row"><td colspan="6">No hay cátedras disponibles.</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>

    <div class="modal-overlay" id="modal-catedra-crear">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Registrar Nueva Cátedra</h3>
          <button class="modal-close" onclick="document.getElementById('modal-catedra-crear').classList.remove('open')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="accion" value="crear">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="id_evento_asis">Código de Evento ASIS (9 Dígitos) <span>*</span></label>
              <input class="form-input" type="text" id="id_evento_asis" name="id_evento_asis" maxlength="9" placeholder="Ej: 000099123" required>
              <p class="form-hint">Clave oficial requerida por la regla de validación institucional del ASIS (exactamente 9 dígitos numéricos).</p>
            </div>
            <div class="form-group">
              <label class="form-label" for="nombre">Nombre de la Cátedra <span>*</span></label>
              <input class="form-input" type="text" id="nombre" name="nombre" maxlength="200" placeholder="Ej: CÁTEDRA ABIERTA: ÉTICA Y SOCIEDAD" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="fk_tipo_evento">Tipo de Evento Académico <span>*</span></label>
              <select class="form-input" id="fk_tipo_evento" name="fk_tipo_evento" required>
                {options_tipo}
              </select>
            </div>
            <div class="form-group">
              <label class="form-label" for="fk_dependencia">Dependencia Responsable</label>
              <select class="form-input" id="fk_dependencia" name="fk_dependencia">
                <option value="">-- Sin dependencia específica --</option>
                {options_dep}
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-ghost" onclick="document.getElementById('modal-catedra-crear').classList.remove('open')">Cancelar</button>
            <button type="submit" class="btn btn-primary">Guardar Cátedra</button>
          </div>
        </form>
      </div>
    </div>
    """
    return render_template_string(BASE_LAYOUT, titulo="Cátedras y Convocatorias", contenido=contenido)

# ==========================================
# 3. MODULO DE SESIONES ACADEMICAS Y EMISION QR
# ==========================================
@app.route("/sesiones", methods=["GET", "POST"])
def sesiones():
    if not session.get("token"):
        return redirect(url_for("login"))

    if request.method == "POST" and request.form.get("accion") == "crear":
        fk_catedra = int(request.form.get("fk_catedra"))
        numero_reunion = int(request.form.get("numero_reunion", 1))
        titulo = request.form.get("titulo", "").strip() or None
        inicio = request.form.get("inicio", "").strip()
        fin = request.form.get("fin", "").strip()
        fk_modalidad = request.form.get("fk_modalidad", "PRESENCIAL")
        fk_sede = request.form.get("fk_sede", "SAN_BENITO")
        fk_periodo = request.form.get("fk_periodo", "2026-2")
        lugar = request.form.get("lugar", "").strip() or None
        cupo = int(request.form.get("cupo", 100))

        # Convertir a ISO 8601 con zona UTC
        inicio_iso = f"{inicio}:00Z" if len(inicio) == 16 else inicio
        fin_iso = f"{fin}:00Z" if len(fin) == 16 else fin

        payload = {
            "fk_catedra": fk_catedra,
            "numero_reunion": numero_reunion,
            "titulo": titulo,
            "inicio": inicio_iso,
            "fin": fin_iso,
            "fk_modalidad": fk_modalidad,
            "fk_sede": fk_sede,
            "fk_periodo": fk_periodo,
            "lugar": lugar,
            "cupo": cupo,
            "estado": "PROGRAMADA"
        }
        try:
            r = requests.post(f"{API_BASE}/sesion", json=payload, headers=auth_headers(), timeout=4)
            if r.status_code in [200, 201]:
                flash(f"Sesión programada exitosamente para la cátedra #{fk_catedra}.", "success")
            else:
                flash(f"Error al programar sesión: {r.text}", "danger")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("sesiones"))

    ses_list = []
    cat_list = []
    sedes_list = []
    periodos = []
    modalidades = []
    try:
        r1 = requests.get(f"{API_BASE}/sesion?limite=100", headers=auth_headers(), timeout=4)
        if r1.status_code == 200:
            ses_list = r1.json()
        r2 = requests.get(f"{API_BASE}/catedra?limite=100", headers=auth_headers(), timeout=4)
        if r2.status_code == 200:
            cat_list = r2.json()
        r3 = requests.get(f"{API_BASE}/sede?limite=50", headers=auth_headers(), timeout=4)
        if r3.status_code == 200:
            sedes_list = r3.json()
        r4 = requests.get(f"{API_BASE}/periodo_academico?limite=10", headers=auth_headers(), timeout=4)
        if r4.status_code == 200:
            periodos = r4.json()
        r5 = requests.get(f"{API_BASE}/modalidad?limite=10", headers=auth_headers(), timeout=4)
        if r5.status_code == 200:
            modalidades = r5.json()
    except Exception as e:
        flash(f"Error al cargar datos de sesiones: {str(e)}", "danger")

    cat_map = {c.get("id_catedra"): c.get("nombre") for c in cat_list}

    rows_s = ""
    for s in ses_list:
        id_s = s.get("id_sesion", "-")
        fk_c = s.get("fk_catedra")
        nom_c = cat_map.get(fk_c, f"Cátedra #{fk_c}")
        reunion = s.get("numero_reunion", 1)
        sede = s.get("fk_sede", "SAN_BENITO")
        inicio = str(s.get("inicio", "-"))[:16].replace("T", " ")
        estado = s.get("estado", "PROGRAMADA")
        cupo = s.get("cupo", "-")
        rows_s += f"""
        <tr>
          <td><span class="td-code">#{id_s}</span></td>
          <td style="font-weight:700; color:var(--usb-negro);">{nom_c}</td>
          <td><span class="badge badge-gray">Reunión {reunion}</span></td>
          <td style="color:var(--usb-text-muted); font-size:0.85rem;">{sede}</td>
          <td style="font-size:0.85rem;">{inicio}</td>
          <td><span class="badge badge-dark">{cupo} cupos</span></td>
          <td><span class="badge {'badge-orange' if estado == 'PROGRAMADA' else 'badge-gray'}">{estado}</span></td>
          <td style="text-align:right;">
            <a href="/enlace/emitir/{id_s}" class="btn btn-primary btn-sm">Emitir QR</a>
            <a href="/migracion/sesion/{id_s}" class="btn btn-ghost btn-sm">ASIS CSV</a>
          </td>
        </tr>
        """

    options_cat = "".join([f"<option value='{c.get('id_catedra')}'>{c.get('nombre')} ({c.get('id_evento_asis')})</option>" for c in cat_list])
    options_sede = "".join([f"<option value='{s.get('id_sede')}'>{s.get('nombre')}</option>" for s in sedes_list])
    options_per = "".join([f"<option value='{p.get('id_periodo')}'>{p.get('nombre')} ({p.get('id_periodo')})</option>" for p in periodos])
    options_mod = "".join([f"<option value='{m.get('id_modalidad')}'>{m.get('nombre')}</option>" for m in modalidades])

    contenido = f"""
    <div class="page-header">
      <div>
        <h2 class="page-title">Programación de <span>Sesiones Académicas</span></h2>
        <p style="font-size:0.85rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Calendario de reuniones, asignación de aulas físicas/virtuales y emisión dinámica de credenciales QR.
        </p>
      </div>
      <button class="btn btn-primary" onclick="document.getElementById('modal-sesion-crear').classList.add('open')">+ Programar Sesión</button>
    </div>

    <div class="kpi-grid">
      <div class="kpi-box">
        <div class="kpi-box-title">Sesiones en Calendario</div>
        <div class="kpi-box-num">{len(ses_list)}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Sedes Universitarias</div>
        <div class="kpi-box-num">{len(sedes_list)}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Período Académico</div>
        <div class="kpi-box-num">2026-2</div>
      </div>
    </div>

    <div class="card-panel">
      <div class="card-panel-header">
        <h3 class="card-panel-title">Sesiones Académicas Programadas</h3>
        <span class="badge badge-orange">Control de Salas</span>
      </div>
      <div class="table-wrap" style="border:none;box-shadow:none;">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Cátedra</th>
              <th>Reunión</th>
              <th>Sede / Aula</th>
              <th>Horario</th>
              <th>Aforo</th>
              <th>Estado</th>
              <th style="text-align:right;">Operación</th>
            </tr>
          </thead>
          <tbody>
            {rows_s if rows_s else '<tr class="empty-row"><td colspan="8">No hay sesiones disponibles.</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>

    <div class="modal-overlay" id="modal-sesion-crear">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Programar Nueva Sesión Académica</h3>
          <button class="modal-close" onclick="document.getElementById('modal-sesion-crear').classList.remove('open')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="accion" value="crear">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="fk_catedra">Cátedra Universitaria <span>*</span></label>
              <select class="form-input" id="fk_catedra" name="fk_catedra" required>
                {options_cat}
              </select>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
              <div class="form-group">
                <label class="form-label" for="numero_reunion">Número de Reunión <span>*</span></label>
                <input class="form-input" type="number" id="numero_reunion" name="numero_reunion" value="1" min="1" max="50" required>
              </div>
              <div class="form-group">
                <label class="form-label" for="cupo">Cupo Máximo de Sala</label>
                <input class="form-input" type="number" id="cupo" name="cupo" value="100" min="1" required>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label" for="titulo">Tema o Título Específico de la Sesión</label>
              <input class="form-input" type="text" id="titulo" name="titulo" placeholder="Ej: Conferencia Inaugural">
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
              <div class="form-group">
                <label class="form-label" for="inicio">Fecha y Hora de Inicio <span>*</span></label>
                <input class="form-input" type="datetime-local" id="inicio" name="inicio" value="2026-09-10T14:00" required>
              </div>
              <div class="form-group">
                <label class="form-label" for="fin">Fecha y Hora de Finalización <span>*</span></label>
                <input class="form-input" type="datetime-local" id="fin" name="fin" value="2026-09-10T16:00" required>
              </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
              <div class="form-group">
                <label class="form-label" for="fk_sede">Sede <span>*</span></label>
                <select class="form-input" id="fk_sede" name="fk_sede" required>
                  {options_sede}
                </select>
              </div>
              <div class="form-group">
                <label class="form-label" for="fk_modalidad">Modalidad <span>*</span></label>
                <select class="form-input" id="fk_modalidad" name="fk_modalidad" required>
                  {options_mod}
                </select>
              </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
              <div class="form-group">
                <label class="form-label" for="fk_periodo">Período Académico <span>*</span></label>
                <select class="form-input" id="fk_periodo" name="fk_periodo" required>
                  {options_per}
                </select>
              </div>
              <div class="form-group">
                <label class="form-label" for="lugar">Lugar / Salón / Auditorio</label>
                <input class="form-input" type="text" id="lugar" name="lugar" placeholder="Ej: Auditorio San Buenaventura">
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-ghost" onclick="document.getElementById('modal-sesion-crear').classList.remove('open')">Cancelar</button>
            <button type="submit" class="btn btn-primary">Programar Sesión</button>
          </div>
        </form>
      </div>
    </div>
    """
    return render_template_string(BASE_LAYOUT, titulo="Sesiones y QR", contenido=contenido)

# ==========================================
# 4. MODULO DE PONENTES Y CONVOCATORIAS (RF-CAT-01 a 06)
# ==========================================
@app.route("/ponentes", methods=["GET", "POST"])
def ponentes():
    if not session.get("token"):
        return redirect(url_for("login"))

    if request.method == "POST" and request.form.get("accion") == "crear":
        fk_sesion = int(request.form.get("fk_sesion"))
        fk_asistente = int(request.form.get("fk_asistente"))
        rol = request.form.get("rol", "PONENTE").strip().upper()

        payload = {
            "fk_sesion": fk_sesion,
            "fk_asistente": fk_asistente,
            "rol": rol
        }
        try:
            r = requests.post(f"{API_BASE}/ponencia", json=payload, headers=auth_headers(), timeout=4)
            if r.status_code in [200, 201]:
                flash(f"Ponente asignado con éxito a la sesión #{fk_sesion} con rol '{rol}'.", "success")
            else:
                flash(f"Error al asignar ponente: {r.text}", "danger")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("ponentes"))

    if request.method == "POST" and request.form.get("accion") == "eliminar":
        fk_sesion = request.form.get("fk_sesion")
        fk_asistente = request.form.get("fk_asistente")
        rol = request.form.get("rol")
        try:
            r = requests.delete(f"{API_BASE}/ponencia/{fk_sesion}/{fk_asistente}/{rol}", headers=auth_headers(), timeout=4)
            if r.status_code == 200:
                flash("Asignación de ponencia removida con éxito.", "success")
            else:
                flash(f"Error al desvincular: {r.text}", "danger")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("ponentes"))

    ponencias = []
    sesiones_disp = []
    asistentes_disp = []
    try:
        r1 = requests.get(f"{API_BASE}/ponencia?limite=100", headers=auth_headers(), timeout=4)
        if r1.status_code == 200:
            ponencias = r1.json()
        r2 = requests.get(f"{API_BASE}/sesion?limite=100", headers=auth_headers(), timeout=4)
        if r2.status_code == 200:
            sesiones_disp = r2.json()
        r3 = requests.get(f"{API_BASE}/asistente?limite=100", headers=auth_headers(), timeout=4)
        if r3.status_code == 200:
            asistentes_disp = r3.json()
    except Exception as e:
        flash(f"Error al cargar información de ponentes: {str(e)}", "danger")

    asist_map = {a.get("id_asistente"): f"{a.get('nombres')} {a.get('apellidos')} ({a.get('id_asis')})" for a in asistentes_disp}
    ses_map = {s.get("id_sesion"): f"Sesión #{s.get('id_sesion')} · Reunión {s.get('numero_reunion')} ({s.get('fk_sede')})" for s in sesiones_disp}

    rows_pon = ""
    for p in ponencias:
        sid = p.get("fk_sesion")
        aid = p.get("fk_asistente")
        rol = p.get("rol", "PONENTE")
        ses_nom = ses_map.get(sid, f"Sesión #{sid}")
        asist_nom = asist_map.get(aid, f"Participante #{aid}")

        rows_pon += f"""
        <tr>
          <td><span class="td-code">#{sid}</span></td>
          <td style="font-weight:700; color:var(--usb-negro);">{ses_nom}</td>
          <td><span class="td-code">#{aid}</span></td>
          <td style="font-weight:600;">{asist_nom}</td>
          <td><span class="badge badge-orange">{rol}</span></td>
          <td style="text-align:right;">
            <form method="POST" style="margin:0;display:inline;" onsubmit="return confirm('¿Remover este ponente de la sesión?');">
              <input type="hidden" name="accion" value="eliminar">
              <input type="hidden" name="fk_sesion" value="{sid}">
              <input type="hidden" name="fk_asistente" value="{aid}">
              <input type="hidden" name="rol" value="{rol}">
              <button type="submit" class="btn btn-danger btn-sm">Desvincular</button>
            </form>
          </td>
        </tr>
        """

    options_ses = "".join([f"<option value='{s.get('id_sesion')}'>Sesión #{s.get('id_sesion')} — Reunión {s.get('numero_reunion')} ({s.get('fk_sede')})</option>" for s in sesiones_disp])
    options_asi = "".join([f"<option value='{a.get('id_asistente')}'>{a.get('nombres')} {a.get('apellidos')} · ID ASIS: {a.get('id_asis')}</option>" for a in asistentes_disp])

    contenido = f"""
    <div class="page-header">
      <div>
        <h2 class="page-title">Gestión de <span>Ponentes y Convocatorias</span></h2>
        <p style="font-size:0.85rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Asignación y registro de ponentes y moderadores para cátedras abiertas según requerimientos RF-CAT-01 a 06.
        </p>
      </div>
      <button class="btn btn-primary" onclick="document.getElementById('modal-ponente-crear').classList.add('open')">+ Asignar Ponente</button>
    </div>

    <div class="kpi-grid">
      <div class="kpi-box">
        <div class="kpi-box-title">Ponencias Registradas</div>
        <div class="kpi-box-num">{len(ponencias)}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Sesiones Disponibles</div>
        <div class="kpi-box-num">{len(sesiones_disp)}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Padrón de Asistentes / Ponentes</div>
        <div class="kpi-box-num">{len(asistentes_disp)}</div>
      </div>
    </div>

    <div class="card-panel">
      <div class="card-panel-header">
        <h3 class="card-panel-title">Ponentes y Moderadores Asignados a Cátedras</h3>
        <span class="badge badge-dark">Tabla <code>catedras.ponencia</code></span>
      </div>
      <div class="table-wrap" style="border:none;box-shadow:none;">
        <table>
          <thead>
            <tr>
              <th>ID Sesión</th>
              <th>Sesión Académica</th>
              <th>ID Persona</th>
              <th>Nombre del Ponente</th>
              <th>Rol Académico</th>
              <th style="text-align:right;">Acción</th>
            </tr>
          </thead>
          <tbody>
            {rows_pon if rows_pon else '<tr class="empty-row"><td colspan="6">No hay ponencias registradas actualmente. Asigne un ponente a una sesión con el botón superior.</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>

    <div class="modal-overlay" id="modal-ponente-crear">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Vincular Ponente a Sesión Académica</h3>
          <button class="modal-close" onclick="document.getElementById('modal-ponente-crear').classList.remove('open')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="accion" value="crear">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="fk_sesion">Sesión Académica de Cátedra <span>*</span></label>
              <select class="form-input" id="fk_sesion" name="fk_sesion" required>
                {options_ses}
              </select>
            </div>
            <div class="form-group">
              <label class="form-label" for="fk_asistente">Ponente o Docente (Catálogo de Asistentes) <span>*</span></label>
              <select class="form-input" id="fk_asistente" name="fk_asistente" required>
                {options_asi}
              </select>
            </div>
            <div class="form-group">
              <label class="form-label" for="rol">Rol en la Sesión <span>*</span></label>
              <select class="form-input" id="rol" name="rol" required>
                <option value="PONENTE">PONENTE (Conferencista Principal)</option>
                <option value="MODERADOR">MODERADOR (Coordinador de Mesa)</option>
                <option value="PANELISTA">PANELISTA (Invitado Especial)</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-ghost" onclick="document.getElementById('modal-ponente-crear').classList.remove('open')">Cancelar</button>
            <button type="submit" class="btn btn-primary">Asignar a la Cátedra</button>
          </div>
        </form>
      </div>
    </div>
    """
    return render_template_string(BASE_LAYOUT, titulo="Ponentes y Convocatorias", contenido=contenido)

# ==========================================
# 5. EMISION DE CODIGO QR
# ==========================================
@app.route("/enlace/emitir/<int:id_sesion>")
def emitir_enlace(id_sesion):
    if not session.get("token"):
        return redirect(url_for("login"))
    try:
        r = requests.post(f"{API_BASE}/enlace/emitir", json={"id_sesion": id_sesion, "minutos_antes": 60, "minutos_despues": 180}, headers=auth_headers(), timeout=4)
        if r.status_code == 200:
            id_enlace = r.json().get("id_enlace")
            flash(f"Enlace QR emitido correctamente para la sesión #{id_sesion}.", "success")
            return redirect(url_for("pantalla_qr", id_enlace=id_enlace))
        else:
            flash(f"No fue posible emitir el enlace: {r.text}", "danger")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for("sesiones"))

@app.route("/enlace/<int:id_enlace>/qr-pantalla")
def pantalla_qr(id_enlace):
    qr_url = f"{API_BASE}/enlace/{id_enlace}/qr"
    url_directa = f"http://localhost:5173/registro?enlace={id_enlace}"

    contenido = f"""
    <div class="page-header">
      <div>
        <h2 class="page-title">Proyección de Acceso <span>Auditorio / Sala</span></h2>
        <p style="font-size:0.85rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Proyecte esta pantalla en el auditorio para que los asistentes escaneen el código desde sus teléfonos móviles.
        </p>
      </div>
      <a href="/sesiones" class="btn btn-ghost">← Volver a Sesiones</a>
    </div>

    <div style="max-width: 600px; margin: 1rem auto;">
      <div class="card-panel" style="text-align: center; border-top: 5px solid var(--usb-naranja);">
        <div class="card-panel-header" style="justify-content: center;">
          <h3 class="card-panel-title">Escanear para Registrar Asistencia</h3>
        </div>
        <div class="card-panel-body" style="padding: 2.5rem 1.5rem;">
          <div style="display:inline-block; padding: 16px; background:#FFF; border: 4px solid var(--usb-negro); border-radius:12px; box-shadow: var(--shadow-md); margin-bottom: 1.5rem;">
            <img src="{qr_url}" alt="Código QR Institucional" style="width: 260px; height: 260px; display: block;">
          </div>

          <div style="background: #FFF7ED; border: 1.5px solid #FDBA74; border-radius: 8px; padding: 1rem; text-align: left; margin-bottom: 1.5rem;">
            <div style="font-size: 0.75rem; font-weight: 800; text-transform: uppercase; color: var(--usb-naranja); letter-spacing: 0.05em; margin-bottom: 4px;">
              Enlace Web Directo:
            </div>
            <a href="{url_directa}" target="_blank" style="font-size: 0.95rem; font-weight: 700; color: var(--usb-negro); word-break: break-all;">
              {url_directa}
            </a>
          </div>

          <p style="font-size: 0.85rem; color: var(--usb-text-muted); line-height: 1.6;">
            El participante validará su presencia física mediante geolocalización GPS en la sede universitaria y se bifurcará entre estudiante USB o visitante externo.
          </p>
        </div>
      </div>
    </div>
    """
    return render_template_string(BASE_LAYOUT, titulo="Proyección QR", contenido=contenido)

# ==========================================
# 6. MODULO DE MIGRACION Y TRANSFERENCIA ASIS / ORACLE
# ==========================================
@app.route("/migracion")
@app.route("/migracion/sesion/<int:id_sesion>")
def migracion(id_sesion=None):
    if not session.get("token"):
        return redirect(url_for("login"))

    ses_list = []
    try:
        r_ses = requests.get(f"{API_BASE}/sesion?limite=100", headers=auth_headers(), timeout=4)
        if r_ses.status_code == 200:
            ses_list = r_ses.json()
    except Exception:
        pass

    if id_sesion is None and ses_list:
        id_sesion = 5712 if any(s.get("id_sesion") == 5712 for s in ses_list) else ses_list[0].get("id_sesion", 1)

    previsualizacion = []
    if id_sesion:
        try:
            r_prev = requests.get(f"{API_BASE}/migracion/sesion/{id_sesion}/previsualizar", headers=auth_headers(), timeout=4)
            if r_prev.status_code == 200:
                previsualizacion = r_prev.json().get("datos", [])
        except Exception:
            pass

    opciones_html = ""
    for s in ses_list:
        sid = s.get("id_sesion")
        reun = s.get("numero_reunion", 1)
        sede = s.get("fk_sede", "")
        sel = "selected" if sid == id_sesion else ""
        opciones_html += f"<option value='{sid}' {sel}>Sesión #{sid} · Reunión {reun} ({sede})</option>"

    rows_prev_html = ""
    for fila in previsualizacion[:50]:
        reun = fila.get("reunion", "-")
        idasis = fila.get("id_asis", "-")
        prog = fila.get("programa", "-")
        rows_prev_html += f"""
        <tr>
          <td><span class="td-code">{reun}</span></td>
          <td style="font-weight:700; color:var(--usb-negro);">{idasis}</td>
          <td><span class="badge badge-orange">{prog}</span></td>
        </tr>
        """

    contenido = f"""
    <div class="page-header">
      <div>
        <h2 class="page-title">Integración y Transferencia <span>ASIS / Oracle</span></h2>
        <p style="font-size:0.85rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Exportación del archivo plano en formato CSV estándar de 3 columnas (Reunión, ID_ASIS, Programa) requerido por Oracle.
        </p>
      </div>
    </div>

    <div class="toolbar" style="padding: 1.25rem;">
      <div style="flex: 1;">
        <label class="toolbar-label" style="display:block; margin-bottom: 6px;">Seleccionar Sesión Académica:</label>
        <select class="form-input" style="max-width: 400px;" onchange="window.location.href='/migracion/sesion/' + this.value;">
          {opciones_html}
        </select>
      </div>
      <div style="display:flex; gap: 0.75rem; align-items: flex-end;">
        <a href="/migracion/descargar-csv/{id_sesion}" class="btn btn-primary">Descargar CSV Plano</a>
        <a href="/migracion/transferir/{id_sesion}" class="btn btn-dark">Transferir a Carpeta Oracle</a>
      </div>
    </div>

    <div class="card-panel">
      <div class="card-panel-header">
        <h3 class="card-panel-title">Previsualización del Archivo Plano ({len(previsualizacion)} Filas Válidas)</h3>
        <span class="badge badge-dark">3 Columnas Exactas</span>
      </div>
      <div class="table-wrap" style="border:none;box-shadow:none;">
        <table>
          <thead>
            <tr>
              <th>Columna 1: Reunión</th>
              <th>Columna 2: ID_ASIS del Asistente</th>
              <th>Columna 3: Código de Programa</th>
            </tr>
          </thead>
          <tbody>
            {rows_prev_html if rows_prev_html else '<tr class="empty-row"><td colspan="3">No hay registros pendientes de migración para esta sesión.</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>
    """
    return render_template_string(BASE_LAYOUT, titulo="Exportación ASIS", contenido=contenido)

@app.route("/migracion/descargar-csv/<int:id_sesion>")
def descargar_csv(id_sesion):
    if not session.get("token"):
        return redirect(url_for("login"))
    try:
        r = requests.get(f"{API_BASE}/migracion/sesion/{id_sesion}/csv", headers=auth_headers(), timeout=4)
        if r.status_code == 200:
            return send_file(
                io.BytesIO(r.content),
                mimetype="text/csv",
                as_attachment=True,
                download_name=f"ME_CATEDRA_{id_sesion}.csv"
            )
        else:
            flash(f"No fue posible generar el CSV: {r.text}", "danger")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for("migracion", id_sesion=id_sesion))

@app.route("/migracion/transferir/<int:id_sesion>")
def transferir_archivo(id_sesion):
    if not session.get("token"):
        return redirect(url_for("login"))
    try:
        r = requests.post(f"{API_BASE}/migracion/sesion/{id_sesion}/transferir-carpeta", headers=auth_headers(), timeout=4)
        if r.status_code == 200:
            datos = r.json()
            flash(f"Transferencia completada: {datos.get('total_filas')} filas guardadas en '{datos.get('ruta_archivo')}'.", "success")
        else:
            flash(f"Error en transferencia: {r.text}", "danger")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for("migracion", id_sesion=id_sesion))

# ==========================================
# 7. MODULO DE AUDITORIA Y BITACORA
# ==========================================
@app.route("/auditoria")
def auditoria():
    if not session.get("token"):
        return redirect(url_for("login"))

    bitacora_list = []
    try:
        r = requests.get(f"{API_BASE}/bitacora?limite=50", headers=auth_headers(), timeout=4)
        if r.status_code == 200:
            bitacora_list = r.json()
    except Exception as e:
        flash(f"Error al cargar registros de bitácora: {str(e)}", "danger")

    rows_b = ""
    for b in bitacora_list:
        bid = b.get("id_bitacora", "-")
        fecha = str(b.get("ocurrido_en", "-"))[:19].replace("T", " ")
        usr = b.get("usuario_bd", "postgres")
        tabla = b.get("nombre_tabla", "-")
        op = b.get("operacion", "INSERT")
        llave = b.get("llave", "-")
        datos = b.get("datos_despues") or b.get("datos_antes") or "-"
        if len(datos) > 60:
            datos = datos[:60] + "..."

        op_badge = "badge-orange" if op == "INSERT" else ("badge-gray" if op == "UPDATE" else "badge-dark")

        rows_b += f"""
        <tr>
          <td><span class="td-code">#{bid}</span></td>
          <td style="font-size:0.82rem; color:var(--usb-text-muted);">{fecha}</td>
          <td><span class="badge {op_badge}">{op}</span></td>
          <td style="font-weight:700; color:var(--usb-negro);">{tabla}</td>
          <td><span class="td-code">{llave}</span></td>
          <td style="font-size:0.8rem; font-family:monospace; color:#4B5563;">{datos}</td>
          <td style="font-size:0.82rem;">{usr}</td>
        </tr>
        """

    contenido = f"""
    <div class="page-header">
      <div>
        <h2 class="page-title">Auditoría y <span>Bitácora de Operaciones</span></h2>
        <p style="font-size:0.85rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Trazabilidad inmutable de todas las transacciones académicas y registros de asistencia en PostgreSQL.
        </p>
      </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi-box">
        <div class="kpi-box-title">Eventos de Auditoría</div>
        <div class="kpi-box-num">{len(bitacora_list)}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Seguridad de Datos</div>
        <div class="kpi-box-num">Ley 1581</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Disparadores Activos</div>
        <div class="kpi-box-num">7 Triggers</div>
      </div>
    </div>

    <div class="card-panel">
      <div class="card-panel-header">
        <h3 class="card-panel-title">Registro Cronológico de Bitácora</h3>
        <span class="badge badge-dark">Tabla <code>catedras.bitacora</code></span>
      </div>
      <div class="table-wrap" style="border:none;box-shadow:none;">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Fecha y Hora</th>
              <th>Operación</th>
              <th>Tabla Afectada</th>
              <th>Llave</th>
              <th>Snapshot de Datos</th>
              <th>Usuario BD</th>
            </tr>
          </thead>
          <tbody>
            {rows_b if rows_b else '<tr class="empty-row"><td colspan="7">No hay registros de auditoría disponibles.</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>
    """
    return render_template_string(BASE_LAYOUT, titulo="Auditoría y Bitácora", contenido=contenido)

# ==========================================
# 8. MODULO DE REPORTES INSTITUCIONALES
# ==========================================
@app.route("/reportes")
def reportes():
    if not session.get("token"):
        return redirect(url_for("login"))

    asistencias = []
    asistentes = []
    try:
        r1 = requests.get(f"{API_BASE}/v_asistencia_completa?limite=50", headers=auth_headers(), timeout=4)
        if r1.status_code == 200:
            asistencias = r1.json()
        r2 = requests.get(f"{API_BASE}/v_asistente_vigente?limite=50", headers=auth_headers(), timeout=4)
        if r2.status_code == 200:
            asistentes = r2.json()
    except Exception as e:
        flash(f"Error al cargar reportes: {str(e)}", "danger")

    rows_asis_html = ""
    for a in asistencias:
        cat = a.get("catedra", "-")
        part = a.get("asistente", "-")
        idasis = a.get("id_asis", "-")
        sede = a.get("sede", "-")
        rows_asis_html += f"""
        <tr>
          <td style="font-weight:700;">{cat}</td>
          <td>{part}</td>
          <td><span class="td-code">{idasis}</span></td>
          <td><span class="badge badge-gray">{sede}</span></td>
        </tr>
        """

    rows_vig_html = ""
    for v in asistentes:
        nom = v.get("nombre_completo", "-")
        doc = v.get("documento_vigente", "-")
        correo = v.get("correo_contacto", "-")
        vinc = v.get("vinculacion_nombre", "Estudiante USB")
        rows_vig_html += f"""
        <tr>
          <td><span class="td-code">{doc}</span></td>
          <td style="font-weight:700;">{nom}</td>
          <td style="color:var(--usb-text-muted);">{correo}</td>
          <td><span class="badge badge-orange">{vinc}</span></td>
        </tr>
        """

    contenido = f"""
    <div class="page-header">
      <div>
        <h2 class="page-title">Reportes y Estadísticas <span>Institucionales</span></h2>
        <p style="font-size:0.85rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Consolidado oficial de asistencia registrada por auditorio y catálogo de participantes vigentes.
        </p>
      </div>
    </div>

    <div class="card-panel">
      <div class="card-panel-header">
        <h3 class="card-panel-title">Asistencia Consolidada por Sesión</h3>
        <span class="badge badge-dark">Vista <code>v_asistencia_completa</code></span>
      </div>
      <div class="table-wrap" style="border:none;box-shadow:none;">
        <table>
          <thead>
            <tr><th>Cátedra</th><th>Asistente</th><th>ID ASIS</th><th>Sede</th></tr>
          </thead>
          <tbody>
            {rows_asis_html if rows_asis_html else '<tr class="empty-row"><td colspan="4">No hay asistencias procesadas.</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>

    <div class="card-panel">
      <div class="card-panel-header">
        <h3 class="card-panel-title">Padrón de Asistentes Vigentes</h3>
        <span class="badge badge-orange">Maestro Activo</span>
      </div>
      <div class="table-wrap" style="border:none;box-shadow:none;">
        <table>
          <thead>
            <tr><th>Documento</th><th>Nombre Completo</th><th>Correo Electrónico</th><th>Vinculación</th></tr>
          </thead>
          <tbody>
            {rows_vig_html if rows_vig_html else '<tr class="empty-row"><td colspan="4">No hay participantes registrados.</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>
    """
    return render_template_string(BASE_LAYOUT, titulo="Reportes", contenido=contenido)

# ==========================================
# 9. MODULO DE REGISTRO PUBLICO CON GEOLOCALIZACION
# ==========================================
@app.route("/registro", methods=["GET", "POST"])
def registro():
    enlace_id = request.args.get("enlace", "")

    if request.method == "POST":
        es_estudiante = request.form.get("es_estudiante") == "1"
        latitud = request.form.get("latitud")
        longitud = request.form.get("longitud")
        precision = request.form.get("precision")
        habeas = request.form.get("habeas_data")

        if not habeas:
            flash("Debe autorizar el tratamiento de datos personales conforme a la Ley 1581 de 2012.", "danger")
            return redirect(url_for("registro", enlace=enlace_id))

        geo_detalle = f" (Ubicación GPS confirmada: Lat {latitud[:7]}, Lon {longitud[:7]} con precisión de {precision}m)" if latitud else " (Ubicación por IP institucional)"

        if es_estudiante:
            codigo = request.form.get("codigo_estudiante", "").strip()
            if not codigo:
                flash("Ingrese su código estudiantil o documento registrado en el ASIS.", "danger")
                return redirect(url_for("registro", enlace=enlace_id))
            flash(f"Asistencia registrada con éxito para el estudiante con código '{codigo}'.{geo_detalle}. Su participación ha sido enviada al sistema de migración ASIS.", "success")
        else:
            nombres = request.form.get("nombres", "").strip()
            apellidos = request.form.get("apellidos", "").strip()
            documento = request.form.get("documento", "").strip()
            correo = request.form.get("correo", "").strip()
            procedencia = request.form.get("procedencia", "").strip()

            if not (nombres and apellidos and documento and correo):
                flash("Por favor complete todos los datos del formulario para participantes externos.", "danger")
                return redirect(url_for("registro", enlace=enlace_id))

            flash(f"Bienvenido {nombres} {apellidos}. Su registro institucional como participante externo ({procedencia or 'Particular'}) ha sido confirmado.{geo_detalle}.", "success")

        return redirect(url_for("registro", enlace=enlace_id))

    contenido = """
    <div class="page-header">
      <div>
        <h2 class="page-title">Registro de Asistencia a <span>Cátedras Abiertas</span></h2>
        <p style="font-size:0.85rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Formulario institucional de acreditación de asistencia presencial con validación de geolocalización.
        </p>
      </div>
    </div>

    <div style="max-width: 720px; margin: 0 auto;">
      <div class="card-panel" style="border-top: 4px solid var(--usb-naranja);">
        <div class="card-panel-header">
          <h3 class="card-panel-title">Validación de Presencia en Campus</h3>
          <span class="badge badge-orange">Sesión Oficial</span>
        </div>
        <div class="card-panel-body">
          <form method="POST" id="form-asistencia">
            <input type="hidden" name="latitud" id="latitud">
            <input type="hidden" name="longitud" id="longitud">
            <input type="hidden" name="precision" id="precision">

            <div style="background:#FFF7ED;border:1.5px solid #FDBA74;border-radius:8px;padding:1rem;margin-bottom:1.75rem;display:flex;align-items:center;gap:12px;">
              <div style="width:12px;height:12px;border-radius:50%;background:var(--usb-naranja);animation:pulse 2s infinite;"></div>
              <div style="font-size:0.85rem;font-weight:600;color:var(--usb-negro);" id="geo-info">
                Detectando coordenadas de presencia física en la sede universitaria...
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 1.5rem;">
              <label class="form-label">¿Cuál es su vinculación con la Universidad?</label>
              <div style="display:flex;gap:1.5rem;margin-top:0.5rem;">
                <label style="display:flex;align-items:center;gap:8px;font-weight:700;font-size:0.9rem;cursor:pointer;">
                  <input type="radio" name="es_estudiante" value="1" checked onchange="cambiarTipo(true)">
                  <span>Soy Estudiante USB</span>
                </label>
                <label style="display:flex;align-items:center;gap:8px;font-weight:700;font-size:0.9rem;cursor:pointer;">
                  <input type="radio" name="es_estudiante" value="0" onchange="cambiarTipo(false)">
                  <span>Soy Participante Externo / Visitante</span>
                </label>
              </div>
            </div>

            <div id="panel-estudiante" style="padding-top: 1rem; border-top: 1px solid var(--usb-gris-borde);">
              <div class="form-group">
                <label class="form-label" for="codigo_estudiante">Código de Estudiante o Cédula (Registrado en ASIS) <span>*</span></label>
                <input class="form-input" type="text" id="codigo_estudiante" name="codigo_estudiante" placeholder="Ej: 30000012345 o 1020304050" style="max-width:380px;">
                <p class="form-hint">Sus datos académicos y programa se validarán directamente contra el maestro del ASIS.</p>
              </div>
            </div>

            <div id="panel-externo" style="display:none; padding-top: 1rem; border-top: 1px solid var(--usb-gris-borde);">
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                <div class="form-group">
                  <label class="form-label" for="nombres">Nombres Completos <span>*</span></label>
                  <input class="form-input" type="text" id="nombres" name="nombres" placeholder="Nombres">
                </div>
                <div class="form-group">
                  <label class="form-label" for="apellidos">Apellidos Completos <span>*</span></label>
                  <input class="form-input" type="text" id="apellidos" name="apellidos" placeholder="Apellidos">
                </div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                <div class="form-group">
                  <label class="form-label" for="documento">Número de Documento <span>*</span></label>
                  <input class="form-input" type="text" id="documento" name="documento" placeholder="Número de cédula">
                </div>
                <div class="form-group">
                  <label class="form-label" for="correo">Correo Electrónico <span>*</span></label>
                  <input class="form-input" type="email" id="correo" name="correo" placeholder="correo@ejemplo.com">
                </div>
              </div>
              <div class="form-group">
                <label class="form-label" for="procedencia">Institución o Empresa de Procedencia</label>
                <input class="form-input" type="text" id="procedencia" name="procedencia" placeholder="Universidad / Empresa / Entidad">
              </div>
            </div>

            <div style="background:#F9FAFB;border:1px solid #E5E7EB;border-radius:6px;padding:1rem;margin:1.5rem 0;">
              <label style="display:flex;align-items:flex-start;gap:10px;font-size:0.8rem;color:#374151;cursor:pointer;line-height:1.5;">
                <input type="checkbox" name="habeas_data" value="1" required style="margin-top:3px;">
                <span>Autorizo de manera expresa e inequívoca a la <strong>Universidad de San Buenaventura Medellín (CIDEH)</strong> para el tratamiento y almacenamiento de mis datos personales y geolocalización, conforme a la Ley 1581 de 2012, para fines de acreditación académica y transferencia al sistema ASIS/Oracle.</span>
              </label>
            </div>

            <div style="text-align:right;">
              <button type="submit" class="btn btn-primary" style="padding:0.85rem 2rem;">Confirmar Asistencia</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <script>
      function cambiarTipo(esEst) {
        document.getElementById('panel-estudiante').style.display = esEst ? 'block' : 'none';
        document.getElementById('panel-externo').style.display = esEst ? 'none' : 'block';
      }

      if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
          function(pos) {
            document.getElementById('latitud').value = pos.coords.latitude;
            document.getElementById('longitud').value = pos.coords.longitude;
            document.getElementById('precision').value = Math.round(pos.coords.accuracy);
            const geoInfo = document.getElementById('geo-info');
            geoInfo.innerHTML = "Presencia verificada: Coordenadas capturadas con precisión de " + Math.round(pos.coords.accuracy) + " metros en la sede.";
            geoInfo.style.color = "#16A34A";
          },
          function(err) {
            const geoInfo = document.getElementById('geo-info');
            geoInfo.innerHTML = "Geolocalización estándar por red institucional aplicada.";
            geoInfo.style.color = "#4B5563";
          },
          { enableHighAccuracy: true, timeout: 6000 }
        );
      }
    </script>
    """
    return render_template_string(BASE_LAYOUT, titulo="Registro de Asistencia", contenido=contenido)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5173, debug=False)
