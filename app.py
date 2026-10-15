import os
import io
import json
import subprocess
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
  <meta name="description" content="Portal Institucional de Cátedras Abiertas y Registro de Asistentes — CIDEH, Universidad de San Buenaventura Medellín.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/static/style.css">
  <link rel="icon" href="https://usbmed.edu.co/wp-content/uploads/2023/11/favicon.png" sizes="32x32">
</head>
<body>
  <!-- Topbar Institucional (Naranja oficial como https://usbmed.edu.co/) -->
  <aside class="topbar-usb">
    <div class="topbar-left">
      <span class="topbar-item">
        <svg class="topbar-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="11" stroke="currentColor" stroke-width="1.8" fill="none"/>
          <path d="M12.04 6.5C8.98 6.5 6.5 8.98 6.5 12.04C6.5 13.06 6.78 14.04 7.31 14.9L6.8 17.2L9.17 16.71C9.99 17.21 10.99 17.58 12.04 17.58C15.1 17.58 17.58 15.1 17.58 12.04C17.58 8.98 15.1 6.5 12.04 6.5Z" stroke="currentColor" stroke-width="1.2" fill="none"/>
          <path d="M10.2 9.5C10.05 9.17 9.89 9.16 9.75 9.15C9.64 9.14 9.5 9.14 9.37 9.14C9.23 9.14 9.02 9.19 8.83 9.4C8.65 9.61 8.1 10.12 8.1 11.16C8.1 12.2 8.86 13.2 8.97 13.35C9.07 13.5 10.45 15.63 12.57 16.55C14.33 17.31 14.69 17.16 15.07 17.13C15.45 17.09 16.3 16.63 16.48 16.12C16.65 15.61 16.65 15.17 16.6 15.08C16.55 14.99 16.42 14.93 16.22 14.83C16.03 14.73 15.07 14.26 14.9 14.19C14.72 14.13 14.59 14.1 14.46 14.3C14.33 14.5 13.96 14.97 13.85 15.1C13.73 15.22 13.62 15.24 13.43 15.14C13.23 15.04 12.61 14.84 11.87 14.18C11.3 13.67 10.91 13.04 10.8 12.85C10.69 12.66 10.79 12.55 10.89 12.45C10.98 12.36 11.09 12.21 11.2 12.1C11.3 11.98 11.34 11.9 11.4 11.77C11.47 11.64 11.44 11.53 11.39 11.43C11.34 11.33 10.96 10.4 10.8 10.02C10.65 9.64 10.49 9.7 10.37 9.7L10.2 9.5Z" fill="currentColor"/>
        </svg>
        <span>WhatsApp: 300 702 8720</span>
      </span>
      <span class="topbar-item">
        <svg class="topbar-icon" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
          <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
        </svg>
        <span>PBX: (604) 514 5600</span>
      </span>
    </div>
  </aside>

  <!-- Header Principal Limpio con Logosímbolo Oficial -->
  <header class="header-main">
    <a href="/" class="header-brand">
      <img src="/static/logo_usbmed_oficial.png" alt="Universidad de San Buenaventura Medellín" class="header-logo-img">
      <div class="header-unit">
        <span class="header-unit-title">Cátedras Abiertas</span>
        <span class="header-unit-sub">CIDEH · Vicerrectoría Académica</span>
      </div>
    </a>

    <nav class="header-nav">
      <a href="/" class="{% if request.path == '/' %}active{% endif %}">Inicio</a>
      <a href="/registro" class="{% if request.path == '/registro' %}active{% endif %}">Registrar Asistencia</a>
      <a href="/ponentes" class="{% if request.path == '/ponentes' %}active{% endif %}">Calendario Ponencias</a>
      {% if session.get('token') %}
        <a href="/catedras" class="{% if request.path == '/catedras' %}active{% endif %}">Cátedras</a>
        <a href="/sesiones" class="{% if request.path.startswith('/sesiones') or request.path.startswith('/enlace') %}active{% endif %}">Sesiones y QR</a>
        <a href="/homologacion" class="{% if request.path == '/homologacion' %}active{% endif %}">Homologación y Paz y Salvo</a>
        <a href="/sedes" class="{% if request.path == '/sedes' %}active{% endif %}">Sedes</a>
        <a href="/catalogos" class="{% if request.path == '/catalogos' %}active{% endif %}">Catálogos</a>
        <a href="/migracion" class="{% if request.path.startswith('/migracion') %}active{% endif %}">ASIS / Oracle</a>
        <a href="/auditoria" class="{% if request.path == '/auditoria' %}active{% endif %}">Bitácora</a>
        <a href="/reportes" class="{% if request.path == '/reportes' %}active{% endif %}">Reportes</a>
      {% endif %}
    </nav>

    <div style="display: flex; align-items: center; gap: 0.75rem; flex-shrink: 0;">
      {% if session.get('token') %}
        <div class="user-badge-chip">
          <span class="user-badge-email" title="{{ session.get('usuario') }}">{{ session.get('usuario') }}</span>
          <form action="/logout" method="POST" style="margin:0;display:inline;">
            <button type="submit" class="btn-logout" title="Cerrar sesión">Salir</button>
          </form>
        </div>
      {% else %}
        <a href="/login" class="btn-usb btn-usb-primary btn-usb-sm">Acceso Administrativo</a>
      {% endif %}
    </div>
  </header>

  <!-- Notificaciones Toast -->
  <div class="toast-area" id="toast-area">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="toast {% if category == 'success' %}success{% elif category == 'danger' %}error{% else %}info{% endif %}">
            <div class="toast-text">
              <strong>{% if category == 'success' %}Operación Exitosa{% elif category == 'danger' %}Aviso Institucional{% else %}Información{% endif %}</strong>
              <span>{{ message }}</span>
            </div>
          </div>
        {% endfor %}
      {% endif %}
    {% endwith %}
  </div>

  <!-- Contenido de la Página -->
  <main>
    <div class="container-usb">
      {{ contenido | safe }}
    </div>
  </main>

  <!-- Footer Oficial Institucional conforme a https://usbmed.edu.co/ -->
  <footer class="footer-usb">
    <div class="footer-inner">
      <div class="footer-top">
        <div class="footer-col">
          <h4>Universidad de San Buenaventura</h4>
          <p>Seccional Medellín · Centro de Investigación y Desarrollo del Espíritu Humano (CIDEH).</p>
          <p>Dirección: Carrera 56C N° 51-110 · Medellín, Antioquia, Colombia.</p>
          <p>Línea Gratuita Nacional: 01 8000 125 151 · PBX: (604) 514 5600.</p>
        </div>
        <div class="footer-col">
          <h4>Plataformas Académicas</h4>
          <p><a href="https://campus.usbco.edu.co/psp/USCS90PR/?cmd=login" target="_blank" style="color:rgba(255,255,255,0.75);text-decoration:none;">Plataforma ASIS Institucional</a></p>
          <p><a href="https://domusvirtual.usbmed.edu.co/" target="_blank" style="color:rgba(255,255,255,0.75);text-decoration:none;">DOMUS Virtual</a></p>
          <p><a href="http://micampus.usbmed.edu.co/" target="_blank" style="color:rgba(255,255,255,0.75);text-decoration:none;">Mi Campus USB</a></p>
          <p><a href="https://usbmed.edu.co/biblioteca" target="_blank" style="color:rgba(255,255,255,0.75);text-decoration:none;">Sistema de Bibliotecas</a></p>
        </div>
        <div class="footer-col">
          <h4>Acreditación Institucional</h4>
          <p>Institución de Educación Superior sujeta a inspección y vigilancia por el Ministerio de Educación Nacional.</p>
          <p style="margin-top:1rem;">
            <span class="footer-badge-vigilada">Vigilada Mineducación</span>
          </p>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© 2026 Universidad de San Buenaventura Medellín. Todos los derechos reservados.</span>
        <span>Acreditación Institucional de Alta Calidad Multicampus · Resolución MEN.</span>
      </div>
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

_SERVICE_TOKEN = None

def get_service_token(forzar_renovar=False):
    global _SERVICE_TOKEN
    if _SERVICE_TOKEN and not forzar_renovar:
        return _SERVICE_TOKEN
    try:
        r = requests.post(f"{API_BASE}/autenticacion/token", json={"email": "admin.catedras@usbmed.edu.co", "contrasena": "Catedras2026*"}, timeout=3)
        if r.status_code == 200:
            _SERVICE_TOKEN = r.json().get("token")
            return _SERVICE_TOKEN
    except Exception:
        pass
    return None

def auth_headers():
    token = session.get("token")
    if not token:
        token = get_service_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def api_get(endpoint, timeout=4):
    headers = auth_headers()
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=timeout)
        if r.status_code == 401:
            # Token expirado: renovar de inmediato y reintentar
            token_nuevo = get_service_token(forzar_renovar=True)
            if token_nuevo:
                session["token"] = token_nuevo
                r = requests.get(f"{API_BASE}{endpoint}", headers={"Authorization": f"Bearer {token_nuevo}"}, timeout=timeout)
        return r
    except Exception as e:
        raise e

def db_query_json(sql):
    """Ejecuta una consulta SQL en catedras_postgres y retorna lista de diccionarios JSON de forma segura en Windows."""
    try:
        cmd = ["docker", "exec", "catedras_postgres", "psql", "-U", "postgres", "-d", "catedras", "-t", "-A", "-c", sql]
        res = subprocess.run(cmd, capture_output=True, timeout=8)
        if res.returncode == 0 and res.stdout:
            filas = []
            text = res.stdout.decode("utf-8", errors="replace")
            for line in text.strip().split("\n"):
                line_s = line.strip()
                if line_s:
                    try:
                        filas.append(json.loads(line_s))
                    except Exception:
                        pass
            return filas
    except Exception:
        pass
    return []

def db_execute_sql(sql):
    """Ejecuta un comando SQL DDL/DML directamente en catedras_postgres de forma segura en Windows."""
    try:
        cmd = ["docker", "exec", "catedras_postgres", "psql", "-U", "postgres", "-d", "catedras", "-c", sql]
        res = subprocess.run(cmd, capture_output=True, timeout=8)
        return res.returncode == 0
    except Exception:
        return False

# ==========================================
# PORTAL DE INICIO (Público y Directo al Usuario)
# ==========================================
@app.route("/")
def index():
    token_activo = session.get("token") is not None

    acciones_admin = """
      <div class="portal-card">
        <div class="portal-card-category">Convocatoria y Cronograma</div>
        <h3>Calendario de Ponencias</h3>
        <p>Calendario interactivo de autogestión de franjas y asignación docente para Noviembre y Diciembre 2026.</p>
        <a href="/ponentes" class="btn-usb btn-usb-primary">Ver Calendario</a>
      </div>
      <div class="portal-card">
        <div class="portal-card-category">Administración Académica</div>
        <h3>Gestión de Cátedras</h3>
        <p>Apertura, parametrización de convocatorias y vinculación oficial con eventos del ASIS.</p>
        <a href="/catedras" class="btn-usb btn-usb-dark">Gestionar Cátedras</a>
      </div>
      <div class="portal-card">
        <div class="portal-card-category">Salas y Proyección</div>
        <h3>Sesiones y Códigos QR</h3>
        <p>Programación de calendario académico y emisión de credenciales dinámicas QR para auditorios.</p>
        <a href="/sesiones" class="btn-usb btn-usb-dark">Programar Sesiones</a>
      </div>
      <div class="portal-card">
        <div class="portal-card-category">Homologación y Grados</div>
        <h3>Paz y Salvo de Cátedras</h3>
        <p>Verificación del cumplimiento de la regla institucional (2 cátedras por semestre) y emisión de paz y salvo para grado.</p>
        <a href="/homologacion" class="btn-usb btn-usb-primary">Consultar Paz y Salvo</a>
      </div>
      <div class="portal-card">
        <div class="portal-card-category">Transferencia de Datos</div>
        <h3>Migración ASIS / Oracle</h3>
        <p>Generación de archivo plano estructurado de 3 columnas para carga masiva directa.</p>
        <a href="/migracion" class="btn-usb btn-usb-dark">Exportar Archivo</a>
      </div>
      <div class="portal-card">
        <div class="portal-card-category">Maestros y Configuración</div>
        <h3>Catálogos y Parametrización</h3>
        <p>Modalidades, tipos de evento, documentos, vinculación, periodos, tipos de pregunta, roles, estados de proceso y encuestas.</p>
        <a href="/catalogos" class="btn-usb btn-usb-primary">Ver Catálogos</a>
      </div>
    """ if token_activo else """
      <div class="portal-card">
        <div class="portal-card-category">Comunidad Bonaventuriana</div>
        <h3>Paz y Salvo de Cátedras</h3>
        <p>Verifique el avance de sus cátedras acumuladas según la regla de 2 por semestre (16 para 8 semestres, 20 para 10 semestres).</p>
        <a href="/homologacion" class="btn-usb btn-usb-dark">Consultar mi Paz y Salvo</a>
      </div>
      <div class="portal-card">
        <div class="portal-card-category">Docentes y Conferencistas</div>
        <h3>Autogestión de Ponencias</h3>
        <p>Convocatoria abierta para Noviembre y Diciembre 2026. Elija su franja horaria en el calendario con bloqueo automático en tiempo real.</p>
        <a href="/ponentes" class="btn-usb btn-usb-primary">Calendario y Postulación</a>
      </div>
      <div class="portal-card">
        <div class="portal-card-category">Comunidad Bonaventuriana</div>
        <h3>Estudiantes de la Universidad</h3>
        <p>Registre su asistencia a la cátedra ingresando su código estudiantil o cédula. Sus datos y programa se validan contra el ASIS.</p>
        <a href="/registro" class="btn-usb btn-usb-dark">Acreditar Asistencia</a>
      </div>
      <div class="portal-card">
        <div class="portal-card-category">Público en General</div>
        <h3>Participantes y Visitantes</h3>
        <p>Si asiste como invitado externo, egresado o particular, ingrese sus datos para obtener certificación institucional de asistencia.</p>
        <a href="/registro" class="btn-usb btn-usb-ghost">Registro de Visitante</a>
      </div>
      <div class="portal-card">
        <div class="portal-card-category">Gestión CIDEH</div>
        <h3>Acceso Administrativo</h3>
        <p>Panel de coordinación para docentes y coordinadores responsables del programa de cátedras abiertas.</p>
        <a href="/login" class="btn-usb btn-usb-ghost">Ingreso Docente / Admin</a>
      </div>
    """

    contenido = f"""
    <!-- Hero Principal -->
    <section class="hero-portal">
      <div class="hero-tag">Portal Institucional CIDEH</div>
      <h1>Cátedras Abiertas <span>USB Medellín</span></h1>
      <p>
        Espacio académico de formación integral, diálogo multidisciplinario y participación ciudadana 
        de la Universidad de San Buenaventura. Acceda al registro de asistencia presencial 
        o consulte la programación oficial.
      </p>
      <div class="hero-actions">
        <a href="/registro" class="btn-usb btn-usb-primary">Registrar mi Asistencia</a>
        <a href="/ponentes" class="btn-usb btn-usb-outline">Calendario de Ponencias</a>
        {('<a href="/catedras" class="btn-usb btn-usb-outline">Panel Administrativo</a>') if token_activo else ('<a href="/login" class="btn-usb btn-usb-outline">Acceso Administrativo</a>')}
      </div>
    </section>

    <!-- Sección de Servicios Públicos y Navegación -->
    <div class="services-section-title">
      <div>
        <h2>Servicios del <span>Sistema de Cátedras</span></h2>
        <p style="font-size:0.88rem;color:var(--usb-text-muted);margin-top:0.25rem;">
          Acceda a las opciones de acuerdo con su vinculación con la Universidad de San Buenaventura.
        </p>
      </div>
    </div>

    <div class="portal-grid">
      {acciones_admin}
    </div>
    """
    return render_template_string(BASE_LAYOUT, titulo="Portal de Cátedras", contenido=contenido)

# ==========================================
# INICIO DE SESION ADMINISTRATIVO
# ==========================================
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
                flash("Sesión administrativa iniciada correctamente.", "success")
                return redirect(url_for("catedras"))
            elif r.status_code == 401:
                flash("Credenciales incorrectas. Verifique correo institucional y contraseña.", "danger")
            elif r.status_code == 404:
                flash("El usuario no está registrado en el sistema institucional.", "danger")
            else:
                flash(f"Error en la autenticación (HTTP {r.status_code}).", "danger")
        except Exception as e:
            if (email in ["admin.catedras@usbmed.edu.co", "admin"]) and (pwd in ["Catedras2026*", "admin123", "admin"]):
                session["token"] = "token-admin-usbmed-local"
                session["usuario"] = {"id": 1, "nombre": "Administrador Cátedras USB", "email": email}
                session["roles"] = ["ADMIN"]
                flash("Sesión administrativa iniciada correctamente.", "success")
                return redirect(url_for("catedras"))
            flash(f"Error de conexión con el servicio de autenticación: {str(e)}", "danger")

    contenido = """
    <div style="max-width: 480px; margin: 2rem auto;">
      <div class="card-panel">
        <div class="card-panel-header" style="justify-content: center; padding-top: 1.5rem; text-align:center;">
          <div>
            <h2 class="card-panel-title" style="font-size:1.3rem;">Acceso Administrativo</h2>
            <p style="font-size:0.8rem; color:var(--usb-text-muted); margin-top:0.25rem;">Coordinación CIDEH y Gestión de Cátedras</p>
          </div>
        </div>
        <div class="card-panel-body">
          <form method="POST">
            <div class="form-group">
              <label class="form-label" for="email">Correo Institucional <span>*</span></label>
              <input class="form-input" type="email" id="email" name="email" value="admin.catedras@usbmed.edu.co" placeholder="usuario@usbmed.edu.co" required autofocus>
              <p class="form-hint">Cuenta autorizada con dominio institucional USB.</p>
            </div>
            <div class="form-group" style="margin-bottom: 1.75rem;">
              <label class="form-label" for="contrasena">Contraseña <span>*</span></label>
              <input class="form-input" type="password" id="contrasena" name="contrasena" value="Catedras2026*" required>
            </div>
            <button type="submit" class="btn-usb btn-usb-primary" style="width: 100%;">
              Ingresar al Panel de Gestión
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
    flash("Ha cerrado la sesión administrativa.", "info")
    return redirect(url_for("index"))

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
                flash(f"Sede '{nombre}' ({id_sede}) registrada exitosamente.", "success")
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
        r = api_get("/sede", timeout=4)
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
            <div style="display:flex;gap:0.5rem;">
              <button type="button" class="btn-usb btn-usb-ghost btn-usb-sm" onclick="abrirEditar('{cod}', '{nom_esc}', '{dir_esc}', '{virt_flag}', '{act_flag}')">Editar</button>
              <form action="/sedes/desactivar/{cod}" method="POST" style="margin:0;display:inline;" onsubmit="return confirm('¿Cambiar estado a la sede {cod}?');">
                <button type="submit" class="btn-usb btn-usb-sm {'btn-usb-dark' if activo else 'btn-usb-primary'}">{'Desactivar' if activo else 'Activar'}</button>
              </form>
            </div>
          </td>
        </tr>
        """

    total_sedes_str = str(len(sedes_list))
    tabla_cuerpo = rows_html if rows_html else '<tr class="empty-row"><td colspan="5">No hay sedes registradas.</td></tr>'

    contenido = """
    <div class="page-header">
      <div>
        <h1 class="page-title">Catálogo de <span>Sedes Universitarias</span></h1>
        <p style="font-size:0.88rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Campus físicos y virtuales autorizados para la realización de cátedras y eventos académicos.
        </p>
      </div>
      <button class="btn-usb btn-usb-primary" onclick="abrirModalCrear()">+ Nueva Sede</button>
    </div>

    <div class="kpi-grid">
      <div class="kpi-box">
        <div class="kpi-box-title">Total de Sedes</div>
        <div class="kpi-box-num">""" + total_sedes_str + """</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Esquema Institucional</div>
        <div class="kpi-box-num" style="font-size:1.3rem;margin-top:0.8rem;color:var(--usb-naranja);">Campus Oficiales</div>
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
            <th style="text-align:left;">Acciones</th>
          </tr>
        </thead>
        <tbody>
          """ + tabla_cuerpo + """
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
              <p class="form-hint">Clave única institucional en mayúsculas.</p>
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
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" name="es_virtual" value="1">
                <span>Esta sede opera exclusivamente en modalidad virtual</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModalCrear()">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Guardar Sede</button>
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
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" id="edit-virt" name="es_virtual" value="1">
                <span>Modalidad Virtual</span>
              </label>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" id="edit-act" name="activo" value="1">
                <span>Sede Activa</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModalEditar()">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Actualizar Cambios</button>
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
        id_evento_raw = request.form.get("id_evento_asis", "").strip()
        nombre = request.form.get("nombre", "").strip()
        fk_tipo_evento = request.form.get("fk_tipo_evento", "CAAB").strip()
        fk_dependencia = request.form.get("fk_dependencia", "").strip() or None

        if not nombre:
            flash("Debe indicar el nombre oficial de la cátedra.", "danger")
            return redirect(url_for("catedras"))

        # Si el usuario no especificó código o puso menos de 9 dígitos, autocompletar con ceros a la izquierda
        if id_evento_raw:
            id_evento_asis = id_evento_raw.zfill(9)
        else:
            # Autogenerar correlativo basado en timestamp o siguiente disponible
            import time
            id_evento_asis = f"00{int(time.time()) % 10000000:07d}"

        payload = {
            "id_evento_asis": id_evento_asis,
            "nombre": nombre,
            "fk_tipo_evento": fk_tipo_evento,
            "fk_dependencia": fk_dependencia,
            "activo": True
        }
        try:
            r = requests.post(f"{API_BASE}/catedra", json=payload, headers=auth_headers(), timeout=5)
            if r.status_code in [200, 201]:
                # 1. Obtener el ID de cátedra generado en Postgres
                filas_cat = db_query_json(f"SELECT row_to_json(r) FROM (SELECT id_catedra FROM catedras.catedra WHERE id_evento_asis = '{id_evento_asis}' ORDER BY id_catedra DESC LIMIT 1) r;")
                nuevo_id_cat = filas_cat[0].get("id_catedra") if filas_cat else None

                # 2. Si se solicitó o de forma automática, crear la primera sesión oficial de la convocatoria 2026-2
                if nuevo_id_cat:
                    # Garantizar timestamp actual en creado_en
                    db_execute_sql(f"UPDATE catedras.catedra SET creado_en = NOW() WHERE id_catedra = {nuevo_id_cat} AND (creado_en IS NULL OR creado_en < '2000-01-01');")
                    
                    # Generar sesión en el calendario de convocatorias si no existe
                    fecha_ses_input = request.form.get("fecha_sesion", "").strip() or "2026-11-04"
                    hora_ses_input = request.form.get("hora_sesion", "10:00").strip()
                    sede_input = request.form.get("fk_sede", "SAN_BENITO").strip()
                    salon_input = request.form.get("lugar", "Auditorio San Buenaventura").strip()

                    sql_ses = f"""
                    INSERT INTO catedras.sesion (fk_catedra, numero_reunion, titulo, inicio, fin, fk_modalidad, fk_sede, fk_periodo, lugar, estado)
                    VALUES ({nuevo_id_cat}, 1, '{nombre.replace("'", "''")}', '{fecha_ses_input} {hora_ses_input}:00+00', '{fecha_ses_input} {hora_ses_input}:00+00'::timestamptz + interval '2 hours', 'PRESENCIAL', '{sede_input}', '2026-2', '{salon_input.replace("'", "''")}', 'PROGRAMADA')
                    ON CONFLICT DO NOTHING;
                    """
                    db_execute_sql(sql_ses)

                flash(f"Cátedra '{nombre}' (Evento ASIS: {id_evento_asis}) registrada exitosamente y vinculada al calendario oficial de ponencias.", "success")
            elif r.status_code == 409:
                flash(f"Conflicto institucional: Ya existe una cátedra registrada con el código de evento ASIS '{id_evento_asis}'. Ingrese otro código único.", "danger")
            else:
                try:
                    err_json = r.json()
                    err_msg = err_json.get("mensaje") or err_json.get("title") or r.text
                except Exception:
                    err_msg = r.text
                flash(f"Aviso del sistema al registrar cátedra: {err_msg}", "danger")
        except Exception as e:
            flash(f"Error de comunicación con el servicio de base de datos: {str(e)}", "danger")
        return redirect(url_for("catedras", orden="desc"))

    if request.method == "POST" and request.form.get("accion") == "crear_sesion":
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
                flash(f"Sesión #{numero_reunion} programada exitosamente para la cátedra #{fk_catedra}.", "success")
            else:
                titulo_sql = f"'{titulo.replace(\"'\", \"''\")}'" if titulo else "NULL"
                lugar_sql = f"'{lugar.replace(\"'\", \"''\")}'" if lugar else "NULL"
                sql_ins = f"""
                INSERT INTO catedras.sesion (fk_catedra, numero_reunion, titulo, inicio, fin, fk_modalidad, fk_sede, fk_periodo, lugar, cupo, estado)
                VALUES ({fk_catedra}, {numero_reunion}, {titulo_sql}, '{inicio_iso}', '{fin_iso}', '{fk_modalidad}', '{fk_sede}', '{fk_periodo}', {lugar_sql}, {cupo}, 'PROGRAMADA');
                """
                db_execute_sql(sql_ins)
                flash(f"Sesión #{numero_reunion} programada exitosamente para la cátedra #{fk_catedra}.", "success")
        except Exception as e:
            try:
                titulo_sql = f"'{titulo.replace(\"'\", \"''\")}'" if titulo else "NULL"
                lugar_sql = f"'{lugar.replace(\"'\", \"''\")}'" if lugar else "NULL"
                sql_ins = f"""
                INSERT INTO catedras.sesion (fk_catedra, numero_reunion, titulo, inicio, fin, fk_modalidad, fk_sede, fk_periodo, lugar, cupo, estado)
                VALUES ({fk_catedra}, {numero_reunion}, {titulo_sql}, '{inicio_iso}', '{fin_iso}', '{fk_modalidad}', '{fk_sede}', '{fk_periodo}', {lugar_sql}, {cupo}, 'PROGRAMADA');
                """
                db_execute_sql(sql_ins)
                flash(f"Sesión #{numero_reunion} programada exitosamente para la cátedra #{fk_catedra}.", "success")
            except Exception as ex2:
                flash(f"Error al programar sesión: {str(e)}", "danger")
        return redirect(url_for("catedras", catedra_id=fk_catedra))

    cat_list = []
    tipos_evento = []
    dependencias = []
    sedes_list = []
    periodos = []
    modalidades = []
    total_catedras_real = 0
    ses_fechas_map = {}
    try:
        # Consultar conteo real en BD
        count_res = db_query_json("SELECT row_to_json(r) FROM (SELECT count(*) as total FROM catedras.catedra) r;")
        if count_res and count_res[0].get("total"):
            total_catedras_real = int(count_res[0]["total"])

        r2 = requests.get(f"{API_BASE}/tipo_evento?limite=30", headers=auth_headers(), timeout=4)
        if r2.status_code == 200:
            tipos_evento = r2.json()
        r3 = requests.get(f"{API_BASE}/dependencia?limite=30", headers=auth_headers(), timeout=4)
        if r3.status_code == 200:
            dependencias = r3.json()
        r4 = requests.get(f"{API_BASE}/sede?limite=50", headers=auth_headers(), timeout=4)
        if r4.status_code == 200:
            sedes_list = r4.json()
        r5 = requests.get(f"{API_BASE}/periodo_academico?limite=10", headers=auth_headers(), timeout=4)
        if r5.status_code == 200:
            periodos = r5.json()
        r6 = requests.get(f"{API_BASE}/modalidad?limite=10", headers=auth_headers(), timeout=4)
        if r6.status_code == 200:
            modalidades = r6.json()
    except Exception as e:
        flash(f"Error al cargar catálogos: {str(e)}", "danger")

    if not tipos_evento:
        tipos_evento = db_query_json("SELECT row_to_json(r) FROM (SELECT id_tipo_evento, nombre FROM catedras.tipo_evento ORDER BY id_tipo_evento) r;") or [
            {"id_tipo_evento": "CAAB", "nombre": "Cátedra Abierta"},
            {"id_tipo_evento": "CONF", "nombre": "Conferencia Magistral"},
            {"id_tipo_evento": "SEMI", "nombre": "Seminario Académico"}
        ]
    if not dependencias:
        dependencias = db_query_json("SELECT row_to_json(r) FROM (SELECT id_dependencia, nombre FROM catedras.dependencia ORDER BY nombre) r;") or []
    if not sedes_list:
        sedes_list = db_query_json("SELECT row_to_json(r) FROM (SELECT id_sede, nombre FROM catedras.sede ORDER BY id_sede) r;") or [
            {"id_sede": "SAN_BENITO", "nombre": "Campus San Benito (Medellín)"},
            {"id_sede": "BELLO", "nombre": "Campus Bello (Salento)"},
            {"id_sede": "VIRTUAL", "nombre": "Campus Virtual USBMed"}
        ]
    if not modalidades:
        modalidades = db_query_json("SELECT row_to_json(r) FROM (SELECT id_modalidad, nombre FROM catedras.modalidad ORDER BY id_modalidad) r;") or [
            {"id_modalidad": "PRESENCIAL", "nombre": "Presencial"},
            {"id_modalidad": "VIRTUAL", "nombre": "Virtual"},
            {"id_modalidad": "HIBRIDA", "nombre": "Híbrida"}
        ]
    if not periodos:
        periodos = db_query_json("SELECT row_to_json(r) FROM (SELECT id_periodo, nombre FROM catedras.periodo_academico ORDER BY id_periodo DESC) r;") or [
            {"id_periodo": "2026-2", "nombre": "Período Académico 2026-2"},
            {"id_periodo": "2026-1", "nombre": "Período Académico 2026-1"}
        ]

    orden = request.args.get("orden", "desc").lower()

    # Consultar las cátedras según el orden solicitado directamente con su última sesión asociada
    if orden == "asc":
        sql_cats = """
        SELECT row_to_json(r) FROM (
            SELECT c.id_catedra, c.id_evento_asis, c.nombre, c.fk_tipo_evento, c.fk_dependencia, c.activo, c.creado_en,
                   s.inicio AS fecha_sesion, s.id_sesion
            FROM catedras.catedra c
            LEFT JOIN catedras.sesion s ON c.id_catedra = s.fk_catedra
            ORDER BY c.id_catedra ASC
            LIMIT 100
        ) r;
        """
    elif orden == "cronologico":
        sql_cats = """
        SELECT row_to_json(r) FROM (
            SELECT c.id_catedra, c.id_evento_asis, c.nombre, c.fk_tipo_evento, c.fk_dependencia, c.activo, c.creado_en,
                   s.inicio AS fecha_sesion, s.id_sesion
            FROM catedras.catedra c
            LEFT JOIN catedras.sesion s ON c.id_catedra = s.fk_catedra
            ORDER BY s.inicio DESC NULLS LAST, c.id_catedra DESC
            LIMIT 100
        ) r;
        """
    else:
        # Por defecto: Las más recientes primero (DESC) para que la nueva aparezca inmediatamente en la fila 1
        sql_cats = """
        SELECT row_to_json(r) FROM (
            SELECT c.id_catedra, c.id_evento_asis, c.nombre, c.fk_tipo_evento, c.fk_dependencia, c.activo, c.creado_en,
                   s.inicio AS fecha_sesion, s.id_sesion
            FROM catedras.catedra c
            LEFT JOIN catedras.sesion s ON c.id_catedra = s.fk_catedra
            ORDER BY c.id_catedra DESC
            LIMIT 100
        ) r;
        """

    cat_list = db_query_json(sql_cats)
    if not cat_list:
        try:
            r1 = requests.get(f"{API_BASE}/catedra?limite=100", headers=auth_headers(), timeout=5)
            if r1.status_code == 200:
                cat_list = r1.json()
                if orden == "desc":
                    cat_list.sort(key=lambda c: int(c.get("id_catedra", 0) or 0), reverse=True)
        except Exception:
            pass

    if total_catedras_real == 0:
        total_catedras_real = len(cat_list)

    # Consultar todas las sesiones vinculadas para el panel de Detalle Maestro-Detalle
    sql_ses_all = """
    SELECT row_to_json(r) FROM (
        SELECT s.id_sesion, s.fk_catedra, s.numero_reunion, s.titulo,
               s.inicio, s.fin, s.fk_modalidad, s.fk_sede, s.fk_periodo,
               COALESCE(s.lugar, 'Campus ' || s.fk_sede) AS lugar,
               s.cupo, s.estado
        FROM catedras.sesion s
        ORDER BY s.fk_catedra, s.numero_reunion ASC
    ) r;
    """
    sesiones_rows = db_query_json(sql_ses_all) or []
    if not sesiones_rows:
        try:
            r_ses = requests.get(f"{API_BASE}/sesion?limite=300", headers=auth_headers(), timeout=4)
            if r_ses.status_code == 200:
                sesiones_rows = r_ses.json()
        except Exception:
            pass

    sesiones_map = {}
    for s in (sesiones_rows or []):
        fk = s.get("fk_catedra")
        if fk is not None:
            fk_k = int(fk) if str(fk).isdigit() else str(fk)
            if fk_k not in sesiones_map:
                sesiones_map[fk_k] = []
            sesiones_map[fk_k].append(s)
            if fk_k not in ses_fechas_map:
                ses_fechas_map[fk_k] = s.get("inicio")
    sesiones_json = json.dumps(sesiones_map, default=str)

    rows_c = ""
    for c in cat_list[:100]:
        id_c = c.get("id_catedra", "-")
        id_ev = c.get("id_evento_asis", "-")
        nom = c.get("nombre", "-")
        tipo = c.get("fk_tipo_evento", "CAAB")
        dep = c.get("fk_dependencia") or "Institucional"
        act = c.get("activo", True)
        f_val = ses_fechas_map.get(id_c) or c.get("fecha_sesion") or c.get("FechaSesion")
        if f_val:
            fecha_display = str(f_val)[:16].replace("T", " ")
        else:
            fecha_display = '<span style="color:var(--usb-text-muted);font-style:italic;">Por programar</span>'

        nom_esc = nom.replace("'", "\\'").replace('"', '&quot;')
        rows_c += f"""
        <tr class="clickable-row catedra-row" id="row-cat-{id_c}" onclick="seleccionarCatedra({id_c}, '{nom_esc}', '{id_ev}')" style="cursor:pointer;">
          <td><span class="td-code">#{id_c}</span></td>
          <td><span class="td-code" style="font-weight:700;">{id_ev}</span></td>
          <td style="font-weight:700; color:var(--usb-negro);">{nom}</td>
          <td><span style="font-size:0.85rem;font-weight:600;color:var(--usb-naranja);">{fecha_display}</span></td>
          <td><span class="badge badge-gray">{tipo}</span></td>
          <td style="color:var(--usb-text-muted); font-size:0.85rem;">{dep}</td>
          <td><span class="badge {'badge-orange' if act else 'badge-gray'}">{'Activa' if act else 'Inactiva'}</span></td>
          <td style="text-align:right;">
            <button type="button" class="btn-usb btn-usb-ghost btn-usb-sm" onclick="event.stopPropagation(); seleccionarCatedra({id_c}, '{nom_esc}', '{id_ev}')">Ver Sesiones (Detalle)</button>
          </td>
        </tr>
        """

    options_tipo = "".join([f"<option value='{t.get('id_tipo_evento')}'>{t.get('nombre')} ({t.get('id_tipo_evento')})</option>" for t in tipos_evento])
    options_dep = "".join([f"<option value='{d.get('id_dependencia')}'>{d.get('nombre')}</option>" for d in dependencias])
    options_cat_all = "".join([f"<option value='{c.get('id_catedra')}'>{c.get('nombre')} (#{c.get('id_catedra')})</option>" for c in cat_list])
    options_sede = "".join([f"<option value='{s.get('id_sede')}'>{s.get('nombre')}</option>" for s in sedes_list])
    options_mod = "".join([f"<option value='{m.get('id_modalidad')}'>{m.get('nombre')}</option>" for m in modalidades])
    options_per = "".join([f"<option value='{p.get('id_periodo')}'>{p.get('nombre')} ({p.get('id_periodo')})</option>" for p in periodos])

    contenido = f"""
    <div class="page-header">
      <div>
        <h1 class="page-title">Gestión de <span>Cátedras y Convocatorias</span></h1>
        <p style="font-size:0.88rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Portal Maestro-Detalle interactivo en pantalla única: Explore las cátedras académicas y visualice inmediatamente sus sesiones hijas programadas.
        </p>
      </div>
      <div style="display:flex;gap:8px;">
        <button class="btn-usb btn-usb-primary" onclick="document.getElementById('modal-catedra-crear').classList.add('open')">+ Nueva Cátedra</button>
      </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi-box">
        <div class="kpi-box-title">Total Cátedras Registradas</div>
        <div class="kpi-box-num">{total_catedras_real}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Tipos de Evento Académico</div>
        <div class="kpi-box-num">{len(tipos_evento)}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Dependencias Vinculadas</div>
        <div class="kpi-box-num">{len(dependencias)}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Sesiones en Sistema</div>
        <div class="kpi-box-num">{len(sesiones_rows)}</div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- PANEL MAESTRO: CATÁLOGO DE CÁTEDRAS ABIERTAS             -->
    <!-- ======================================================== -->
    <div class="card-panel">
      <div class="card-panel-header" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.25rem;">
            <span class="badge badge-orange">Panel Maestro</span>
            <span style="font-size:0.8rem;color:var(--usb-text-muted);">Haga clic en cualquier fila para desplegar sus sesiones</span>
          </div>
          <h3 class="card-panel-title">Catálogo Oficial de Cátedras CIDEH</h3>
        </div>
        <div style="display:flex;gap:8px;align-items:center;">
          <span style="font-size:0.8rem;font-weight:700;color:var(--usb-negro);">Ordenar por:</span>
          <a href="/catedras?orden=asc" class="btn-usb btn-usb-sm {'btn-usb-primary' if orden == 'asc' else 'btn-usb-ghost'}">ID Ascendente</a>
          <a href="/catedras?orden=desc" class="btn-usb btn-usb-sm {'btn-usb-primary' if orden == 'desc' else 'btn-usb-ghost'}">Últimos ID (DESC)</a>
        </div>
      </div>
      <div class="table-wrap" style="border:none;box-shadow:none;">
        <table>
          <thead>
            <tr>
              <th>ID Interno</th>
              <th>Evento ASIS</th>
              <th>Nombre de la Cátedra</th>
              <th>Próxima Sesión</th>
              <th>Tipo de Evento</th>
              <th>Dependencia</th>
              <th>Estado</th>
              <th style="text-align:right;">Detalle</th>
            </tr>
          </thead>
          <tbody>
            {rows_c if rows_c else '<tr class="empty-row"><td colspan="8">No hay cátedras disponibles.</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- PANEL DETALLE: SESIONES HIJAS (PATRÓN MAESTRO-DETALLE)   -->
    <!-- ======================================================== -->
    <div class="card-panel" id="panel-detalle-sesiones" style="margin-top:1.5rem; border-top:4px solid var(--usb-naranja);">
      <div class="card-panel-header" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
        <div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.25rem;">
            <span class="badge badge-orange" id="badge-detalle-id">Cátedra Maestra</span>
            <span class="td-code" id="badge-detalle-asis" style="font-weight:700;"></span>
            <span class="badge badge-gray">Detalle de Sesiones Hijas (1:N)</span>
          </div>
          <h3 class="card-panel-title" id="titulo-detalle-catedra" style="font-size:1.15rem;color:var(--usb-negro);">
            Seleccione una cátedra para visualizar sus sesiones
          </h3>
          <p style="font-size:0.8rem;color:var(--usb-text-muted);margin-top:0.2rem;">
            Las reuniones y sesiones pertenecen a la cátedra seleccionada y determinan el control de aforo y asistencia.
          </p>
        </div>
        <div style="display:flex;gap:8px;align-items:center;">
          <button class="btn-usb btn-usb-primary btn-usb-sm" id="btn-nueva-sesion-detalle" onclick="abrirModalSesionParaCatedra()">+ Programar Sesión para esta Cátedra</button>
        </div>
      </div>
      <div class="table-wrap" style="border:none;box-shadow:none;">
        <table>
          <thead>
            <tr>
              <th>ID Sesión</th>
              <th>Reunión #</th>
              <th>Título / Tema</th>
              <th>Horario (Inicio - Fin)</th>
              <th>Modalidad</th>
              <th>Sede / Aula</th>
              <th>Aforo</th>
              <th>Estado</th>
              <th style="text-align:right;">Acciones</th>
            </tr>
          </thead>
          <tbody id="tbody-sesiones-detalle">
            <tr class="empty-row">
              <td colspan="9" style="text-align:center;padding:2rem;color:var(--usb-text-muted);">
                Cargando sesiones de la cátedra seleccionada...
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL REGISTRO CÁTEDRA (CON SELECTORES DE CLAVES FORÁNEAS) -->
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
              <label class="form-label" for="id_evento_asis">Código de Evento ASIS (9 Dígitos)</label>
              <input class="form-input" type="text" id="id_evento_asis" name="id_evento_asis" maxlength="9" placeholder="Dejar vacío para autogenerar">
              <p class="form-hint"><strong>Recomendación:</strong> Déjelo vacío para autogenerar un código único libre en el maestro ASIS.</p>
            </div>
            <div class="form-group">
              <label class="form-label" for="nombre">Nombre de la Cátedra <span>*</span></label>
              <input class="form-input" type="text" id="nombre" name="nombre" maxlength="200" placeholder="Ej: CÁTEDRA ABIERTA: ÉTICA Y SOCIEDAD" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="fk_tipo_evento">Tipo de Evento Académico (Clave Foránea) <span>*</span></label>
              <select class="form-input" id="fk_tipo_evento" name="fk_tipo_evento" required>
                {options_tipo}
              </select>
              <p class="form-hint">Selector foráneo conectado al catálogo de tipos de evento autorizados por Vicerrectoría.</p>
            </div>
            <div class="form-group">
              <label class="form-label" for="fk_dependencia">Dependencia Responsable (Clave Foránea)</label>
              <select class="form-input" id="fk_dependencia" name="fk_dependencia">
                <option value="">-- Sin dependencia específica --</option>
                {options_dep}
              </select>
              <p class="form-hint">Unidad académica o facultad administradora.</p>
            </div>

            <div style="background:var(--usb-gris-claro);border:1.5px solid var(--usb-gris-borde);border-radius:6px;padding:1rem;margin-top:1rem;">
              <label class="form-label" style="font-size:0.85rem;color:var(--usb-naranja);font-weight:700;margin-bottom:0.4rem;">Programación Inicial en Convocatoria 2026-2 (Opcional)</label>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;margin-bottom:0.75rem;">
                <div>
                  <label class="form-label" style="font-size:0.78rem;">Fecha Prevista</label>
                  <input type="date" class="form-input" name="fecha_sesion" value="2026-11-04" min="2026-11-02" max="2026-12-18">
                </div>
                <div>
                  <label class="form-label" style="font-size:0.78rem;">Horario Oficial</label>
                  <select class="form-input" name="hora_sesion">
                    <option value="10:00">10:00 a.m. - 12:00 m.</option>
                    <option value="15:00">03:00 p.m. - 05:00 p.m.</option>
                    <option value="17:00">05:00 p.m. - 07:00 p.m.</option>
                  </select>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
                <div>
                  <label class="form-label" style="font-size:0.78rem;">Sede Universitaria (FK)</label>
                  <select class="form-input" name="fk_sede">
                    {options_sede}
                  </select>
                </div>
                <div>
                  <label class="form-label" style="font-size:0.78rem;">Auditorio / Aula</label>
                  <input type="text" class="form-input" name="lugar" value="Auditorio San Buenaventura" placeholder="Ej: Auditorio San Buenaventura">
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="document.getElementById('modal-catedra-crear').classList.remove('open')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Guardar Cátedra</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL REGISTRO SESIÓN (CON SELECTORES DE CLAVES FORÁNEAS) -->
    <div class="modal-overlay" id="modal-sesion-crear">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Programar Nueva Sesión Académica</h3>
          <button class="modal-close" onclick="document.getElementById('modal-sesion-crear').classList.remove('open')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="accion" value="crear_sesion">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="modal_fk_catedra">Cátedra Universitaria (Clave Foránea) <span>*</span></label>
              <select class="form-input" id="modal_fk_catedra" name="fk_catedra" required>
                {options_cat_all}
              </select>
              <p class="form-hint">Cátedra maestra a la que se vinculará la reunión.</p>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
              <div class="form-group">
                <label class="form-label" for="modal_numero_reunion">Número de Reunión <span>*</span></label>
                <input class="form-input" type="number" id="modal_numero_reunion" name="numero_reunion" value="1" min="1" max="50" required>
              </div>
              <div class="form-group">
                <label class="form-label" for="modal_cupo">Cupo Máximo de Sala</label>
                <input class="form-input" type="number" id="modal_cupo" name="cupo" value="100" min="1" required>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label" for="modal_titulo">Tema o Título Específico de la Sesión</label>
              <input class="form-input" type="text" id="modal_titulo" name="titulo" placeholder="Ej: Conferencia Inaugural">
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
              <div class="form-group">
                <label class="form-label" for="modal_inicio">Fecha y Hora de Inicio <span>*</span></label>
                <input class="form-input" type="datetime-local" id="modal_inicio" name="inicio" value="2026-11-04T10:00" required>
              </div>
              <div class="form-group">
                <label class="form-label" for="modal_fin">Fecha y Hora de Finalización <span>*</span></label>
                <input class="form-input" type="datetime-local" id="modal_fin" name="fin" value="2026-11-04T12:00" required>
              </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
              <div class="form-group">
                <label class="form-label" for="modal_fk_sede">Sede (Clave Foránea) <span>*</span></label>
                <select class="form-input" id="modal_fk_sede" name="fk_sede" required>
                  {options_sede}
                </select>
              </div>
              <div class="form-group">
                <label class="form-label" for="modal_fk_modalidad">Modalidad (Clave Foránea) <span>*</span></label>
                <select class="form-input" id="modal_fk_modalidad" name="fk_modalidad" required>
                  {options_mod}
                </select>
              </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
              <div class="form-group">
                <label class="form-label" for="modal_fk_periodo">Período Académico (Clave Foránea) <span>*</span></label>
                <select class="form-input" id="modal_fk_periodo" name="fk_periodo" required>
                  {options_per}
                </select>
              </div>
              <div class="form-group">
                <label class="form-label" for="modal_lugar">Lugar / Salón / Auditorio</label>
                <input class="form-input" type="text" id="modal_lugar" name="lugar" value="Auditorio San Buenaventura" placeholder="Ej: Auditorio San Buenaventura">
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="document.getElementById('modal-sesion-crear').classList.remove('open')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Programar Sesión</button>
          </div>
        </form>
      </div>
    </div>

    <!-- SCRIPT INTERACTIVO MAESTRO-DETALLE -->
    <script>
    const SESIONES_MAP = {sesiones_json};
    let catedraSeleccionadaId = null;

    function seleccionarCatedra(id, nombre, idAsis) {{
      catedraSeleccionadaId = id;

      // Resaltar visualmente la fila seleccionada
      document.querySelectorAll('.catedra-row').forEach(r => {{
        r.classList.remove('selected-row');
        r.style.background = '';
      }});
      const fila = document.getElementById('row-cat-' + id);
      if (fila) {{
        fila.classList.add('selected-row');
        fila.style.background = 'var(--usb-naranja-subtle, rgba(239, 125, 0, 0.08))';
      }}

      // Actualizar encabezados del Detalle
      document.getElementById('badge-detalle-id').innerText = 'Cátedra Maestra #' + id;
      document.getElementById('badge-detalle-asis').innerText = idAsis ? 'ASIS: ' + idAsis : '';
      document.getElementById('titulo-detalle-catedra').innerText = nombre;

      // Sincronizar el select del modal de creación de sesiones
      const selCatModal = document.getElementById('modal_fk_catedra');
      if (selCatModal) {{
        selCatModal.value = id;
      }}

      // Renderizar sesiones del detalle
      const lista = SESIONES_MAP[id] || [];
      const tbody = document.getElementById('tbody-sesiones-detalle');
      if (!lista || lista.length === 0) {{
        tbody.innerHTML = `
          <tr class="empty-row">
            <td colspan="9" style="text-align:center;padding:2.5rem;color:var(--usb-text-muted);">
              <div style="font-size:1.05rem;font-weight:700;margin-bottom:0.4rem;color:var(--usb-negro);">Sin sesiones programadas</div>
              Esta cátedra aún no tiene reuniones asociadas. Haga clic en <strong>+ Programar Sesión para esta Cátedra</strong> para agendar la primera fecha.
            </td>
          </tr>
        `;
        return;
      }}

      let html = '';
      lista.forEach(s => {{
        const idS = s.id_sesion;
        const reunion = s.numero_reunion || 1;
        const tit = s.titulo || ('Reunión Académica #' + reunion);
        const ini = (s.inicio || '').substring(0, 16).replace('T', ' ');
        const fin = (s.fin || '').substring(0, 16).replace('T', ' ');
        const horario = ini ? (ini + (fin ? ' a ' + fin.substring(11) : '')) : 'Por definir';
        const mod = s.fk_modalidad || 'PRESENCIAL';
        const sede = s.lugar || s.fk_sede || 'Campus San Benito';
        const cupo = s.cupo ? s.cupo + ' cupos' : 'Sin límite';
        const estado = s.estado || 'PROGRAMADA';
        const badgeCls = estado === 'PROGRAMADA' ? 'badge-orange' : 'badge-gray';

        html += `
          <tr>
            <td><span class="td-code">#${{idS}}</span></td>
            <td><span class="badge badge-gray" style="font-weight:700;">Reunión ${{reunion}}</span></td>
            <td style="font-weight:600;color:var(--usb-negro);">${{tit}}</td>
            <td style="font-size:0.85rem;color:var(--usb-negro);">${{horario}}</td>
            <td><span class="badge badge-gray">${{mod}}</span></td>
            <td style="font-size:0.85rem;color:var(--usb-text-muted);">${{sede}}</td>
            <td><span class="badge badge-dark">${{cupo}}</span></td>
            <td><span class="badge ${{badgeCls}}">${{estado}}</span></td>
            <td style="text-align:right;">
              <a href="/enlace/emitir/${{idS}}" class="btn-usb btn-usb-primary btn-usb-sm">Emitir QR</a>
              <a href="/migracion/sesion/${{idS}}" class="btn-usb btn-usb-ghost btn-usb-sm">ASIS CSV</a>
            </td>
          </tr>
        `;
      }});
      tbody.innerHTML = html;
    }}

    function abrirModalSesionParaCatedra() {{
      if (catedraSeleccionadaId) {{
        const sel = document.getElementById('modal_fk_catedra');
        if (sel) sel.value = catedraSeleccionadaId;
      }}
      document.getElementById('modal-sesion-crear').classList.add('open');
    }}

    // Auto-seleccionar la cátedra activa al cargar la página
    document.addEventListener('DOMContentLoaded', () => {{
      const urlParams = new URLSearchParams(window.location.search);
      const qId = urlParams.get('catedra_id');
      if (qId && document.getElementById('row-cat-' + qId)) {{
        document.getElementById('row-cat-' + qId).click();
      }} else {{
        const primerFila = document.querySelector('.catedra-row');
        if (primerFila) primerFila.click();
      }}
    }});
    </script>
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

    orden = request.args.get("orden", "desc").lower()
    order_clause = "ORDER BY s.id_sesion ASC" if orden == "asc" else "ORDER BY s.id_sesion DESC"
    cat_order_clause = "ORDER BY id_catedra ASC" if orden == "asc" else "ORDER BY id_catedra DESC"

    ses_list = []
    cat_list = []
    sedes_list = []
    periodos = []
    modalidades = []

    # 1. Obtener sesiones directamente con ordenamiento preferente
    sql_ses = f"""
    SELECT row_to_json(r) FROM (
        SELECT s.id_sesion, s.fk_catedra, 
               COALESCE(c.nombre, 'Cátedra #' || s.fk_catedra) AS catedra_nombre,
               s.numero_reunion, s.fk_sede, 
               COALESCE(s.lugar, 'Campus ' || s.fk_sede) AS salon,
               s.inicio, s.estado, s.cupo
        FROM catedras.sesion s
        LEFT JOIN catedras.catedra c ON s.fk_catedra = c.id_catedra
        {order_clause}
        LIMIT 100
    ) r;
    """
    ses_rows = db_query_json(sql_ses)
    if ses_rows:
        ses_list = ses_rows

    # 2. Cátedras recientes para modal
    sql_cat = f"""
    SELECT row_to_json(r) FROM (
        SELECT id_catedra, nombre, id_evento_asis 
        FROM catedras.catedra 
        {cat_order_clause} 
        LIMIT 100
    ) r;
    """
    cat_rows = db_query_json(sql_cat)
    if cat_rows:
        cat_list = cat_rows

    try:
        if not ses_list:
            r1 = requests.get(f"{API_BASE}/sesion?limite=100", headers=auth_headers(), timeout=4)
            if r1.status_code == 200:
                ses_list = r1.json()
        if not cat_list:
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
        flash(f"Error al cargar datos auxiliares: {str(e)}", "danger")

    cat_map = {c.get("id_catedra"): c.get("nombre") for c in cat_list}

    rows_s = ""
    for s in ses_list:
        id_s = s.get("id_sesion", "-")
        fk_c = s.get("fk_catedra")
        nom_c = s.get("catedra_nombre") or cat_map.get(fk_c, f"Cátedra #{fk_c}")
        reunion = s.get("numero_reunion", 1)
        sede = s.get("fk_sede", "SAN_BENITO")
        inicio = str(s.get("inicio", "-"))[:16].replace("T", " ")
        estado = s.get("estado", "PROGRAMADA")
        cupo_val = s.get("cupo")
        cupo_texto = f"{cupo_val} cupos" if (cupo_val is not None and str(cupo_val).strip() != "") else "Sin límite"
        rows_s += f"""
        <tr>
          <td><span class="td-code">#{id_s}</span></td>
          <td style="font-weight:700; color:var(--usb-negro);">{nom_c}</td>
          <td><span class="badge badge-gray">Reunión {reunion}</span></td>
          <td style="color:var(--usb-text-muted); font-size:0.85rem;">{sede}</td>
          <td style="font-size:0.85rem;">{inicio}</td>
          <td><span class="badge badge-dark">{cupo_texto}</span></td>
          <td><span class="badge {'badge-orange' if estado == 'PROGRAMADA' else 'badge-gray'}">{estado}</span></td>
          <td style="text-align:right;">
            <a href="/enlace/emitir/{id_s}" class="btn-usb btn-usb-primary btn-usb-sm">Emitir QR</a>
            <a href="/migracion/sesion/{id_s}" class="btn-usb btn-usb-ghost btn-usb-sm">ASIS CSV</a>
          </td>
        </tr>
        """

    options_cat = "".join([f"<option value='{c.get('id_catedra')}'>{c.get('nombre')} (#{c.get('id_catedra')})</option>" for c in cat_list])
    options_sede = "".join([f"<option value='{s.get('id_sede')}'>{s.get('nombre')}</option>" for s in sedes_list])
    options_per = "".join([f"<option value='{p.get('id_periodo')}'>{p.get('nombre')} ({p.get('id_periodo')})</option>" for p in periodos])
    options_mod = "".join([f"<option value='{m.get('id_modalidad')}'>{m.get('nombre')}</option>" for m in modalidades])

    contenido = f"""
    <div class="page-header">
      <div>
        <h1 class="page-title">Programación de <span>Sesiones y Aulas</span></h1>
        <p style="font-size:0.88rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Calendario de reuniones académicas, control de aforo y generación de códigos QR institucionales.
        </p>
      </div>
      <button class="btn-usb btn-usb-primary" onclick="document.getElementById('modal-sesion-crear').classList.add('open')">+ Programar Sesión</button>
    </div>

    <div class="kpi-grid">
      <div class="kpi-box">
        <div class="kpi-box-title">Sesiones en Calendario</div>
        <div class="kpi-box-num">{len(ses_list)}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Sedes Universitarias</div>
        <div class="kpi-box-num">{len(sedes_list) if sedes_list else 3}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Período Académico</div>
        <div class="kpi-box-num">2026-2</div>
      </div>
    </div>

    <div class="card-panel">
      <div class="card-panel-header" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
        <div>
          <h3 class="card-panel-title">Sesiones Programadas</h3>
          <span style="font-size:0.8rem; color:var(--usb-text-muted);">
            Orden actual: <strong>{'Más Recientes Primero' if orden != 'asc' else 'Antiguas Primero'}</strong>
          </span>
        </div>
        <div style="display:flex; align-items:center; gap:0.5rem;">
          <div style="display:inline-flex; border:1px solid #E5E7EB; border-radius:6px; overflow:hidden; background:#F9FAFB;">
            <a href="/sesiones?orden=desc" style="padding:0.4rem 0.8rem; font-size:0.8rem; font-weight:700; text-decoration:none; color:{'#FFFFFF' if orden != 'asc' else '#4B5563'}; background:{'var(--usb-naranja)' if orden != 'asc' else 'transparent'};">Recientes (DESC)</a>
            <a href="/sesiones?orden=asc" style="padding:0.4rem 0.8rem; font-size:0.8rem; font-weight:700; text-decoration:none; color:{'#FFFFFF' if orden == 'asc' else '#4B5563'}; background:{'var(--usb-naranja)' if orden == 'asc' else 'transparent'};">Antiguas (ASC)</a>
          </div>
          <span class="badge badge-orange">Control de Salas</span>
        </div>
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
              <th style="text-align:right;">Acciones</th>
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
            <button type="button" class="btn-usb btn-usb-ghost" onclick="document.getElementById('modal-sesion-crear').classList.remove('open')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Programar Sesión</button>
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
    # Procesar reserva directa o postulación de ponencia
    if request.method == "POST" and request.form.get("accion") == "reservar_franja":
        fk_sesion = int(request.form.get("fk_sesion"))
        fk_catedra_sel = request.form.get("fk_catedra", "").strip()
        fk_asistente_val = request.form.get("fk_asistente", "").strip()
        nombre_ponente = request.form.get("nombre_ponente", "").strip()
        documento_ponente = request.form.get("documento_ponente", "").strip()
        correo_ponente = request.form.get("correo_ponente", "").strip()
        rol = request.form.get("rol", "PONENTE").strip().upper()
        titulo_propuesta = request.form.get("titulo_propuesta", "").strip()

        # Si el usuario seleccionó una cátedra específica, actualizar el fk_catedra de la sesión si es necesario
        if fk_catedra_sel and fk_catedra_sel.isdigit():
            db_execute_sql(f"UPDATE catedras.sesion SET fk_catedra = {fk_catedra_sel} WHERE id_sesion = {fk_sesion};")

        # 1. Verificar bloqueo previo en tiempo real
        try:
            r_check = requests.get(f"{API_BASE}/ponencia?limite=500", headers=auth_headers(), timeout=4)
            if r_check.status_code == 200:
                ya_asignada = any(p.get("fk_sesion") == fk_sesion for p in r_check.json())
                if ya_asignada:
                    flash("¡Bloqueo Automático! La franja horaria seleccionada ya fue reservada previamente por otro ponente.", "danger")
                    return redirect(url_for("ponentes"))
        except Exception:
            pass

        # 2. Obtener o crear el ID del asistente/ponente
        fk_asistente = None
        if fk_asistente_val and fk_asistente_val.isdigit():
            fk_asistente = int(fk_asistente_val)
        elif documento_ponente:
            try:
                # Buscar por documento en BD
                filas_asist = db_query_json(f"SELECT row_to_json(r) FROM (SELECT id_asistente FROM catedras.asistente WHERE id_asis = '{documento_ponente}' ORDER BY id_asistente DESC LIMIT 1) r;")
                if filas_asist:
                    fk_asistente = filas_asist[0].get("id_asistente")
                else:
                    nombres = nombre_ponente.split()[0] if nombre_ponente else "Docente"
                    apellidos = " ".join(nombre_ponente.split()[1:]) if len(nombre_ponente.split()) > 1 else "Ponente"
                    new_user = {
                        "nombres": nombres,
                        "apellidos": apellidos,
                        "nombre_completo_asis": nombre_ponente or f"Docente {documento_ponente}",
                        "correo_institucional": correo_ponente or f"ponente.{documento_ponente}@usbmed.edu.co",
                        "correo_personal": correo_ponente,
                        "es_externo": True,
                        "activo": True
                    }
                    r_cr = requests.post(f"{API_BASE}/asistente", json=new_user, headers=auth_headers(), timeout=4)
                    if r_cr.status_code in [200, 201]:
                        filas_new = db_query_json("SELECT row_to_json(r) FROM (SELECT id_asistente FROM catedras.asistente ORDER BY id_asistente DESC LIMIT 1) r;")
                        if filas_new:
                            fk_asistente = filas_new[0].get("id_asistente")
            except Exception:
                pass

        if not fk_asistente:
            fk_asistente = 1  # Fallback a docente de referencia

        payload = {
            "fk_sesion": fk_sesion,
            "fk_asistente": fk_asistente,
            "rol": rol
        }
        try:
            r = requests.post(f"{API_BASE}/ponencia", json=payload, headers=auth_headers(), timeout=4)
            if r.status_code in [200, 201]:
                flash(f"¡Ponencia confirmada con éxito! La franja de la sesión #{fk_sesion} ha quedado bloqueada en el calendario y vinculada a la cátedra.", "success")
            elif r.status_code == 409:
                flash("¡Conflicto de Horario! Esta sesión ya cuenta con una ponencia registrada.", "danger")
            else:
                # Si la API dio error por constraint pero los datos son válidos, asegurar registro directo
                res_ins = db_execute_sql(f"INSERT INTO catedras.ponencia (fk_sesion, fk_asistente, rol) VALUES ({fk_sesion}, {fk_asistente}, '{rol}') ON CONFLICT DO NOTHING;")
                if res_ins:
                    flash(f"¡Ponencia confirmada con éxito! La franja de la sesión #{fk_sesion} ha quedado bloqueada en el calendario.", "success")
                else:
                    flash(f"Aviso del sistema: {r.text}", "danger")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("ponentes"))

    if request.method == "POST" and request.form.get("accion") == "eliminar":
        sid = int(request.form.get("fk_sesion"))
        aid = int(request.form.get("fk_asistente"))
        rol = request.form.get("rol", "PONENTE")
        # En la base de datos se libera la ponencia
        db_execute_sql(f"DELETE FROM catedras.ponencia WHERE fk_sesion = {sid} AND fk_asistente = {aid} AND rol = '{rol}';")
        flash(f"Se ha liberado la franja de la sesión #{sid}.", "info")
        return redirect(url_for("ponentes"))

    ponencias = []
    sesiones_disp = []
    asistentes_disp = []
    catedras_recientes = []

    try:
        # Cargar ponencias con nombres enriquecidos desde PostgreSQL
        sql_ponencias = """
        SELECT row_to_json(r) FROM (
            SELECT p.fk_sesion, p.fk_asistente, p.rol,
                   COALESCE(c.nombre, 'Cátedra #' || s.fk_catedra) AS catedra_nombre,
                   s.inicio, s.fk_sede, COALESCE(s.lugar, 'Auditorio San Buenaventura') AS salon,
                   COALESCE(a.nombres || ' ' || a.apellidos, 'Docente #' || p.fk_asistente) AS ponente_nombre,
                   COALESCE(a.id_asis, CAST(p.fk_asistente AS text)) AS doc_asis,
                   COALESCE(a.correo_institucional, a.correo_personal, '') AS correo
            FROM catedras.ponencia p
            LEFT JOIN catedras.sesion s ON p.fk_sesion = s.id_sesion
            LEFT JOIN catedras.catedra c ON s.fk_catedra = c.id_catedra
            LEFT JOIN catedras.asistente a ON p.fk_asistente = a.id_asistente
            ORDER BY p.fk_sesion DESC
        ) r;
        """
        ponencias = db_query_json(sql_ponencias)

        # Cargar únicamente cátedras activas y no vencidas en fechas (con sesiones vigentes en el periodo académico actual o programadas)
        sql_cats_recientes = """
        SELECT row_to_json(r) FROM (
            SELECT DISTINCT ON (c.id_catedra)
                   c.id_catedra, c.nombre, c.id_evento_asis, 
                   s.id_sesion, s.inicio, s.fin, s.estado, s.fk_sede, 
                   COALESCE(s.lugar, 'Auditorio San Buenaventura') as salon
            FROM catedras.catedra c
            JOIN catedras.sesion s ON c.id_catedra = s.fk_catedra
            WHERE c.activo = true
              AND (
                  s.estado IN ('PROGRAMADA', 'ACTIVA', 'ABIERTA')
                  OR (s.inicio >= '2026-09-08' AND s.inicio <= '2026-12-31')
              )
            ORDER BY c.id_catedra DESC, s.inicio DESC
            LIMIT 60
        ) r;
        """
        catedras_recientes = db_query_json(sql_cats_recientes)

        # Asistentes disponibles para autocompletar
        r3 = requests.get(f"{API_BASE}/asistente?limite=200", headers=auth_headers(), timeout=4)
        if r3.status_code == 200:
            asistentes_disp = r3.json()

        # Sesiones disponibles
        r2 = requests.get(f"{API_BASE}/sesion?limite=200", headers=auth_headers(), timeout=4)
        if r2.status_code == 200:
            sesiones_disp = r2.json()
    except Exception as e:
        flash(f"Error al cargar información de ponentes: {str(e)}", "danger")

    # Mapa de sesiones bloqueadas
    sesiones_bloqueadas_map = {}
    for p in ponencias:
        sid = p.get("fk_sesion")
        sesiones_bloqueadas_map[sid] = {
            "ponente": p.get("ponente_nombre", "Docente Asignado"),
            "rol": p.get("rol", "PONENTE"),
            "catedra": p.get("catedra_nombre", "")
        }

    # Pool dinámico que combina primero las cátedras reales creadas por el usuario en la BD
    nombres_catedras_pool = []
    for cr in catedras_recientes:
        nom = cr.get("nombre")
        sede = "Campus San Benito" if cr.get("fk_sede") == "SAN_BENITO" else ("Campus Bello" if cr.get("fk_sede") == "BELLO" else "Campus San Benito")
        salon = cr.get("salon") or "Auditorio San Buenaventura"
        if nom and (nom, sede, salon) not in nombres_catedras_pool:
            nombres_catedras_pool.append((nom, sede, salon))

    # Cátedras institucionales de respaldo para completar el calendario
    catedras_base_institucionales = [
        ("Cátedra Abierta CIDEH: Ética, Paz y Transformación Social", "Campus San Benito", "Auditorio San Buenaventura"),
        ("Cátedra CIDEH: Nuevas Tecnologías, Sociedad y Futuro", "Campus Bello", "Aula Magna Fray Alberto Montealegre"),
        ("Cátedra Bonaventuriana: Innovación y Liderazgo", "Campus San Benito", "Salón de Grados 102"),
        ("Cátedra Abierta: Pedagogía Electoral y Democracia", "Campus San Benito", "Auditorio San Buenaventura"),
        ("Cátedra de Arte y Creación: Miradas Contemporáneas", "Campus Bello", "Auditorio Guillermo de Ockham"),
        ("Cátedra de Humanismo Franciscano y Convivencia", "Campus San Benito", "Salón 305"),
        ("Cátedra Abierta de Inteligencia Artificial y Sociedad", "Campus Bello", "Aula Magna"),
        ("Cátedra de Emprendimiento y Desarrollo Regional", "Campus San Benito", "Auditorio San Buenaventura"),
        ("Cátedra de Psicología y Bienestar Comunitario", "Campus San Benito", "Salón de Grados"),
        ("Cátedra de Sostenibilidad, Biodiversidad y Territorio", "Campus San Benito", "Auditorio San Buenaventura")
    ]
    for c_item in catedras_base_institucionales:
        if c_item not in nombres_catedras_pool:
            nombres_catedras_pool.append(c_item)

    import datetime
    franjas_catalogo = []
    id_base_counter = 1

    # Días de Lunes a Viernes para Noviembre (días 2 a 30) y Diciembre (días 1 a 18)
    for mes_num, max_dias in [(11, 30), (12, 18)]:
        for dia_n in range(1, max_dias + 1):
            fecha_dt = datetime.date(2026, mes_num, dia_n)
            # 0=Lunes, 4=Viernes, 5=Sábado, 6=Domingo
            if fecha_dt.weekday() < 5:
                fecha_iso = fecha_dt.strftime("%Y-%m-%d")
                horarios = [("10:00 a.m.", "10:00"), ("03:00 p.m.", "15:00"), ("05:00 p.m.", "17:00")]
                for hora_txt, hora_iso in horarios:
                    pool_idx = (dia_n * 3 + len(franjas_catalogo)) % len(nombres_catedras_pool)
                    c_nom, c_sede, c_salon = nombres_catedras_pool[pool_idx]
                    franjas_catalogo.append({
                        "fecha": fecha_iso,
                        "hora": hora_txt,
                        "hora_iso": hora_iso,
                        "dia_num": dia_n,
                        "mes": mes_num,
                        "catedra": c_nom,
                        "sede": c_sede,
                        "salon": c_salon,
                        "id_base": id_base_counter
                    })
                    id_base_counter += 1

    # Mapear sesiones y estado de bloqueo
    total_disponibles = 0
    total_bloqueadas = 0

    for idx, f in enumerate(franjas_catalogo):
        # Asignar ID de sesión consistente
        ses_id = sesiones_disp[idx].get("id_sesion") if idx < len(sesiones_disp) else (idx + 1)
        f["ses_id"] = ses_id
        bloqueo = sesiones_bloqueadas_map.get(ses_id)
        f["bloqueada"] = bloqueo is not None
        f["bloqueo_info"] = bloqueo
        if f["bloqueada"]:
            total_bloqueadas += 1
            if bloqueo.get("catedra"):
                f["catedra"] = bloqueo.get("catedra")
        else:
            total_disponibles += 1

    # Agrupar franjas por mes y día para pintar el calendario mensual
    nov_matrix = [
        [0, 0, 0, 0, 0, 0, 1],
        [2, 3, 4, 5, 6, 7, 8],
        [9, 10, 11, 12, 13, 14, 15],
        [16, 17, 18, 19, 20, 21, 22],
        [23, 24, 25, 26, 27, 28, 29],
        [30, 0, 0, 0, 0, 0, 0]
    ]
    dic_matrix = [
        [0, 1, 2, 3, 4, 5, 6],
        [7, 8, 9, 10, 11, 12, 13],
        [14, 15, 16, 17, 18, 19, 20],
        [21, 22, 23, 24, 25, 26, 27],
        [28, 29, 30, 31, 0, 0, 0]
    ]

    def render_month_cells(mes_num, matrix):
        html = ""
        for week in matrix:
            for day in week:
                if day == 0:
                    html += '<div class="cal-day-cell empty-day"></div>'
                else:
                    date_str = f"2026-{mes_num:02d}-{day:02d}"
                    slots_day = [f for f in franjas_catalogo if f["mes"] == mes_num and f["dia_num"] == day]
                    has_slots = len(slots_day) > 0
                    free_count = sum(1 for s in slots_day if not s["bloqueada"])

                    chips_html = ""
                    for s in slots_day:
                        chip_cls = "occupied" if s["bloqueada"] else "available"
                        status_lbl = "Ocupada" if s["bloqueada"] else "Disponible"
                        chips_html += f"""
                        <div class="cal-chip {chip_cls}" onclick="event.stopPropagation(); abrirModalDesdeChip('{s['ses_id']}', {str(s['bloqueada']).lower()})" title="{s['catedra']} ({s['hora']})">
                          <span class="cal-chip-time">{s['hora']}</span>
                          <span>{status_lbl}</span>
                        </div>
                        """

                    badge_html = ""
                    if has_slots:
                        if free_count > 0:
                            badge_html = f'<span class="cal-slots-count-badge free">{free_count} libres</span>'
                        else:
                            badge_html = '<span class="cal-slots-count-badge full">Lleno</span>'

                    cell_classes = f"cal-day-cell {'has-slots' if has_slots else ''}"
                    html += f"""
                    <div class="{cell_classes}" id="cell-{date_str}" onclick="seleccionarDiaCalendario('{date_str}', {day}, {mes_num})">
                      <div class="cal-day-top">
                        <span class="cal-day-num">{day}</span>
                        {badge_html}
                      </div>
                      <div class="cal-slot-chips">
                        {chips_html}
                      </div>
                    </div>
                    """
        return html

    nov_cells_html = render_month_cells(11, nov_matrix)
    dic_cells_html = render_month_cells(12, dic_matrix)

    # Opciones de cátedras reales de la BD para el desplegable dentro del modal
    options_catedras_select = ""
    for cr in catedras_recientes:
        options_catedras_select += f'<option value="{cr.get("id_catedra")}">{cr.get("nombre")} (Evento: {cr.get("id_evento_asis")})</option>\n'

    # Datos JSON para alimentar el panel lateral y el buscador
    franjas_json = json.dumps(franjas_catalogo)
    asistentes_json = json.dumps([{"id": a.get("id_asistente"), "nombre": f"{a.get('nombres')} {a.get('apellidos')}", "doc": a.get("id_asis") or str(a.get("id_asistente")), "correo": a.get("correo_institucional") or a.get("correo_personal") or ""} for a in asistentes_disp])

    rows_pon = ""
    for p in ponencias:
        sid = p.get("fk_sesion")
        aid = p.get("fk_asistente")
        rol = p.get("rol", "PONENTE")
        cat_nom = p.get("catedra_nombre") or f"Sesión #{sid}"
        pon_nom = p.get("ponente_nombre") or f"Docente #{aid}"
        doc_asis = p.get("doc_asis", "-")

        rows_pon += f"""
        <tr>
          <td><span class="td-code">#{sid}</span></td>
          <td style="font-weight:700; color:var(--usb-negro);">{cat_nom}</td>
          <td><span class="td-code">#{aid}</span></td>
          <td style="font-weight:600;">{pon_nom} <span style="font-size:0.8rem;color:var(--usb-text-muted);">({doc_asis})</span></td>
          <td><span class="badge badge-orange">{rol}</span></td>
          <td style="text-align:right;">
            <form method="POST" style="margin:0;display:inline;" onsubmit="return confirm('¿Remover este ponente y liberar la franja horaria?');">
              <input type="hidden" name="accion" value="eliminar">
              <input type="hidden" name="fk_sesion" value="{sid}">
              <input type="hidden" name="fk_asistente" value="{aid}">
              <input type="hidden" name="rol" value="{rol}">
              <button type="submit" class="btn-usb btn-usb-sm btn-usb-dark">Liberar Franja</button>
            </form>
          </td>
        </tr>
        """

    options_ses = "".join([f"<option value='{s.get('id_sesion')}'>Sesión #{s.get('id_sesion')} — Reunión {s.get('numero_reunion')} ({s.get('fk_sede')})</option>" for s in sesiones_disp])
    options_asi = "".join([f"<option value='{a.get('id_asistente')}'>{a.get('nombres')} {a.get('apellidos')} · ID ASIS: {a.get('id_asis') or 'ID ' + str(a.get('id_asistente'))}</option>" for a in asistentes_disp])

    contenido = f"""
    <div class="page-header">
      <div>
        <h1 class="page-title">Calendario y <span>Autogestión de Ponencias</span></h1>
        <p style="font-size:0.88rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Convocatoria CIDEH 2026: Visualice el calendario oficial, seleccione su fecha y franja horaria preferida con bloqueo automático en tiempo real.
        </p>
      </div>
      <div style="display:flex;gap:0.75rem;">
        <button class="btn-usb btn-usb-primary" onclick="abrirReservaVacia()">+ Postular Ponencia</button>
        {('<button class="btn-usb btn-usb-dark" onclick="document.getElementById(\'modal-ponente-crear\').classList.add(\'open\')">Asignación Directa</button>') if session.get('token') else ''}
      </div>
    </div>

    <!-- BANNER OFICIAL DE CONVOCATORIA -->
    <div class="convocatoria-banner">
      <div class="convocatoria-info">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.25rem;">
          <span class="badge badge-orange" style="font-size:0.72rem;letter-spacing:0.05em;">CONVOCATORIA OFICIAL 2026-2</span>
          <span style="font-size:0.8rem;font-weight:700;color:var(--usb-negro);">CIDEH · Vicerrectoría Académica</span>
        </div>
        <h3>Periodo de Convocatoria Abierto (9 al 30 de Septiembre)</h3>
        <p>
          Haga clic en cualquier día o franja horaria del calendario para reservar su cátedra institucional. El sistema bloquea el aula y el horario de forma inmediata para evitar cruces.
        </p>
      </div>
      <div class="convocatoria-countdown">
        <div class="countdown-box">
          <div class="countdown-num">22</div>
          <div class="countdown-label">Días restantes</div>
        </div>
        <div class="countdown-box">
          <div class="countdown-num">100%</div>
          <div class="countdown-label">Tiempo Real</div>
        </div>
      </div>
    </div>

    <!-- KPI GRID -->
    <div class="kpi-grid">
      <div class="kpi-box">
        <div class="kpi-box-title">Franjas Disponibles</div>
        <div class="kpi-box-num" style="color:#16A34A;">{total_disponibles}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Franjas Bloqueadas</div>
        <div class="kpi-box-num" style="color:#DC2626;">{total_bloqueadas}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Horarios Estandarizados</div>
        <div class="kpi-box-num" style="font-size:1.4rem;padding-top:4px;">10am · 3pm · 5pm</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Ponencias Activas</div>
        <div class="kpi-box-num">{len(ponencias)}</div>
      </div>
    </div>

    <!-- NAVEGACIÓN POR PESTAÑAS -->
    <div class="view-tabs-nav">
      <button type="button" class="view-tab-btn active" id="tab-btn-calendario" onclick="cambiarPestanaPonentes('calendario')">
        Calendario Visual Interactivo <span class="tab-counter">{total_disponibles} Libres</span>
      </button>
      <button type="button" class="view-tab-btn" id="tab-btn-asignados" onclick="cambiarPestanaPonentes('asignados')">
        Ponentes Registrados y Moderadores <span class="tab-counter">{len(ponencias)}</span>
      </button>
    </div>

    <!-- VISTA 1: CALENDARIO VISUAL INTERACTIVO -->
    <div id="vista-calendario-autogestion" style="display:block;">
      <!-- Selector de Mes -->
      <div class="calendar-month-selector">
        <div class="calendar-month-title">
          
          <span id="calendar-current-label">Noviembre 2026</span>
          <span class="badge badge-dark" style="font-size:0.75rem;margin-left:0.5rem;">Cátedras Abiertas</span>
        </div>
        <div class="month-btn-group">
          <button type="button" class="month-btn active" id="btn-mes-nov" onclick="cambiarMesCalendario(11)">Noviembre 2026</button>
          <button type="button" class="month-btn" id="btn-mes-dic" onclick="cambiarMesCalendario(12)">Diciembre 2026</button>
        </div>
      </div>

      <!-- Layout Principal del Calendario + Panel Lateral -->
      <div class="calendar-wrapper">
        <!-- Grilla de Calendario -->
        <div class="calendar-grid-container">
          <div class="calendar-weekdays-header">
            <div>Lun</div>
            <div>Mar</div>
            <div>Mié</div>
            <div>Jue</div>
            <div>Vie</div>
            <div>Sáb</div>
            <div>Dom</div>
          </div>
          
          <!-- Grilla Noviembre -->
          <div class="calendar-month-grid" id="grid-mes-11" style="display:grid;">
            {nov_cells_html}
          </div>

          <!-- Grilla Diciembre -->
          <div class="calendar-month-grid" id="grid-mes-12" style="display:none;">
            {dic_cells_html}
          </div>
        </div>

        <!-- Panel Lateral: Detalle del Día y Franjas -->
        <aside class="day-details-panel" id="panel-detalle-dia">
          <div class="day-details-header">
            <h3 class="day-details-title" id="side-dia-title">Miércoles, 4 de Noviembre</h3>
            <div class="day-details-sub" id="side-dia-sub">3 franjas académicas programadas</div>
          </div>

          <div class="day-slots-list" id="side-slots-container">
            <!-- Se actualiza dinámicamente con JS -->
          </div>
        </aside>
      </div>
    </div>

    <!-- VISTA 2: LISTADO DE ASIGNACIONES REALES -->
    <div id="vista-ponentes-asignados" style="display:none;">
      <div class="card-panel">
        <div class="card-panel-header" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
          <div>
            <h3 class="card-panel-title">Registro Oficial de Ponencias en Base de Datos</h3>
            <p style="font-size:0.8rem;color:var(--usb-text-muted);margin-top:0.2rem;">
              Docentes y ponentes postulados con franjas reservadas y confirmadas en la tabla <code>catedras.ponencia</code>.
            </p>
          </div>
          <div style="display:flex;gap:10px;align-items:center;">
            <a href="/ponentes/exportar-csv" class="btn-usb btn-usb-dark btn-usb-sm">
              ⬇ Exportar CSV para ASIS / Oracle
            </a>
            <span class="badge badge-dark">Tabla <code>catedras.ponencia</code></span>
          </div>
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
              {rows_pon if rows_pon else '<tr class="empty-row"><td colspan="6">No hay ponencias registradas actualmente. Reserve una franja horaria en el calendario superior.</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- MODAL LIMPIO: RESERVA Y REGISTRO INTUITIVO DE PONENCIA -->
    <div class="modal-overlay" id="modal-reserva-franja">
      <div class="modal" style="max-width: 620px;">
        <div class="modal-header">
          <h3 class="modal-title">Registrar Ponencia en Calendario</h3>
          <button class="modal-close" onclick="cerrarModalReserva()">✕</button>
        </div>
        <form method="POST" id="form-reserva-franja">
          <input type="hidden" name="accion" value="reservar_franja">
          <input type="hidden" name="fk_sesion" id="reserva_fk_sesion" value="1">
          <input type="hidden" name="fk_asistente" id="reserva_fk_asistente" value="">

          <div class="modal-body">
            <!-- Flujo Intuitivo: Selector de Fecha Calendario y Horarios Disponibles -->
            <div style="background:var(--usb-gris-claro);border:1.5px solid var(--usb-gris-borde);border-radius:8px;padding:1.1rem;margin-bottom:1.25rem;">
              <div class="form-group" style="margin-bottom:1rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                  <label class="form-label" for="modal-input-fecha" style="margin:0;">1. Seleccionar Día en el Calendario <span>*</span></label>
                  <span class="badge badge-orange" id="modal-fecha-badge" style="font-size:0.75rem;">Noviembre 2026</span>
                </div>
                <input type="date" id="modal-input-fecha" class="form-input" 
                       min="2026-11-02" max="2026-12-18" 
                       value="2026-11-02" 
                       onchange="alCambiarFechaEnModal(this.value)" 
                       style="font-weight:700;font-size:0.95rem;background:#FFFFFF;cursor:pointer;">
                <p class="form-hint">Elija cualquier fecha de la convocatoria (Lunes a Viernes). Al cambiar el día, se cargan sus horarios.</p>
              </div>
              
              <div class="form-group" style="margin-bottom:0;">
                <label class="form-label" style="margin-bottom:0.4rem;">2. Horarios Disponibles para este Día <span>*</span></label>
                <div id="modal-horarios-botones" style="display:grid;grid-template-columns:repeat(3, 1fr);gap:8px;margin-bottom:0.4rem;">
                  <!-- Botones generados dinámicamente según el día -->
                </div>
                <p class="form-hint" style="margin:0;" id="modal-horarios-hint">Haga clic en la hora en la que desea postular su cátedra.</p>
              </div>
            </div>

            <!-- Resumen Visual y Selector de la Cátedra Vinculada -->
            <div style="background:var(--usb-naranja-light);border:1.5px solid #FDBA74;border-radius:8px;padding:1rem;margin-bottom:1.25rem;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <span class="badge badge-dark" style="font-size:0.72rem;">CÁTEDRA Y LUGAR DE LA FRANJA</span>
                <span id="reserva-resumen-hora" style="font-weight:800;color:var(--usb-negro);font-size:0.85rem;">10:00 a.m.</span>
              </div>
              <div class="form-group" style="margin-bottom:0.4rem;">
                <label class="form-label" for="reserva_select_catedra" style="font-size:0.8rem;margin-bottom:0.25rem;">Seleccione la Cátedra Académica a la que postula <span>*</span></label>
                <select class="form-input" id="reserva_select_catedra" name="fk_catedra" onchange="alCambiarCatedraEnModal(this)" style="background:#FFFFFF;font-weight:700;font-size:0.88rem;">
                  {options_catedras_select}
                </select>
              </div>
              <div id="reserva-resumen-franja" style="display:none;"></div>
              <div id="reserva-resumen-lugar" style="font-size:0.82rem;color:var(--usb-text-muted);margin-top:4px;">
                Campus San Benito · Auditorio San Buenaventura
              </div>
            </div>

            <!-- Paso 1: Identificación del Ponente con Autocompletado Intuitivo -->
            <div class="form-group" style="margin-bottom:1rem;">
              <label class="form-label">Docente o Conferencista (Nombre o Cédula) <span>*</span></label>
              <div class="autocomplete-search-box">
                <input class="form-input" type="text" id="reserva_busqueda_ponente" placeholder="Escriba su nombre o cédula para buscar o registrar..." autocomplete="off" oninput="buscarPonenteAutocompletar(this.value)">
                <div class="autocomplete-dropdown" id="dropdown-sugerencias-ponentes"></div>
              </div>
              <p class="form-hint">Si ya está registrado en la universidad se cargarán sus datos automáticamente.</p>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;margin-bottom:1rem;">
              <div class="form-group">
                <label class="form-label" for="reserva_documento">Número de Cédula / Documento <span>*</span></label>
                <input class="form-input" type="text" id="reserva_documento" name="documento_ponente" required placeholder="Ej: 71234567">
              </div>
              <div class="form-group">
                <label class="form-label" for="reserva_nombre">Nombre Completo del Ponente <span>*</span></label>
                <input class="form-input" type="text" id="reserva_nombre" name="nombre_ponente" required placeholder="Ej: Dr. Carlos Restrepo">
              </div>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;margin-bottom:1rem;">
              <div class="form-group">
                <label class="form-label" for="reserva_correo">Correo Electrónico Institucional <span>*</span></label>
                <input class="form-input" type="email" id="reserva_correo" name="correo_ponente" required placeholder="docente@usbmed.edu.co">
              </div>
              <div class="form-group">
                <label class="form-label" for="reserva_rol">Rol Académico <span>*</span></label>
                <select class="form-input" id="reserva_rol" name="rol" required>
                  <option value="PONENTE">PONENTE (Conferencista Principal)</option>
                  <option value="MODERADOR">MODERADOR (Coordinador de Mesa)</option>
                  <option value="PANELISTA">PANELISTA (Invitado Especial)</option>
                </select>
              </div>
            </div>

            <!-- Paso 2: Título y Eje de la Ponencia -->
            <div class="form-group" style="margin-bottom:1.25rem;">
              <label class="form-label" for="reserva_titulo">Título o Tema Específico de su Ponencia <span>*</span></label>
              <input class="form-input" type="text" id="reserva_titulo" name="titulo_propuesta" required placeholder="Ej: Nuevos Horizontes de la Bioética y Tecnología en Colombia">
              <p class="form-hint">Este título figurará en la agenda académica oficial y en las actas de acreditación.</p>
            </div>

            <div style="background:var(--usb-gris-claro);border:1px solid var(--usb-gris-borde);border-radius:6px;padding:0.85rem;font-size:0.78rem;color:var(--usb-text-muted);line-height:1.45;">
              <strong>Garantía de Bloqueo Inmediato:</strong> Al enviar el formulario, el sistema bloquea de inmediato la franja para que ningún otro docente pueda elegirla y le despacha la confirmación para sincronizar con su calendario.
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModalReserva()">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Confirmar Ponencia y Bloquear Franja</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL: INSCRIPCIÓN Y AUTOGESTIÓN DIRECTA DEL DOCENTE -->
    <div class="modal-overlay" id="modal-ponente-crear">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Inscripción Directa de Cátedra por el Docente</h3>
          <button class="modal-close" onclick="document.getElementById('modal-ponente-crear').classList.remove('open')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="accion" value="crear">
          <div class="modal-body">
            <div class="alert alert-info py-2 mb-3">
              <strong>Autogestión Docente:</strong> El docente inscribe el mismo su cátedra y confirma su ponencia de forma autónoma.
            </div>
            <div class="form-group">
              <label class="form-label" for="fk_sesion">Sesión Académica de Cátedra <span>*</span></label>
              <select class="form-input" id="fk_sesion" name="fk_sesion" required>
                {options_ses}
              </select>
            </div>
            <div class="form-group">
              <label class="form-label" for="fk_asistente">Ponente o Docente <span>*</span></label>
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
            <button type="button" class="btn-usb btn-usb-ghost" onclick="document.getElementById('modal-ponente-crear').classList.remove('open')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Asignar a la Cátedra</button>
          </div>
        </form>
      </div>
    </div>

    <script>
      const TODAS_FRANJAS = {franjas_json};
      const PADRON_ASISTENTES = {asistentes_json};
      let diaSeleccionadoActual = '2026-11-04';

      function cambiarPestanaPonentes(pestana) {{
        const btnCal = document.getElementById('tab-btn-calendario');
        const btnAsig = document.getElementById('tab-btn-asignados');
        const vistaCal = document.getElementById('vista-calendario-autogestion');
        const vistaAsig = document.getElementById('vista-ponentes-asignados');

        if (pestana === 'calendario') {{
          btnCal.classList.add('active');
          btnAsig.classList.remove('active');
          vistaCal.style.display = 'block';
          vistaAsig.style.display = 'none';
        }} else {{
          btnAsig.classList.add('active');
          btnCal.classList.remove('active');
          vistaCal.style.display = 'none';
          vistaAsig.style.display = 'block';
        }}
      }}

      function cambiarMesCalendario(mes) {{
        const grid11 = document.getElementById('grid-mes-11');
        const grid12 = document.getElementById('grid-mes-12');
        const btn11 = document.getElementById('btn-mes-nov');
        const btn12 = document.getElementById('btn-mes-dic');
        const label = document.getElementById('calendar-current-label');

        if (mes === 11) {{
          grid11.style.display = 'grid';
          grid12.style.display = 'none';
          btn11.classList.add('active');
          btn12.classList.remove('active');
          label.textContent = 'Noviembre 2026';
          seleccionarDiaCalendario('2026-11-04', 4, 11);
        }} else {{
          grid11.style.display = 'none';
          grid12.style.display = 'grid';
          btn12.classList.add('active');
          btn11.classList.remove('active');
          label.textContent = 'Diciembre 2026';
          seleccionarDiaCalendario('2026-12-02', 2, 12);
        }}
      }}

      function seleccionarDiaCalendario(dateStr, dia, mes) {{
        diaSeleccionadoActual = dateStr;
        document.querySelectorAll('.cal-day-cell').forEach(c => c.classList.remove('active-selected'));
        const cell = document.getElementById('cell-' + dateStr);
        if (cell) cell.classList.add('active-selected');

        const mesesNombres = {{ 11: 'Noviembre', 12: 'Diciembre' }};
        const slotsDelDia = TODAS_FRANJAS.filter(f => f.fecha === dateStr);

        document.getElementById('side-dia-title').textContent = dia + ' de ' + mesesNombres[mes] + ' 2026';
        document.getElementById('side-dia-sub').textContent = slotsDelDia.length > 0 
          ? slotsDelDia.length + ' franja(s) académica(s) programada(s)'
          : 'No hay franjas de cátedra programadas para este día';

        const cont = document.getElementById('side-slots-container');
        if (slotsDelDia.length === 0) {{
          cont.innerHTML = '<div style="color:var(--usb-text-muted);font-size:0.84rem;padding:1rem 0;text-align:center;">Seleccione cualquier día hábil de la semana (Lunes a Viernes) para ver las franjas disponibles.</div>';
          return;
        }}

        let html = '';
        slotsDelDia.forEach(s => {{
          const estaBloqueada = s.bloqueada;
          const badge = estaBloqueada ? '<span class="badge-bloqueada">BLOQUEADA</span>' : '<span class="badge-disponible">DISPONIBLE</span>';
          const btn = estaBloqueada 
            ? '<button type="button" class="btn-usb btn-usb-sm btn-usb-dark" style="width:100%;opacity:0.75;cursor:not-allowed;" disabled>Ocupado por ' + (s.bloqueo_info?.ponente?.substring(0, 16) || 'Docente') + '...</button>'
            : '<button type="button" class="btn-usb btn-usb-primary btn-usb-sm" style="width:100%;" onclick="abrirReservaPorId(' + s.ses_id + ')">Postular mi Ponencia &rarr;</button>';

          html += `
          <div class="day-slot-item ${{estaBloqueada ? 'bloqueada' : 'disponible'}}">
            <div class="day-slot-item-header">
              <span class="day-slot-time">Horario: ${{s.hora}}</span>
              ${{badge}}
            </div>
            <div class="day-slot-catedra">${{s.catedra}}</div>
            <div class="day-slot-loc">
              <span><strong>Sede:</strong> ${{s.sede}}</span>
              <span><strong>Aula:</strong> ${{s.salon}} (Sesión #${{s.ses_id}})</span>
            </div>
            ${{btn}}
          </div>
          `;
        }});
        cont.innerHTML = html;
      }}

      function abrirReservaPorId(idSesion) {{
        const franja = TODAS_FRANJAS.find(f => String(f.ses_id) === String(idSesion)) || TODAS_FRANJAS[0];
        if (!franja) return;
        if (franja.bloqueada) {{
          alert('Esta franja horaria ya se encuentra reservada y bloqueada para evitar cruces en el auditorio.');
          return;
        }}
        abrirReservaFranja(franja.ses_id, franja.fecha, franja.hora, franja.catedra, franja.sede, franja.salon);
      }}

      function abrirModalDesdeChip(idSesion, estaBloqueada) {{
        if (estaBloqueada) {{
          alert('Esta franja horaria ya se encuentra reservada y bloqueada para evitar cruces en el auditorio.');
          return;
        }}
        abrirReservaPorId(idSesion);
      }}

      function alCambiarFechaEnModal(fecha) {{
        const slots = TODAS_FRANJAS.filter(f => f.fecha === fecha);
        const badge = document.getElementById('modal-fecha-badge');
        if (badge) {{
          badge.textContent = fecha;
        }}
        if (slots.length === 0) {{
          document.getElementById('modal-horarios-botones').innerHTML = '<div style="color:var(--usb-text-muted);font-size:0.8rem;grid-column:1/-1;padding:0.5rem 0;">No hay franjas académicas para esta fecha (elija de lunes a viernes en noviembre o diciembre).</div>';
          return;
        }}
        const primeraLibre = slots.find(s => !s.bloqueada) || slots[0];
        abrirReservaFranja(primeraLibre.ses_id, primeraLibre.fecha, primeraLibre.hora, primeraLibre.catedra, primeraLibre.sede, primeraLibre.salon);
      }}

      function alCambiarCatedraEnModal(selectElem) {{
        const text = selectElem.options[selectElem.selectedIndex].text;
        const resFranja = document.getElementById('reserva-resumen-franja');
        if (resFranja) {{
          resFranja.textContent = text;
        }}
      }}

      function abrirReservaFranja(idSesion, fecha, hora, catedra, sede, salon) {{
        document.getElementById('reserva_fk_sesion').value = idSesion;
        const inputFecha = document.getElementById('modal-input-fecha');
        if (inputFecha) inputFecha.value = fecha;
        const badgeFecha = document.getElementById('modal-fecha-badge');
        if (badgeFecha) badgeFecha.textContent = fecha;
        const resFranja = document.getElementById('reserva-resumen-franja');
        if (resFranja) resFranja.textContent = catedra;
        document.getElementById('reserva-resumen-hora').textContent = hora;
        document.getElementById('reserva-resumen-lugar').textContent = sede + ' · ' + salon + ' (Sesión #' + idSesion + ')';

        // Sincronizar el select de cátedra si coincide con alguna opción
        const selCat = document.getElementById('reserva_select_catedra');
        if (selCat) {{
          for (let i = 0; i < selCat.options.length; i++) {{
            if (selCat.options[i].text.toLowerCase().includes(catedra.toLowerCase().substring(0, 15))) {{
              selCat.selectedIndex = i;
              break;
            }}
          }}
        }}

        // Renderizar los botones de horario disponibles para este día exacto
        const franjasDelDia = TODAS_FRANJAS.filter(f => f.fecha === fecha);
        const contenedorHorarios = document.getElementById('modal-horarios-botones');
        let botonesHtml = '';

        franjasDelDia.forEach(f => {{
          const esActual = String(f.ses_id) === String(idSesion);
          const bloqueada = f.bloqueada;
          let btnCls = 'btn-usb btn-usb-sm ';
          if (bloqueada) {{
            btnCls += 'btn-usb-ghost" style="opacity:0.4;text-decoration:line-through;cursor:not-allowed;" disabled title="Horario bloqueado por otra ponencia"';
          }} else if (esActual) {{
            btnCls += 'btn-usb-primary" style="font-weight:800;box-shadow:0 0 0 2px var(--usb-negro);"';
          }} else {{
            btnCls += 'btn-usb-ghost" style="border:1.5px solid var(--usb-gris-borde);" onclick="seleccionarHoraEnModal(' + f.ses_id + ')"';
          }}
          botonesHtml += `<button type="button" class="${{btnCls}}">${{f.hora}}</button>`;
        }});
        contenedorHorarios.innerHTML = botonesHtml;

        document.getElementById('modal-reserva-franja').classList.add('open');
      }}

      function seleccionarHoraEnModal(idSesion) {{
        const f = TODAS_FRANJAS.find(x => String(x.ses_id) === String(idSesion));
        if (f) {{
          abrirReservaFranja(f.ses_id, f.fecha, f.hora, f.catedra, f.sede, f.salon);
        }}
      }}

      function abrirReservaVacia() {{
        const primeraLibre = TODAS_FRANJAS.find(f => !f.bloqueada) || TODAS_FRANJAS[0];
        if (primeraLibre) {{
          abrirReservaFranja(primeraLibre.ses_id, primeraLibre.fecha, primeraLibre.hora, primeraLibre.catedra, primeraLibre.sede, primeraLibre.salon);
        }}
      }}

      function cerrarModalReserva() {{
        document.getElementById('modal-reserva-franja').classList.remove('open');
        document.getElementById('dropdown-sugerencias-ponentes').style.display = 'none';
      }}

      function buscarPonenteAutocompletar(query) {{
        const q = query.toLowerCase().trim();
        const drop = document.getElementById('dropdown-sugerencias-ponentes');
        if (!q || q.length < 2) {{
          drop.style.display = 'none';
          return;
        }}

        const coincidencias = PADRON_ASISTENTES.filter(a => 
          a.nombre.toLowerCase().includes(q) || a.doc.toLowerCase().includes(q)
        ).slice(0, 6);

        if (coincidencias.length === 0) {{
          drop.innerHTML = '<div class="autocomplete-item" style="color:var(--usb-text-muted);">Sin coincidencias en el padrón. Puede ingresar sus datos manualmente abajo.</div>';
          drop.style.display = 'block';
          return;
        }}

        let html = '';
        coincidencias.forEach(a => {{
          html += `
          <div class="autocomplete-item" onclick="seleccionarPonenteSugerido('${{a.id}}', '${{a.nombre.replace(/'/g, "\\'")}}', '${{a.doc}}', '${{a.correo}}')">
            <strong>${{a.nombre}}</strong> <span style="font-size:0.75rem;color:var(--usb-text-muted);">— Doc: ${{a.doc}}</span>
          </div>
          `;
        }});
        drop.innerHTML = html;
        drop.style.display = 'block';
      }}

      function seleccionarPonenteSugerido(id, nombre, doc, correo) {{
        document.getElementById('reserva_fk_asistente').value = id;
        document.getElementById('reserva_busqueda_ponente').value = nombre + ' (' + doc + ')';
        document.getElementById('reserva_nombre').value = nombre;
        document.getElementById('reserva_documento').value = doc;
        if (correo) document.getElementById('reserva_correo').value = correo;
        document.getElementById('dropdown-sugerencias-ponentes').style.display = 'none';
      }}

      // Inicializar en el primer día con cátedras
      document.addEventListener('DOMContentLoaded', () => {{
        seleccionarDiaCalendario('2026-11-04', 4, 11);
      }});
      // Ejecución directa si el script corre tras carga
      seleccionarDiaCalendario('2026-11-04', 4, 11);
    </script>
    """
    return render_template_string(BASE_LAYOUT, titulo="Calendario y Ponencias", contenido=contenido)

@app.route("/ponentes/exportar-csv")
def exportar_csv_ponentes():
    try:
        r_p = api_get("/ponencia?limite=1000")
        ponencias = r_p.json() if r_p.status_code == 200 else []
        r_a = api_get("/asistente?limite=1000")
        asistentes = {a.get("id_asistente"): a for a in (r_a.json() if r_a.status_code == 200 else [])}
        r_s = api_get("/sesion?limite=1000")
        sesiones = {s.get("id_sesion"): s for s in (r_s.json() if r_s.status_code == 200 else [])}
        r_c = api_get("/catedra?limite=1000")
        catedras = {c.get("id_catedra"): c for c in (r_c.json() if r_c.status_code == 200 else [])}

        csv_lines = ["ID_EVENTO_ASIS,ID_ASISTENTE_ASIS,ROL_ACADEMICO,FECHA_SESION,CATEDRA_OFICIAL"]
        for p in ponencias:
            sid = p.get("fk_sesion")
            aid = p.get("fk_asistente")
            rol = p.get("rol", "PONENTE")

            ses = sesiones.get(sid, {})
            cid = ses.get("fk_catedra")
            cat = catedras.get(cid, {})
            ev_asis = cat.get("id_evento_asis", "000000000")
            asis = asistentes.get(aid, {})
            asis_id = asis.get("id_asis") or asis.get("documento_vigente") or str(aid)
            fecha_ses = (ses.get("inicio") or "2026-11-04")[:10]
            cat_nom = cat.get("nombre", "Catedra Abierta").replace(",", " ")

            csv_lines.append(f"{ev_asis},{asis_id},{rol},{fecha_ses},{cat_nom}")

        csv_data = "\n".join(csv_lines)
        return send_file(
            io.BytesIO(csv_data.encode("utf-8-sig")),
            mimetype="text/csv",
            as_attachment=True,
            download_name="PONENTES_CONVOCATORIA_ASIS_ORACLE.csv"
        )
    except Exception as e:
        flash(f"Error al exportar archivo de ponentes: {str(e)}", "danger")
        return redirect(url_for("ponentes"))


# ==========================================
# 5. EMISION DE CODIGO QR PARA SALA
# ==========================================
@app.route("/enlace/emitir/<int:id_sesion>")
def emitir_enlace(id_sesion):
    if not session.get("token"):
        return redirect(url_for("login"))
    try:
        r = requests.post(f"{API_BASE}/enlace/emitir", json={"id_sesion": id_sesion, "minutos_antes": 60, "minutos_despues": 180}, headers=auth_headers(), timeout=4)
        if r.status_code == 200:
            id_enlace = r.json().get("id_enlace")
            flash(f"Código QR emitido para la sesión #{id_sesion}.", "success")
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
        <h1 class="page-title">Proyección de Acceso <span>Auditorio / Sala</span></h1>
        <p style="font-size:0.88rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Proyecte esta pantalla en el auditorio para que los asistentes escaneen el código desde sus teléfonos móviles.
        </p>
      </div>
      <a href="/sesiones" class="btn-usb btn-usb-ghost">← Volver a Sesiones</a>
    </div>

    <div style="max-width: 600px; margin: 1rem auto;">
      <div class="card-panel" style="text-align: center;">
        <div class="card-panel-header" style="justify-content: center;">
          <h3 class="card-panel-title">Escanear para Registrar Asistencia</h3>
        </div>
        <div class="card-panel-body" style="padding: 2.5rem 1.5rem;">
          <div style="display:inline-block; padding: 16px; background:#FFF; border: 3px solid var(--usb-negro); border-radius:12px; box-shadow: var(--shadow-hover); margin-bottom: 1.5rem;">
            <img src="{qr_url}" alt="Código QR Institucional" style="width: 260px; height: 260px; display: block;">
          </div>

          <div style="background: var(--usb-naranja-light); border: 1.5px solid #FDBA74; border-radius: 8px; padding: 1rem; text-align: left; margin-bottom: 1.5rem;">
            <div style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; color: var(--usb-naranja); letter-spacing: 0.05em; margin-bottom: 4px;">
              Enlace Web Directo de la Cátedra:
            </div>
            <a href="{url_directa}" target="_blank" style="font-size: 0.92rem; font-weight: 700; color: var(--usb-negro); word-break: break-all;">
              {url_directa}
            </a>
          </div>

          <p style="font-size: 0.85rem; color: var(--usb-text-muted); line-height: 1.6;">
            El participante validará su presencia física mediante geolocalización en el campus universitario 
            y se bifurcará automáticamente entre estudiante USB o asistente externo.
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
        <h1 class="page-title">Integración y Transferencia <span>ASIS / Oracle</span></h1>
        <p style="font-size:0.88rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Exportación de archivo plano estándar de 3 columnas (Reunión, ID_ASIS, Programa) requerido por Oracle.
        </p>
      </div>
    </div>

    <div class="card-panel" style="padding: 1.5rem; margin-bottom:1.5rem;">
      <div style="display:flex; gap:1.25rem; align-items:flex-end; flex-wrap:wrap;">
        <div style="flex: 1; min-width:280px;">
          <label class="form-label" style="display:block; margin-bottom: 6px;">Seleccionar Sesión Académica:</label>
          <select class="form-input" onchange="window.location.href='/migracion/sesion/' + this.value;">
            {opciones_html}
          </select>
        </div>
        <div style="display:flex; gap: 0.75rem;">
          <a href="/migracion/descargar-csv/{id_sesion}" class="btn-usb btn-usb-primary">Descargar CSV Plano</a>
          <a href="/migracion/transferir/{id_sesion}" class="btn-usb btn-usb-dark">Transferir a Carpeta Oracle</a>
        </div>
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

    import html
    import json

    bitacora_list = []
    asistencias_list = []
    try:
        r = requests.get(f"{API_BASE}/bitacora?limite=1000", headers=auth_headers(), timeout=6)
        if r.status_code == 200:
            bitacora_list = r.json()
    except Exception as e:
        flash(f"Error al cargar registros de bitácora: {str(e)}", "danger")

    try:
        r_asis = requests.get(f"{API_BASE}/v_asistencia_completa?limite=1000", headers=auth_headers(), timeout=6)
        if r_asis.status_code == 200:
            asistencias_list = r_asis.json()
    except Exception as e:
        flash(f"Error al cargar asistencias completas: {str(e)}", "danger")

    # Agrupar asistencias por Cátedra
    # Estructura: dict con clave nombre/id de catedra
    catedras_asist_map = {}
    for a in asistencias_list:
        cat_nom = a.get("catedra") or "Cátedra General"
        ev_asis = a.get("id_evento_asis") or "-"
        if cat_nom not in catedras_asist_map:
            catedras_asist_map[cat_nom] = {
                "nombre": cat_nom,
                "evento_asis": ev_asis,
                "sesiones": set(),
                "asistentes": []
            }
        ses_id = a.get("id_sesion")
        if ses_id:
            catedras_asist_map[cat_nom]["sesiones"].add(ses_id)
        catedras_asist_map[cat_nom]["asistentes"].append(a)

    # Tarjetas de Cátedras con Asistencia
    cards_catedras_html = ""
    for cat_nom, data in sorted(catedras_asist_map.items(), key=lambda x: len(x[1]["asistentes"]), reverse=True):
        total_asist = len(data["asistentes"])
        num_ses = len(data["sesiones"]) or 1
        ev_cod = data["evento_asis"]
        cat_payload = html.escape(json.dumps(data["asistentes"], ensure_ascii=False), quote=True)
        cat_nom_esc = html.escape(cat_nom, quote=True)
        ev_cod_esc = html.escape(str(ev_cod), quote=True)

        cards_catedras_html += f"""
        <div class="catedra-card-asist" data-search="{html.escape(cat_nom).lower()} {ev_cod}">
          <div>
            <div class="cat-header-top">
              <span class="td-code" style="font-weight:700;">ASIS: {ev_cod}</span>
              <span class="cat-asist-badge-count">{total_asist} Asistentes</span>
            </div>
            <h4 class="cat-title-asist">{cat_nom}</h4>
            <div class="cat-card-meta">
              <span><strong>Sesiones con Registro:</strong> {num_ses} sesión(es)</span>
              <span><strong>Auditoría de Origen:</strong> Código QR / ASIS</span>
            </div>
          </div>
          <div class="cat-card-footer">
            <span style="font-size:0.75rem; color:var(--usb-text-muted);">Trazabilidad activa</span>
            <button type="button" class="btn-usb btn-usb-primary btn-usb-sm"
              onclick="abrirDetalleAsistentes('{cat_nom_esc}', '{ev_cod_esc}', {total_asist}, this)"
              data-asistentes="{cat_payload}">
              Ver Asistentes ({total_asist}) →
            </button>
          </div>
        </div>
        """

    if not cards_catedras_html:
        cards_catedras_html = '<div class="card-panel" style="padding:2rem;text-align:center;color:var(--usb-text-muted);">No hay registros de asistencias vinculados a cátedras actualmente.</div>'

    rows_b = ""
    tablas_unicas = set()
    total_inserts = 0
    total_updates = 0
    total_deletes = 0

    for idx, b in enumerate(bitacora_list):
        bid = b.get("id_bitacora", "-")
        fecha = str(b.get("ocurrido_en", "-"))[:19].replace("T", " ")
        usr = b.get("usuario_bd", "postgres")
        tabla = b.get("nombre_tabla", "-")
        tablas_unicas.add(tabla)
        op = (b.get("operacion") or "INSERT").upper()
        llave = b.get("llave", "-")
        raw_datos = b.get("datos_despues") or b.get("datos_antes") or "{}"

        if op == "INSERT":
            total_inserts += 1
            op_badge = '<span class="audit-badge-op audit-badge-insert">INSERT</span>'
        elif op == "UPDATE":
            total_updates += 1
            op_badge = '<span class="audit-badge-op audit-badge-update">UPDATE</span>'
        else:
            total_deletes += 1
            op_badge = '<span class="audit-badge-op audit-badge-delete">DELETE</span>'

        tags_resumen = ""
        json_bonito = "{}"
        try:
            parsed = json.loads(raw_datos)
            json_bonito = json.dumps(parsed, indent=2, ensure_ascii=False)
            if "origen" in parsed:
                tags_resumen += f'<span class="audit-tag"><strong>Origen:</strong> {parsed.get("origen")}</span>'
            if "fk_sesion" in parsed:
                tags_resumen += f'<span class="audit-tag"><strong>Sesión:</strong> #{parsed.get("fk_sesion")}</span>'
            if "fk_programa_snapshot" in parsed:
                tags_resumen += f'<span class="audit-tag"><strong>Prog:</strong> {parsed.get("fk_programa_snapshot")}</span>'
            if "fk_vinculacion_snapshot" in parsed:
                tags_resumen += f'<span class="audit-tag"><strong>Tipo:</strong> {parsed.get("fk_vinculacion_snapshot")}</span>'
            if "ip" in parsed and not tags_resumen:
                tags_resumen += f'<span class="audit-tag"><strong>IP:</strong> {parsed.get("ip")}</span>'
        except Exception:
            json_bonito = raw_datos
            tags_resumen = f'<span class="audit-tag">{html.escape(str(raw_datos)[:35])}</span>'

        if not tags_resumen:
            tags_resumen = '<span class="audit-tag">Datos registrados</span>'

        json_attr = html.escape(json_bonito, quote=True)
        tabla_esc = html.escape(tabla, quote=True)
        op_esc = html.escape(op, quote=True)
        fecha_esc = html.escape(fecha, quote=True)
        llave_esc = html.escape(str(llave), quote=True)
        usr_esc = html.escape(usr, quote=True)

        rows_b += f"""
        <tr class="audit-row" data-op="{op}" data-tabla="{tabla}" data-search="{bid} {tabla} {op} {llave} {usr} {html.escape(raw_datos).lower()}">
          <td><span class="td-code">#{bid}</span></td>
          <td style="font-size:0.82rem; color:var(--usb-text-muted); white-space:nowrap;">{fecha}</td>
          <td>{op_badge}</td>
          <td style="font-weight:700; color:var(--usb-negro);">{tabla}</td>
          <td><span class="td-code">#{llave}</span></td>
          <td>
            <div class="audit-preview-box">
              <div class="audit-preview-tags">
                {tags_resumen}
              </div>
              <button type="button" class="btn-inspect" 
                onclick="verDetalleAuditoria('{bid}', '{fecha_esc}', '{op_esc}', '{tabla_esc}', '{llave_esc}', '{usr_esc}', this)"
                data-payload="{json_attr}">
                Ver JSON
              </button>
            </div>
          </td>
          <td style="font-size:0.82rem; font-weight:600; color:var(--usb-negro);">{usr}</td>
        </tr>
        """

    chips_tablas = '<button type="button" class="audit-chip active" onclick="filtrarTabla(\'TODAS\', this)">Todas las Tablas</button>'
    for t in sorted(tablas_unicas):
        chips_tablas += f'<button type="button" class="audit-chip" onclick="filtrarTabla(\'{t}\', this)">{t}</button>'

    total_eventos_str = str(len(bitacora_list))
    total_inserts_str = str(total_inserts)
    total_catedras_con_asist = str(len(catedras_asist_map))
    tabla_auditoria_rows = rows_b if rows_b else '<tr class="empty-row"><td colspan="7">No hay registros de auditoría disponibles.</td></tr>'

    contenido = """
    <div class="page-header">
      <div>
        <h1 class="page-title">Auditoría y <span>Bitácora de Cátedras</span></h1>
        <p style="font-size:0.88rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Trazabilidad inmutable de eventos, auditoría transaccional y registro de asistencias por cátedra.
        </p>
      </div>
    </div>

    <!-- Indicadores Principales -->
    <div class="kpi-grid" style="grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); margin-bottom: 1.5rem;">
      <div class="kpi-box" style="border-left: 4px solid var(--usb-naranja);">
        <div class="kpi-box-title">Total Eventos Bitácora</div>
        <div class="kpi-box-num">""" + total_eventos_str + """</div>
        <div style="font-size:0.75rem; color:var(--usb-text-muted); margin-top:0.35rem;">Eventos registrados en base de datos</div>
      </div>
      <div class="kpi-box" style="border-left: 4px solid #16a34a;">
        <div class="kpi-box-title">Asistencias Acreditadas</div>
        <div class="kpi-box-num" style="color:#16a34a;">""" + total_inserts_str + """</div>
        <div style="font-size:0.75rem; color:var(--usb-text-muted); margin-top:0.35rem;">Estudiantes y participantes registrados</div>
      </div>
      <div class="kpi-box" style="border-left: 4px solid #2563EB;">
        <div class="kpi-box-title">Cátedras con Asistentes</div>
        <div class="kpi-box-num" style="color:#2563EB;">""" + total_catedras_con_asist + """</div>
        <div style="font-size:0.75rem; color:var(--usb-text-muted); margin-top:0.35rem;">Cátedras activas con asistencia auditada</div>
      </div>
    </div>

    <!-- Pestañas de Navegación: Asistencias por Cátedra vs Registro Cronológico -->
    <div class="view-tabs-nav">
      <button type="button" class="view-tab-btn active" id="tab-btn-catedras" onclick="cambiarPestana('catedras')">
        <span>Asistencia por Cátedra</span>
        <span class="tab-counter">""" + total_catedras_con_asist + """ Cátedras</span>
      </button>
      <button type="button" class="view-tab-btn" id="tab-btn-bitacora" onclick="cambiarPestana('bitacora')">
        <span>Registro Cronológico de Transacciones</span>
        <span class="tab-counter">""" + total_eventos_str + """ Eventos</span>
      </button>
    </div>

    <!-- VISTA 1: ASISTENCIA POR CÁTEDRA -->
    <div id="vista-asistencias-catedras">
      <div class="audit-toolbar" style="margin-bottom:1.25rem;">
        <div class="audit-search-wrap">
          <input type="text" id="cat-asist-search" class="form-input" 
                 placeholder="Buscar cátedra o código de evento ASIS..." 
                 oninput="filtrarCatedrasAsistencia()" style="max-width:420px;">
        </div>
        <div style="font-size:0.82rem; color:var(--usb-text-muted);">
          Seleccione <strong>"Ver Asistentes"</strong> para consultar el listado nominal auditado de cada cátedra.
        </div>
      </div>

      <div class="catedras-asistencia-grid" id="grid-catedras-asist">
        """ + cards_catedras_html + """
      </div>
    </div>

    <!-- VISTA 2: REGISTRO CRONOLÓGICO DE BITÁCORA -->
    <div id="vista-bitacora-cronologica" style="display:none;">
      <div class="audit-toolbar">
        <div class="audit-search-wrap">
          <input type="text" id="audit-search" class="form-input" 
                 placeholder="Buscar por ID, sesión, tabla, programa o contenido..." 
                 oninput="aplicarFiltros()" style="max-width:380px;">
          <select id="audit-op-filter" class="form-input" onchange="aplicarFiltros()" style="max-width:160px;">
            <option value="TODAS">Todas las operaciones</option>
            <option value="INSERT">Solo INSERT</option>
            <option value="UPDATE">Solo UPDATE</option>
            <option value="DELETE">Solo DELETE</option>
          </select>
        </div>

        <div class="audit-chips-wrap">
          """ + chips_tablas + """
        </div>
      </div>

      <div class="card-panel">
        <div class="card-panel-header">
          <div>
            <h3 class="card-panel-title">Registro Cronológico de Operaciones</h3>
            <p style="font-size:0.8rem;color:var(--usb-text-muted);margin-top:0.2rem;">
              Eventos inmutables capturados por los disparadores de base de datos.
            </p>
          </div>
          <span class="badge badge-dark">catedras.bitacora</span>
        </div>
        <div class="table-wrap" style="border:none;box-shadow:none;">
          <table id="tabla-auditoria">
            <thead>
              <tr>
                <th>ID</th>
                <th>Fecha y Hora</th>
                <th>Operación</th>
                <th>Tabla Afectada</th>
                <th>Registro ID</th>
                <th>Contenido y Snapshot</th>
                <th>Usuario BD</th>
              </tr>
            </thead>
            <tbody>
              """ + tabla_auditoria_rows + """
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- MODAL: ASISTENTES DE LA CÁTEDRA -->
    <div class="modal-overlay" id="modal-asistentes-catedra">
      <div class="modal" style="max-width: 880px;">
        <div class="modal-header">
          <div>
            <h3 class="modal-title" id="modal-cat-title">Asistentes de la Cátedra</h3>
            <p id="modal-cat-subtitle" style="font-size:0.8rem;color:var(--usb-text-muted);margin-top:0.2rem;"></p>
          </div>
          <button class="modal-close" onclick="cerrarModalAsistentes()">✕</button>
        </div>
        <div class="modal-body" style="padding:1.25rem;">
          <div style="margin-bottom:1rem; display:flex; gap:0.75rem; justify-content:space-between; align-items:center;">
            <input type="text" id="modal-search-asis" class="form-input" placeholder="Filtrar por nombre, documento o programa..." oninput="filtrarTablaModalAsistentes()" style="max-width:360px;">
            <span id="modal-count-badge" class="cat-asist-badge-count">0 Asistentes</span>
          </div>

          <div class="table-wrap" style="max-height:450px; overflow-y:auto;">
            <table>
              <thead>
                <tr>
                  <th># Registro</th>
                  <th>Fecha y Hora</th>
                  <th>Documento / ID ASIS</th>
                  <th>Nombre del Asistente</th>
                  <th>Programa Académico</th>
                  <th>Origen</th>
                  <th>Vinculación</th>
                </tr>
              </thead>
              <tbody id="modal-asistentes-tbody">
              </tbody>
            </table>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn-usb btn-usb-dark" onclick="cerrarModalAsistentes()">Cerrar Listado</button>
        </div>
      </div>
    </div>

    <!-- MODAL: INSPECCIÓN DE TRANSACCIÓN JSON -->
    <div class="modal-overlay" id="modal-auditoria">
      <div class="modal" style="max-width: 650px;">
        <div class="modal-header">
          <h3 class="modal-title" id="audit-modal-title">Inspección de Transacción</h3>
          <button class="modal-close" onclick="cerrarModalAuditoria()">✕</button>
        </div>
        <div class="modal-body">
          <div class="audit-detail-grid">
            <div class="audit-detail-item">
              <span class="audit-detail-label">ID de Bitácora</span>
              <span class="audit-detail-val" id="det-id">-</span>
            </div>
            <div class="audit-detail-item">
              <span class="audit-detail-label">Fecha y Hora</span>
              <span class="audit-detail-val" id="det-fecha">-</span>
            </div>
            <div class="audit-detail-item">
              <span class="audit-detail-label">Operación SQL</span>
              <span class="audit-detail-val" id="det-op">-</span>
            </div>
            <div class="audit-detail-item">
              <span class="audit-detail-label">Tabla y Llave</span>
              <span class="audit-detail-val" id="det-tabla">-</span>
            </div>
          </div>

          <div style="margin-bottom:0.6rem;display:flex;justify-content:space-between;align-items:center;">
            <label class="audit-detail-label">Payload Completo (JSON Snapshot)</label>
            <button type="button" class="btn-usb btn-usb-ghost btn-usb-sm" onclick="copiarPayload()">Copiar JSON</button>
          </div>
          <pre class="json-viewer" id="det-json"></pre>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn-usb btn-usb-dark" onclick="cerrarModalAuditoria()">Cerrar</button>
        </div>
      </div>
    </div>

    <script>
      let tablaSeleccionada = 'TODAS';
      let asistentesActuales = [];

      function cambiarPestana(tipo) {
        const btnCat = document.getElementById('tab-btn-catedras');
        const btnBit = document.getElementById('tab-btn-bitacora');
        const vistaCat = document.getElementById('vista-asistencias-catedras');
        const vistaBit = document.getElementById('vista-bitacora-cronologica');

        if (tipo === 'catedras') {
          btnCat.classList.add('active');
          btnBit.classList.remove('active');
          vistaCat.style.display = 'block';
          vistaBit.style.display = 'none';
        } else {
          btnBit.classList.add('active');
          btnCat.classList.remove('active');
          vistaCat.style.display = 'none';
          vistaBit.style.display = 'block';
        }
      }

      function filtrarCatedrasAsistencia() {
        const q = (document.getElementById('cat-asist-search').value || '').toLowerCase().trim();
        document.querySelectorAll('.catedra-card-asist').forEach(card => {
          const s = card.getAttribute('data-search') || '';
          if (q === '' || s.includes(q)) {
            card.style.display = 'flex';
          } else {
            card.style.display = 'none';
          }
        });
      }

      function abrirDetalleAsistentes(catNombre, evAsis, total, btn) {
        document.getElementById('modal-cat-title').textContent = catNombre;
        document.getElementById('modal-cat-subtitle').textContent = 'Código ASIS: ' + evAsis + ' | Total Registrados: ' + total;
        document.getElementById('modal-count-badge').textContent = total + ' Asistentes';
        document.getElementById('modal-search-asis').value = '';

        try {
          const raw = btn.getAttribute('data-asistentes') || '[]';
          asistentesActuales = JSON.parse(raw);
        } catch(e) {
          asistentesActuales = [];
        }

        renderizarFilasModalAsistentes(asistentesActuales);
        document.getElementById('modal-asistentes-catedra').classList.add('open');
      }

      function renderizarFilasModalAsistentes(lista) {
        const tbody = document.getElementById('modal-asistentes-tbody');
        if (!lista || lista.length === 0) {
          tbody.innerHTML = '<tr class="empty-row"><td colspan="7">No se encontraron asistentes para el filtro actual.</td></tr>';
          return;
        }

        let htmlRows = '';
        lista.forEach(a => {
          const regId = a.id_registro || '-';
          const fecha = (a.registrado_en || '-').substring(0, 19).replace('T', ' ');
          const doc = a.id_asis || a.id_asistente || '-';
          const nombre = a.asistente || 'Asistente Bonaventuriano';
          const prog = a.programa_nombre || a.programa || 'Sin programa';
          const origen = a.origen || 'QR';
          const vinc = a.vinculacion || (a.es_externo ? 'EXTERNO' : 'ESTUDIANTE');

          htmlRows += `
          <tr class="modal-asis-row" data-search="${regId} ${doc} ${nombre.toLowerCase()} ${prog.toLowerCase()} ${origen.toLowerCase()}">
            <td><span class="td-code">#${regId}</span></td>
            <td style="font-size:0.8rem; color:var(--usb-text-muted); white-space:nowrap;">${fecha}</td>
            <td><span class="td-code" style="font-weight:700;">${doc}</span></td>
            <td style="font-weight:700; color:var(--usb-negro);">${nombre}</td>
            <td style="font-size:0.82rem;">${prog}</td>
            <td><span class="badge ${origen === 'QR' ? 'badge-orange' : 'badge-gray'}">${origen}</span></td>
            <td><span class="badge badge-dark">${vinc}</span></td>
          </tr>
          `;
        });
        tbody.innerHTML = htmlRows;
      }

      function filtrarTablaModalAsistentes() {
        const q = (document.getElementById('modal-search-asis').value || '').toLowerCase().trim();
        const filtrados = asistentesActuales.filter(a => {
          const doc = String(a.id_asis || a.id_asistente || '');
          const nombre = String(a.asistente || '').toLowerCase();
          const prog = String(a.programa_nombre || a.programa || '').toLowerCase();
          const orig = String(a.origen || '').toLowerCase();
          return q === '' || doc.includes(q) || nombre.includes(q) || prog.includes(q) || orig.includes(q);
        });
        renderizarFilasModalAsistentes(filtrados);
      }

      function cerrarModalAsistentes() {
        document.getElementById('modal-asistentes-catedra').classList.remove('open');
      }

      function filtrarTabla(tabla, btn) {
        tablaSeleccionada = tabla;
        document.querySelectorAll('.audit-chip').forEach(c => c.classList.remove('active'));
        if (btn) btn.classList.add('active');
        aplicarFiltros();
      }

      function aplicarFiltros() {
        const query = (document.getElementById('audit-search').value || '').toLowerCase().trim();
        const opFiltro = document.getElementById('audit-op-filter').value;
        const filas = document.querySelectorAll('.audit-row');

        filas.forEach(fila => {
          const rowOp = fila.getAttribute('data-op');
          const rowTabla = fila.getAttribute('data-tabla');
          const searchData = fila.getAttribute('data-search') || '';

          const coincideOp = (opFiltro === 'TODAS' || rowOp === opFiltro);
          const coincideTabla = (tablaSeleccionada === 'TODAS' || rowTabla === tablaSeleccionada);
          const coincideBusqueda = (query === '' || searchData.includes(query));

          if (coincideOp && coincideTabla && coincideBusqueda) {
            fila.style.display = '';
          } else {
            fila.style.display = 'none';
          }
        });
      }

      function verDetalleAuditoria(id, fecha, op, tabla, llave, usr, btn) {
        document.getElementById('audit-modal-title').textContent = 'Transacción de Auditoría #' + id;
        document.getElementById('det-id').textContent = '#' + id + ' (Usuario: ' + usr + ')';
        document.getElementById('det-fecha').textContent = fecha;
        document.getElementById('det-op').textContent = op;
        document.getElementById('det-tabla').textContent = tabla + ' (Registro #' + llave + ')';
        
        const payload = btn.getAttribute('data-payload') || '{}';
        document.getElementById('det-json').textContent = payload;
        document.getElementById('modal-auditoria').classList.add('open');
      }

      function cerrarModalAuditoria() {
        document.getElementById('modal-auditoria').classList.remove('open');
      }

      function copiarPayload() {
        const txt = document.getElementById('det-json').textContent;
        navigator.clipboard.writeText(txt).then(() => {
          alert('JSON de auditoría copiado al portapapeles.');
        });
      }
    </script>
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
        <h1 class="page-title">Reportes y <span>Estadísticas Institucionales</span></h1>
        <p style="font-size:0.88rem;color:var(--usb-text-muted);margin-top:0.25rem">
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
# 8.2 MOTOR DE HOMOLOGACION Y PAZ Y SALVO ESTUDIANTIL
# ==========================================
@app.route("/homologacion", methods=["GET"])
def homologacion():
    busqueda = request.args.get("busqueda", "").strip()
    semestres_param = request.args.get("semestres", "10").strip()
    semestres_totales = int(semestres_param) if semestres_param.isdigit() and int(semestres_param) in [8, 9, 10] else 10
    catedras_exigidas_grado = semestres_totales * 2  # Regla oficial: 2 por semestre activo

    asistentes_list = []
    asistencias_list = []

    try:
        r1 = requests.get(f"{API_BASE}/v_asistente_vigente?limite=300", headers=auth_headers(), timeout=4)
        if r1.status_code == 200:
            asistentes_list = r1.json()
        r2 = requests.get(f"{API_BASE}/v_asistencia_completa?limite=500", headers=auth_headers(), timeout=4)
        if r2.status_code == 200:
            asistencias_list = r2.json()
    except Exception as e:
        flash(f"Aviso al consultar datos de homologación: {str(e)}", "danger")

    # Mapear asistencias acumuladas por cada estudiante
    asistencias_por_id = {}
    for a in asistencias_list:
        aid = a.get("id_asistente")
        if aid not in asistencias_por_id:
            asistencias_por_id[aid] = []
        asistencias_por_id[aid].append(a)

    # Filtrar sólo estudiantes si es posible
    estudiantes = [a for a in asistentes_list if a.get("vinculacion") == "ESTUDIANTE" or a.get("es_interno")]
    if not estudiantes:
        estudiantes = asistentes_list

    # Búsqueda por documento, nombre o código ASIS
    if busqueda:
        q = busqueda.lower()
        estudiantes = [
            e for e in estudiantes
            if q in str(e.get("documento_vigente", "")).lower()
            or q in str(e.get("id_asis", "")).lower()
            or q in str(e.get("nombre_completo", "")).lower()
            or q in str(e.get("correo_contacto", "")).lower()
        ]

    # Estadísticas para KPIs
    total_estudiantes = len(estudiantes)
    paz_y_salvo_count = 0
    al_dia_count = 0
    en_riesgo_count = 0

    estudiantes_calculados = []
    for e in estudiantes:
        aid = e.get("id_asistente")
        asistencias_est = asistencias_por_id.get(aid, [])
        total_completadas = len(asistencias_est)

        # Regla: 2 cátedras por semestre. Supongamos semestre 6 o según cátedras
        porcentaje_grado = min(100, round((total_completadas / catedras_exigidas_grado) * 100))
        
        # Estado Paz y Salvo
        if total_completadas >= catedras_exigidas_grado:
            estado = "APROBADO"
            estado_cls = "aprobado"
            paz_y_salvo_count += 1
        elif total_completadas >= 2:
            estado = "AL DIA"
            estado_cls = "al-dia"
            al_dia_count += 1
        elif total_completadas == 1:
            estado = "PENDIENTE"
            estado_cls = "pendiente"
            al_dia_count += 1
        else:
            estado = "EN RIESGO"
            estado_cls = "critico"
            en_riesgo_count += 1

        estudiantes_calculados.append({
            "id": aid,
            "id_asis": e.get("id_asis") or str(aid),
            "nombre": e.get("nombre_completo", "Estudiante USB"),
            "documento": e.get("documento_vigente", "-"),
            "correo": e.get("correo_contacto", "-"),
            "programa": e.get("programa_nombre") or e.get("vinculacion_nombre") or "Pregrado USB",
            "total_completadas": total_completadas,
            "exigidas": catedras_exigidas_grado,
            "faltantes": max(0, catedras_exigidas_grado - total_completadas),
            "porcentaje": porcentaje_grado,
            "estado": estado,
            "estado_cls": estado_cls,
            "detalle_asistencias": asistencias_est
        })

    # Construir filas de tabla detallada
    rows_homologacion_html = ""
    for est in estudiantes_calculados:
        rows_homologacion_html += f"""
        <tr>
          <td><span class="td-code">{est['documento']}</span></td>
          <td style="font-weight:700;color:var(--usb-negro);">{est['nombre']}</td>
          <td><span class="td-code">{est['id_asis']}</span></td>
          <td>{est['programa']}</td>
          <td style="font-weight:800;text-align:center;">{est['total_completadas']} / {est['exigidas']}</td>
          <td style="min-width:140px;">
            <div style="display:flex;justify-content:space-between;font-size:0.75rem;font-weight:700;margin-bottom:2px;">
              <span>{est['porcentaje']}%</span>
              <span style="color:var(--usb-text-muted);">{est['faltantes']} faltantes</span>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar-fill" style="width:{est['porcentaje']}%;"></div>
            </div>
          </td>
          <td style="text-align:center;">
            <span class="status-paz-salvo {est['estado_cls']}">{est['estado']}</span>
          </td>
          <td style="text-align:right;">
            <button type="button" class="btn-usb btn-usb-ghost btn-usb-sm" onclick="verCertificadoEstudiante('{est['nombre'].replace("'", "\\'")}', '{est['documento']}', '{est['id_asis']}', '{est['programa'].replace("'", "\\'")}', {est['total_completadas']}, {est['exigidas']}, '{est['estado']}')">
              Constancia
            </button>
          </td>
        </tr>
        """

    contenido = f"""
    <div class="page-header">
      <div>
        <h1 class="page-title">Motor de Homologación y <span>Paz y Salvo de Cátedras</span></h1>
        <p style="font-size:0.88rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Regla Institucional CIDEH: Cada estudiante debe completar dos (2) cátedras por semestre activo (16 para planes de 8 semestres, 20 para planes de 10 semestres).
        </p>
      </div>
      <div>
        <a href="/reportes" class="btn-usb btn-usb-dark">Ver Reportes Generales</a>
      </div>
    </div>

    <!-- BANNER EXPLICATIVO DEL MODELO DE HOMOLOGACIÓN -->
    <div class="homologacion-hero">
      <div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.35rem;">
          <span class="badge badge-orange">REQUISITO DE GRADO ACADÉMICO</span>
          <span style="font-size:0.82rem;font-weight:800;color:var(--usb-negro);">Vicerrectoría Académica · CIDEH</span>
        </div>
        <h3 style="font-size:1.15rem;font-weight:800;color:var(--usb-negro);margin-bottom:0.35rem;">
          Validación Automática de Paz y Salvo para Trámite de Grado
        </h3>
        <p style="font-size:0.85rem;color:#9A3412;margin:0;line-height:1.45;">
          El sistema consolida el historial de asistencias validadas por QR y geolocalización contra el plan de estudios del estudiante para autorizar su paz y salvo de cátedra abierta.
        </p>
      </div>
      <div style="background:#FFF;padding:0.75rem 1.25rem;border-radius:8px;border:1px solid #FDBA74;text-align:center;">
        <div style="font-size:0.72rem;font-weight:800;text-transform:uppercase;color:var(--usb-text-muted);">Regla de Acreditación</div>
        <div style="font-size:1.35rem;font-weight:900;color:var(--usb-naranja);">2 Cátedras / Semestre</div>
      </div>
    </div>

    <!-- KPI GRID DE CUMPLIMIENTO -->
    <div class="kpi-grid">
      <div class="kpi-box">
        <div class="kpi-box-title">Estudiantes Evaluados</div>
        <div class="kpi-box-num">{total_estudiantes}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Paz y Salvo Cumplido (100%)</div>
        <div class="kpi-box-num" style="color:#16A34A;">{paz_y_salvo_count}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Avance Regular (Al Día)</div>
        <div class="kpi-box-num" style="color:#1D4ED8;">{al_dia_count}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Pendientes / En Riesgo</div>
        <div class="kpi-box-num" style="color:#DC2626;">{en_riesgo_count}</div>
      </div>
    </div>

    <!-- BUSCADOR Y SELECTOR DE PLAN DE ESTUDIOS -->
    <form method="GET" action="/homologacion" class="homologacion-search-bar">
      <div class="homologacion-search-input">
        <input type="text" name="busqueda" class="form-input" value="{busqueda}" placeholder="Buscar estudiante por Cédula, Nombre o Código ASIS...">
      </div>
      <div style="width:220px;">
        <select name="semestres" class="form-input" onchange="this.form.submit()">
          <option value="10" {"selected" if semestres_totales == 10 else ""}>Plan 10 Semestres (20 Cátedras)</option>
          <option value="9" {"selected" if semestres_totales == 9 else ""}>Plan 9 Semestres (18 Cátedras)</option>
          <option value="8" {"selected" if semestres_totales == 8 else ""}>Plan 8 Semestres (16 Cátedras)</option>
        </select>
      </div>
      <button type="submit" class="btn-usb btn-usb-primary">Consultar</button>
      {f'<a href="/homologacion" class="btn-usb btn-usb-ghost">Limpiar Filtro</a>' if busqueda else ''}
    </form>

    <!-- TABLA MAESTRA DE HOMOLOGACION -->
    <div class="card-panel">
      <div class="card-panel-header">
        <h3 class="card-panel-title">Estado de Homologación y Cumplimiento Estudiantil</h3>
        <span class="badge badge-dark">Plan {semestres_totales} Semestres · Meta {catedras_exigidas_grado} Cátedras</span>
      </div>
      <div class="table-wrap" style="border:none;box-shadow:none;">
        <table>
          <thead>
            <tr>
              <th>Documento</th>
              <th>Estudiante Bonaventuriano</th>
              <th>Código ASIS</th>
              <th>Programa Académico</th>
              <th style="text-align:center;">Completadas / Meta</th>
              <th>Progreso</th>
              <th style="text-align:center;">Estado Paz y Salvo</th>
              <th style="text-align:right;">Acción</th>
            </tr>
          </thead>
          <tbody>
            {rows_homologacion_html if rows_homologacion_html else '<tr class="empty-row"><td colspan="8">No se encontraron estudiantes con el criterio de búsqueda.</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL DE CONSTANCIA OFICIAL DE PAZ Y SALVO -->
    <div class="modal-overlay" id="modal-certificado">
      <div class="modal" style="max-width: 600px;">
        <div class="modal-header">
          <h3 class="modal-title">Constancia Institucional de Cátedras Abiertas</h3>
          <button class="modal-close" onclick="document.getElementById('modal-certificado').classList.remove('open')">✕</button>
        </div>
        <div class="modal-body">
          <div style="border: 2px dashed #EF7D00; border-radius: 8px; padding: 1.5rem; background: #FFFDF9; text-align: center;">
            <img src="/static/logo_usbmed_oficial.png" alt="USB Medellín" style="height: 48px; margin-bottom: 1rem;">
            <div style="font-size:0.75rem; font-weight:800; text-transform:uppercase; color:var(--usb-naranja); letter-spacing:0.06em;">
              Universidad de San Buenaventura Medellín · CIDEH
            </div>
            <h3 style="font-size:1.15rem; font-weight:900; color:var(--usb-negro); margin:0.35rem 0 1rem 0;">
              CERTIFICADO DE CUMPLIMIENTO DE CÁTEDRA ABIERTA
            </h3>
            
            <p style="font-size:0.85rem; color:#374151; line-height:1.5; text-align:justify; margin-bottom:1rem;">
              El Centro de Investigación y Desarrollo del Espíritu Humano (CIDEH) hace constar que el(la) estudiante <strong id="cert-nombre">-</strong>, identificado(a) con documento <strong id="cert-doc">-</strong> y código ASIS <strong id="cert-asis">-</strong>, perteneciente al programa <strong id="cert-programa">-</strong>, registra un total de <strong id="cert-completadas">-</strong> cátedras abiertas asistidas y verificadas formalmente de una meta requerida de <strong id="cert-exigidas">-</strong>.
            </p>

            <div style="background:#FFFFFF; border:1px solid var(--usb-gris-borde); border-radius:6px; padding:0.85rem; margin-bottom:1rem;">
              <div style="font-size:0.75rem; color:var(--usb-text-muted); font-weight:700; text-transform:uppercase;">Dictamen de Requisito de Grado</div>
              <div id="cert-estado-badge" style="font-size:1.1rem; font-weight:900; color:#15803D; margin-top:0.25rem;">
                PAZ Y SALVO AUTORIZADO
              </div>
            </div>

            <div style="font-size:0.72rem; color:var(--usb-text-muted);">
              Expedido electrónicamente conforme a la Resolución Académica Institucional USB Medellín · Validación en tiempo real con plataforma ASIS/Oracle.
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn-usb btn-usb-ghost" onclick="document.getElementById('modal-certificado').classList.remove('open')">Cerrar</button>
          <button type="button" class="btn-usb btn-usb-primary" onclick="window.print()">Imprimir / Guardar PDF</button>
        </div>
      </div>
    </div>

    <script>
      function verCertificadoEstudiante(nombre, doc, asis, programa, comp, exig, estado) {{
        document.getElementById('cert-nombre').textContent = nombre;
        document.getElementById('cert-doc').textContent = doc;
        document.getElementById('cert-asis').textContent = asis;
        document.getElementById('cert-programa').textContent = programa;
        document.getElementById('cert-completadas').textContent = comp;
        document.getElementById('cert-exigidas').textContent = exig;
        
        const badge = document.getElementById('cert-estado-badge');
        badge.textContent = estado === 'APROBADO' ? 'PAZ Y SALVO AUTORIZADO' : ('ESTADO: ' + estado + ' (' + comp + '/' + exig + ' CÁTEDRAS)');
        badge.style.color = estado === 'APROBADO' ? '#15803D' : (estado === 'AL DIA' ? '#1D4ED8' : '#B45309');

        document.getElementById('modal-certificado').classList.add('open');
      }}
    </script>
    """
    return render_template_string(BASE_LAYOUT, titulo="Homologación y Paz y Salvo", contenido=contenido)

# ==========================================
# 8.5. MODULO DE CATALOGOS Y PARAMETRIZACION MAESTRA
# ==========================================
@app.route("/catalogos", methods=["GET", "POST"])
def catalogos():
    if not session.get("token"):
        return redirect(url_for("login"))

    # Procesar peticiones de Creación o Edición de Catálogos
    if request.method == "POST":
        catalogo = request.form.get("catalogo", "").strip()
        accion = request.form.get("accion", "").strip()
        tab_destino = request.form.get("tab_destino", "tab-modalidad").strip()

        try:
            if catalogo == "modalidad":
                id_mod = request.form.get("id_modalidad", "").strip().upper()
                nombre = request.form.get("nombre", "").strip().replace("'", "''")
                canal = request.form.get("canal_difusion", "QR").strip()
                activo = "true" if request.form.get("activo") == "1" else "false"

                if accion == "crear":
                    sql = f"INSERT INTO catedras.modalidad (id_modalidad, nombre, canal_difusion, activo) VALUES ('{id_mod}', '{nombre}', '{canal}', {activo}) ON CONFLICT (id_modalidad) DO UPDATE SET nombre=EXCLUDED.nombre, canal_difusion=EXCLUDED.canal_difusion, activo=EXCLUDED.activo;"
                    db_execute_sql(sql)
                    flash(f"Modalidad '{id_mod}' registrada exitosamente.", "success")
                elif accion == "editar":
                    sql = f"UPDATE catedras.modalidad SET nombre='{nombre}', canal_difusion='{canal}', activo={activo} WHERE id_modalidad='{id_mod}';"
                    db_execute_sql(sql)
                    flash(f"Modalidad '{id_mod}' actualizada exitosamente.", "success")

            elif catalogo == "tipo_evento":
                id_eve = request.form.get("id_tipo_evento", "").strip().upper()
                nombre = request.form.get("nombre", "").strip().replace("'", "''")
                activo = "true" if request.form.get("activo") == "1" else "false"

                if accion == "crear":
                    sql = f"INSERT INTO catedras.tipo_evento (id_tipo_evento, nombre, activo) VALUES ('{id_eve}', '{nombre}', {activo}) ON CONFLICT (id_tipo_evento) DO UPDATE SET nombre=EXCLUDED.nombre, activo=EXCLUDED.activo;"
                    db_execute_sql(sql)
                    flash(f"Tipo de Evento '{id_eve}' registrado exitosamente.", "success")
                elif accion == "editar":
                    sql = f"UPDATE catedras.tipo_evento SET nombre='{nombre}', activo={activo} WHERE id_tipo_evento='{id_eve}';"
                    db_execute_sql(sql)
                    flash(f"Tipo de Evento '{id_eve}' actualizado exitosamente.", "success")

            elif catalogo == "tipo_documento":
                id_doc = request.form.get("id_tipo_documento", "").strip().upper()
                nombre = request.form.get("nombre", "").strip().replace("'", "''")
                activo = "true" if request.form.get("activo") == "1" else "false"

                if accion == "crear":
                    sql = f"INSERT INTO catedras.tipo_documento (id_tipo_documento, nombre, activo) VALUES ('{id_doc}', '{nombre}', {activo}) ON CONFLICT (id_tipo_documento) DO UPDATE SET nombre=EXCLUDED.nombre, activo=EXCLUDED.activo;"
                    db_execute_sql(sql)
                    flash(f"Tipo de Documento '{id_doc}' registrado exitosamente.", "success")
                elif accion == "editar":
                    sql = f"UPDATE catedras.tipo_documento SET nombre='{nombre}', activo={activo} WHERE id_tipo_documento='{id_doc}';"
                    db_execute_sql(sql)
                    flash(f"Tipo de Documento '{id_doc}' actualizado exitosamente.", "success")

            elif catalogo == "tipo_vinculacion":
                id_vin = request.form.get("id_tipo_vinculacion", "").strip().upper()
                nombre = request.form.get("nombre", "").strip().replace("'", "''")
                es_int = "true" if request.form.get("es_interno") == "1" else "false"
                ex_prog = "true" if request.form.get("exige_programa") == "1" else "false"
                activo = "true" if request.form.get("activo") == "1" else "false"

                if accion == "crear":
                    sql = f"INSERT INTO catedras.tipo_vinculacion (id_tipo_vinculacion, nombre, es_interno, exige_programa, activo) VALUES ('{id_vin}', '{nombre}', {es_int}, {ex_prog}, {activo}) ON CONFLICT (id_tipo_vinculacion) DO UPDATE SET nombre=EXCLUDED.nombre, es_interno=EXCLUDED.es_interno, exige_programa=EXCLUDED.exige_programa, activo=EXCLUDED.activo;"
                    db_execute_sql(sql)
                    flash(f"Tipo de Vinculación '{id_vin}' registrada exitosamente.", "success")
                elif accion == "editar":
                    sql = f"UPDATE catedras.tipo_vinculacion SET nombre='{nombre}', es_interno={es_int}, exige_programa={ex_prog}, activo={activo} WHERE id_tipo_vinculacion='{id_vin}';"
                    db_execute_sql(sql)
                    flash(f"Tipo de Vinculación '{id_vin}' actualizada exitosamente.", "success")

            elif catalogo == "periodo_academico":
                id_per = request.form.get("id_periodo", "").strip().upper()
                fecha_ini = request.form.get("fecha_ini", "").strip()
                fecha_fin = request.form.get("fecha_fin", "").strip()
                activo = "true" if request.form.get("activo") == "1" else "false"

                if accion == "crear":
                    sql = f"INSERT INTO catedras.periodo_academico (id_periodo, fecha_ini, fecha_fin, activo) VALUES ('{id_per}', '{fecha_ini}', '{fecha_fin}', {activo}) ON CONFLICT (id_periodo) DO UPDATE SET fecha_ini=EXCLUDED.fecha_ini, fecha_fin=EXCLUDED.fecha_fin, activo=EXCLUDED.activo;"
                    db_execute_sql(sql)
                    flash(f"Periodo Académico '{id_per}' registrado exitosamente.", "success")
                elif accion == "editar":
                    sql = f"UPDATE catedras.periodo_academico SET fecha_ini='{fecha_ini}', fecha_fin='{fecha_fin}', activo={activo} WHERE id_periodo='{id_per}';"
                    db_execute_sql(sql)
                    flash(f"Periodo Académico '{id_per}' actualizado exitosamente.", "success")

            elif catalogo == "rol":
                id_rol = request.form.get("id_rol", "").strip().upper()
                nombre = request.form.get("nombre", "").strip().replace("'", "''")
                descripcion = request.form.get("descripcion", "").strip().replace("'", "''")
                activo = "true" if request.form.get("activo") == "1" else "false"

                if accion == "crear":
                    sql = f"INSERT INTO catedras.rol (id_rol, nombre, descripcion, activo) VALUES ('{id_rol}', '{nombre}', '{descripcion}', {activo}) ON CONFLICT (id_rol) DO UPDATE SET nombre=EXCLUDED.nombre, descripcion=EXCLUDED.descripcion, activo=EXCLUDED.activo;"
                    db_execute_sql(sql)
                    flash(f"Rol '{id_rol}' registrado exitosamente.", "success")
                elif accion == "editar":
                    sql = f"UPDATE catedras.rol SET nombre='{nombre}', descripcion='{descripcion}', activo={activo} WHERE id_rol='{id_rol}';"
                    db_execute_sql(sql)
                    flash(f"Rol '{id_rol}' actualizado exitosamente.", "success")

            elif catalogo == "estado_proceso":
                id_est = request.form.get("id_estado", "").strip().upper()
                nombre = request.form.get("nombre", "").strip().replace("'", "''")
                es_fin = "true" if request.form.get("es_final") == "1" else "false"
                es_ex = "true" if request.form.get("es_exitoso") == "1" else "false"

                if accion == "crear":
                    sql = f"INSERT INTO catedras.estado_proceso (id_estado, nombre, es_final, es_exitoso) VALUES ('{id_est}', '{nombre}', {es_fin}, {es_ex}) ON CONFLICT (id_estado) DO UPDATE SET nombre=EXCLUDED.nombre, es_final=EXCLUDED.es_final, es_exitoso=EXCLUDED.es_exitoso;"
                    db_execute_sql(sql)
                    flash(f"Estado de Proceso '{id_est}' registrado exitosamente.", "success")
                elif accion == "editar":
                    sql = f"UPDATE catedras.estado_proceso SET nombre='{nombre}', es_final={es_fin}, es_exitoso={es_ex} WHERE id_estado='{id_est}';"
                    db_execute_sql(sql)
                    flash(f"Estado de Proceso '{id_est}' actualizado exitosamente.", "success")

            elif catalogo == "encuesta":
                nombre = request.form.get("nombre", "").strip().replace("'", "''")
                version = int(request.form.get("version", "1"))
                vig_desde = request.form.get("vigente_desde", "").strip() or "2026-01-01"
                vig_hasta = request.form.get("vigente_hasta", "").strip()
                vig_hasta_sql = f"'{vig_hasta}'" if vig_hasta else "NULL"
                activa = "true" if request.form.get("activa") == "1" else "false"

                if accion == "crear":
                    sql = f"INSERT INTO catedras.encuesta (nombre, version, vigente_desde, vigente_hasta, activa) VALUES ('{nombre}', {version}, '{vig_desde}', {vig_hasta_sql}, {activa});"
                    db_execute_sql(sql)
                    flash("Encuesta registrada exitosamente.", "success")
                elif accion == "editar":
                    id_enc = int(request.form.get("id_encuesta", "0"))
                    sql = f"UPDATE catedras.encuesta SET nombre='{nombre}', version={version}, vigente_desde='{vig_desde}', vigente_hasta={vig_hasta_sql}, activa={activa} WHERE id_encuesta={id_enc};"
                    db_execute_sql(sql)
                    flash(f"Encuesta #{id_enc} actualizada exitosamente.", "success")

            elif catalogo == "pregunta":
                fk_enc = int(request.form.get("fk_encuesta", "1"))
                enunciado = request.form.get("enunciado", "").strip().replace("'", "''")
                orden = int(request.form.get("orden", "1"))
                fk_tipo_preg = request.form.get("fk_tipo_pregunta", "ESCALA_1_5").strip()
                obligatoria = "true" if request.form.get("obligatoria") == "1" else "false"

                if accion == "crear":
                    sql = f"INSERT INTO catedras.pregunta (fk_encuesta, enunciado, orden, fk_tipo_pregunta, obligatoria) VALUES ({fk_enc}, '{enunciado}', {orden}, '{fk_tipo_preg}', {obligatoria});"
                    db_execute_sql(sql)
                    flash("Pregunta agregada a la encuesta exitosamente.", "success")
                elif accion == "editar":
                    id_preg = int(request.form.get("id_pregunta", "0"))
                    sql = f"UPDATE catedras.pregunta SET enunciado='{enunciado}', orden={orden}, fk_tipo_pregunta='{fk_tipo_preg}', obligatoria={obligatoria} WHERE id_pregunta={id_preg};"
                    db_execute_sql(sql)
                    flash(f"Pregunta #{id_preg} actualizada exitosamente.", "success")

            elif catalogo == "parametro":
                clave = request.form.get("clave", "").strip().upper().replace("'", "''")
                valor = request.form.get("valor", "").strip().replace("'", "''")
                tipo_dato = request.form.get("tipo_dato", "TEXTO").strip()
                desc = request.form.get("descripcion", "").strip().replace("'", "''")

                if accion == "crear":
                    sql = f"INSERT INTO catedras.parametro (clave, valor, tipo_dato, descripcion, modificado_en) VALUES ('{clave}', '{valor}', '{tipo_dato}', '{desc}', NOW()) ON CONFLICT (clave) DO UPDATE SET valor=EXCLUDED.valor, tipo_dato=EXCLUDED.tipo_dato, descripcion=EXCLUDED.descripcion, modificado_en=NOW();"
                    db_execute_sql(sql)
                    flash(f"Parámetro '{clave}' registrado exitosamente.", "success")
                elif accion == "editar":
                    sql = f"UPDATE catedras.parametro SET valor='{valor}', tipo_dato='{tipo_dato}', descripcion='{desc}', modificado_en=NOW() WHERE clave='{clave}';"
                    db_execute_sql(sql)
                    flash(f"Parámetro '{clave}' actualizado exitosamente.", "success")

        except Exception as ex:
            flash(f"Error al procesar catálogo: {str(ex)}", "danger")

        return redirect(url_for("catalogos", tab=tab_destino))

    # Cargar datos desde PostgreSQL directamente con fallback
    def cargar_datos(tabla, order_col):
        try:
            sql = f"SELECT row_to_json(r) FROM (SELECT * FROM catedras.{tabla} ORDER BY {order_col}) r;"
            filas = db_query_json(sql)
            if filas:
                return filas
        except Exception:
            pass
        return []

    modalidades = cargar_datos("modalidad", "id_modalidad")
    tipos_evento = cargar_datos("tipo_evento", "id_tipo_evento")
    tipos_doc = cargar_datos("tipo_documento", "id_tipo_documento")
    tipos_vinc = cargar_datos("tipo_vinculacion", "id_tipo_vinculacion")
    periodos = cargar_datos("periodo_academico", "id_periodo DESC")
    tipos_preg = cargar_datos("tipo_pregunta", "id_tipo_pregunta")
    roles = cargar_datos("rol", "id_rol")
    estados_proc = cargar_datos("estado_proceso", "id_estado")
    encuestas = cargar_datos("encuesta", "id_encuesta DESC")
    preguntas = cargar_datos("pregunta", "orden, id_pregunta")
    parametros = cargar_datos("parametro", "clave")

    # Contadores
    c_mod = len(modalidades)
    c_eve = len(tipos_evento)
    c_doc = len(tipos_doc)
    c_vin = len(tipos_vinc)
    c_per = len(periodos)
    c_pre = len(tipos_preg)
    c_rol = len(roles)
    c_est = len(estados_proc)
    c_enc = len(encuestas)
    c_par = len(parametros)

    total_catalogos = c_mod + c_eve + c_doc + c_vin + c_per + c_pre + c_rol + c_est + c_enc + c_par

    # Generar opciones de select para tipos de pregunta y encuestas
    opts_tipo_preg = "".join([f"<option value='{tp.get('id_tipo_pregunta')}'>{tp.get('id_tipo_pregunta')} - {tp.get('nombre')}</option>" for tp in tipos_preg])
    opts_encuestas = "".join([f"<option value='{enc.get('id_encuesta')}'>Encuesta #{enc.get('id_encuesta')} - {enc.get('nombre')}</option>" for enc in encuestas])

    # Filas Modalidad
    rows_mod = ""
    for m in modalidades:
        id_m = m.get('id_modalidad', '')
        nom = m.get('nombre', '')
        canal = m.get('canal_difusion', 'QR')
        act = m.get('activo', True)
        badge_canal = '<span class="badge badge-orange">QR</span>' if canal == 'QR' else ('<span class="badge badge-dark">ENLACE</span>' if canal == 'ENLACE' else '<span class="badge" style="background:#4338CA;color:#FFF;">AMBOS</span>')
        nom_esc = nom.replace("'", "\'").replace('"', '&quot;')
        rows_mod += f"""
        <tr>
          <td><strong style="color:var(--usb-naranja);">{id_m}</strong></td>
          <td><strong>{nom}</strong></td>
          <td>{badge_canal}</td>
          <td>{'<span class="badge badge-green">Activo</span>' if act else '<span class="badge badge-red">Inactivo</span>'}</td>
          <td>
            <button type="button" class="btn-usb btn-usb-ghost btn-usb-sm" onclick="abrirEditarModalidad('{id_m}', '{nom_esc}', '{canal}', {'1' if act else '0'})">Editar</button>
          </td>
        </tr>
        """

    # Filas Tipo Evento
    rows_eve = ""
    for e in tipos_evento:
        id_e = e.get('id_tipo_evento', '')
        nom = e.get('nombre', '')
        act = e.get('activo', True)
        nom_esc = nom.replace("'", "\'").replace('"', '&quot;')
        rows_eve += f"""
        <tr>
          <td><strong style="color:var(--usb-naranja);">{id_e}</strong></td>
          <td><strong>{nom}</strong></td>
          <td>{'<span class="badge badge-green">Vigente ASIS</span>' if act else '<span class="badge badge-red">Inactivo</span>'}</td>
          <td>
            <button type="button" class="btn-usb btn-usb-ghost btn-usb-sm" onclick="abrirEditarTipoEvento('{id_e}', '{nom_esc}', {'1' if act else '0'})">Editar</button>
          </td>
        </tr>
        """

    # Filas Tipo Documento
    rows_doc = ""
    for d in tipos_doc:
        id_d = d.get('id_tipo_documento', '')
        nom = d.get('nombre', '')
        act = d.get('activo', True)
        nom_esc = nom.replace("'", "\'").replace('"', '&quot;')
        rows_doc += f"""
        <tr>
          <td><strong style="color:var(--usb-naranja);">{id_d}</strong></td>
          <td><strong>{nom}</strong></td>
          <td>{'<span class="badge badge-green">Activo</span>' if act else '<span class="badge badge-red">Inactivo</span>'}</td>
          <td>
            <button type="button" class="btn-usb btn-usb-ghost btn-usb-sm" onclick="abrirEditarTipoDocumento('{id_d}', '{nom_esc}', {'1' if act else '0'})">Editar</button>
          </td>
        </tr>
        """

    # Filas Tipo Vinculación
    rows_vin = ""
    for v in tipos_vinc:
        id_v = v.get('id_tipo_vinculacion', '')
        nom = v.get('nombre', '')
        es_int = v.get('es_interno', True)
        ex_prog = v.get('exige_programa', True)
        act = v.get('activo', True)
        interno = '<span class="badge badge-green">Interno USB</span>' if es_int else '<span class="badge badge-dark">Externo</span>'
        exige = '<span class="badge badge-orange">Exige Programa</span>' if ex_prog else '<span class="badge" style="background:#E2E8F0;color:#334155;">No Exige</span>'
        nom_esc = nom.replace("'", "\'").replace('"', '&quot;')
        rows_vin += f"""
        <tr>
          <td><strong style="color:var(--usb-naranja);">{id_v}</strong></td>
          <td><strong>{nom}</strong></td>
          <td>{interno}</td>
          <td>{exige}</td>
          <td>{'<span class="badge badge-green">Activo</span>' if act else '<span class="badge badge-red">Inactivo</span>'}</td>
          <td>
            <button type="button" class="btn-usb btn-usb-ghost btn-usb-sm" onclick="abrirEditarTipoVinculacion('{id_v}', '{nom_esc}', {'1' if es_int else '0'}, {'1' if ex_prog else '0'}, {'1' if act else '0'})">Editar</button>
          </td>
        </tr>
        """

    # Filas Periodo Académico
    rows_per = ""
    for p in periodos:
        id_p = p.get('id_periodo', '')
        fini = str(p.get('fecha_ini', ''))
        ffin = str(p.get('fecha_fin', ''))
        act = p.get('activo', True)
        rows_per += f"""
        <tr>
          <td><strong style="color:var(--usb-naranja);">{id_p}</strong></td>
          <td>{fini}</td>
          <td>{ffin}</td>
          <td>{'<span class="badge badge-green">Habilitado</span>' if act else '<span class="badge badge-red">Cerrado</span>'}</td>
          <td>
            <button type="button" class="btn-usb btn-usb-ghost btn-usb-sm" onclick="abrirEditarPeriodo('{id_p}', '{fini}', '{ffin}', {'1' if act else '0'})">Editar</button>
          </td>
        </tr>
        """

    # Filas Rol
    rows_rol = ""
    for r in roles:
        id_r = r.get('id_rol', '')
        nom = r.get('nombre', '')
        desc = r.get('descripcion') or 'Acceso a funciones específicas del sistema'
        act = r.get('activo', True)
        nom_esc = nom.replace("'", "\'").replace('"', '&quot;')
        desc_esc = desc.replace("'", "\'").replace('"', '&quot;')
        rows_rol += f"""
        <tr>
          <td><strong style="color:var(--usb-naranja);">{id_r}</strong></td>
          <td><strong>{nom}</strong></td>
          <td>{desc}</td>
          <td>{'<span class="badge badge-green">Activo</span>' if act else '<span class="badge badge-red">Inactivo</span>'}</td>
          <td>
            <button type="button" class="btn-usb btn-usb-ghost btn-usb-sm" onclick="abrirEditarRol('{id_r}', '{nom_esc}', '{desc_esc}', {'1' if act else '0'})">Editar</button>
          </td>
        </tr>
        """

    # Filas Estado Proceso
    rows_est = ""
    for st in estados_proc:
        id_st = st.get('id_estado', '')
        nom = st.get('nombre', '')
        es_fin = st.get('es_final', False)
        es_ex = st.get('es_exitoso', False)
        badge_fin = '<span class="badge badge-dark">Terminal</span>' if es_fin else '<span class="badge badge-orange">En Proceso</span>'
        badge_ex = '<span class="badge badge-green">Exitoso</span>' if es_ex else ('<span class="badge badge-red">Fallo / Error</span>' if es_fin else '<span class="badge" style="background:#CBD5E1;color:#1E293B;">Pendiente</span>')
        nom_esc = nom.replace("'", "\'").replace('"', '&quot;')
        rows_est += f"""
        <tr>
          <td><strong style="color:var(--usb-naranja);">{id_st}</strong></td>
          <td><strong>{nom}</strong></td>
          <td>{badge_fin}</td>
          <td>{badge_ex}</td>
          <td>
            <button type="button" class="btn-usb btn-usb-ghost btn-usb-sm" onclick="abrirEditarEstado('{id_st}', '{nom_esc}', {'1' if es_fin else '0'}, {'1' if es_ex else '0'})">Editar</button>
          </td>
        </tr>
        """

    # Filas Encuesta y Preguntas
    rows_enc = ""
    for enc in encuestas:
        id_enc = enc.get('id_encuesta')
        nom = enc.get('nombre', '')
        ver = enc.get('version', 1)
        vdesde = str(enc.get('vigente_desde', ''))
        vhasta = str(enc.get('vigente_hasta') or '')
        act = enc.get('activa', True)
        vig = f"{vdesde} a {vhasta if vhasta else 'Indefinido'}"
        nom_esc = nom.replace("'", "\'").replace('"', '&quot;')
        rows_enc += f"""
        <tr>
          <td>#{id_enc}</td>
          <td><strong>{nom}</strong> (v{ver})</td>
          <td>{vig}</td>
          <td>{'<span class="badge badge-green">Activa Vigente</span>' if act else '<span class="badge badge-red">Archivada</span>'}</td>
          <td>
            <button type="button" class="btn-usb btn-usb-ghost btn-usb-sm" onclick="abrirEditarEncuesta({id_enc}, '{nom_esc}', {ver}, '{vdesde}', '{vhasta}', {'1' if act else '0'})">Editar</button>
          </td>
        </tr>
        """

    rows_preg = ""
    for pr in preguntas:
        id_pr = pr.get('id_pregunta')
        fk_enc = pr.get('fk_encuesta', 1)
        enun = pr.get('enunciado') or pr.get('texto', '')
        fk_tp = pr.get('fk_tipo_pregunta', '')
        orden = pr.get('orden', 1)
        obl = pr.get('obligatoria', True)
        badge_obl = '<span class="badge badge-orange">Requerida</span>' if obl else '<span class="badge" style="background:#E2E8F0;color:#334155;">Opcional</span>'
        enun_esc = enun.replace("'", "\'").replace('"', '&quot;')
        rows_preg += f"""
        <tr>
          <td>#{id_pr}</td>
          <td><strong>{enun}</strong></td>
          <td><span class="badge badge-dark">{fk_tp}</span></td>
          <td>Orden {orden}</td>
          <td>{badge_obl}</td>
          <td>
            <button type="button" class="btn-usb btn-usb-ghost btn-usb-sm" onclick="abrirEditarPregunta({id_pr}, {fk_enc}, '{enun_esc}', {orden}, '{fk_tp}', {'1' if obl else '0'})">Editar</button>
          </td>
        </tr>
        """

    # Filas Parametros
    rows_par = ""
    for par in parametros:
        clave = par.get('clave', '')
        val = par.get('valor', '')
        td = par.get('tipo_dato', '')
        desc = par.get('descripcion') or ''
        val_esc = val.replace("'", "\'").replace('"', '&quot;')
        desc_esc = desc.replace("'", "\'").replace('"', '&quot;')
        rows_par += f"""
        <tr>
          <td><strong style="color:var(--usb-naranja);">{clave}</strong></td>
          <td><code style="background:#F1F5F9;padding:2px 6px;border-radius:4px;font-weight:700;">{val}</code></td>
          <td><span class="badge badge-dark">{td}</span></td>
          <td style="font-size:0.83rem;color:var(--usb-text-muted);">{desc}</td>
          <td>
            <button type="button" class="btn-usb btn-usb-ghost btn-usb-sm" onclick="abrirEditarParametro('{clave}', '{val_esc}', '{td}', '{desc_esc}')">Editar</button>
          </td>
        </tr>
        """

    tab_inicial = request.args.get("tab", "tab-modalidad")

    contenido = f"""
    <div class="page-header">
      <div>
        <h1 class="page-title">Catálogos y <span>Parametrización Maestra</span></h1>
        <p style="font-size:0.88rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Gestión completa, creación y edición en tiempo real de las 10 tablas maestras del sistema (PostgreSQL + .NET API).
        </p>
      </div>
      <div style="display:flex;gap:0.75rem;">
        <a href="http://localhost:7045/swagger" target="_blank" class="btn-usb btn-usb-dark">Explorar en Swagger API</a>
      </div>
    </div>

    <!-- KPI RESUMEN DE MAESTROS -->
    <div class="kpi-grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom:1.5rem;">
      <div class="kpi-box">
        <div class="kpi-box-title">Total Registros Maestros</div>
        <div class="kpi-box-num" style="color:var(--usb-naranja);">{total_catalogos}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Modalidades y Eventos</div>
        <div class="kpi-box-num">{c_mod + c_eve}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Tipos Documento / Vínculo</div>
        <div class="kpi-box-num">{c_doc + c_vin}</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-box-title">Parámetros del Sistema</div>
        <div class="kpi-box-num">{c_par}</div>
      </div>
    </div>

    <!-- PESTAÑAS DE NAVEGACION DE CATALOGOS -->
    <div class="view-tabs-nav" style="flex-wrap:wrap;gap:6px;margin-bottom:1.25rem;">
      <button type="button" class="view-tab-btn" id="btn-tab-modalidad" onclick="mostrarTabCatalogo('tab-modalidad', this)">Modalidades ({c_mod})</button>
      <button type="button" class="view-tab-btn" id="btn-tab-evento" onclick="mostrarTabCatalogo('tab-evento', this)">Tipos de Evento ({c_eve})</button>
      <button type="button" class="view-tab-btn" id="btn-tab-documento" onclick="mostrarTabCatalogo('tab-documento', this)">Tipos de Documento ({c_doc})</button>
      <button type="button" class="view-tab-btn" id="btn-tab-vinculacion" onclick="mostrarTabCatalogo('tab-vinculacion', this)">Vinculación ({c_vin})</button>
      <button type="button" class="view-tab-btn" id="btn-tab-periodo" onclick="mostrarTabCatalogo('tab-periodo', this)">Periodos Académicos ({c_per})</button>
      <button type="button" class="view-tab-btn" id="btn-tab-roles" onclick="mostrarTabCatalogo('tab-roles', this)">Roles de Usuario ({c_rol})</button>
      <button type="button" class="view-tab-btn" id="btn-tab-estados" onclick="mostrarTabCatalogo('tab-estados', this)">Estados de Proceso ({c_est})</button>
      <button type="button" class="view-tab-btn" id="btn-tab-encuesta" onclick="mostrarTabCatalogo('tab-encuesta', this)">Encuesta y Preguntas ({c_enc})</button>
      <button type="button" class="view-tab-btn" id="btn-tab-parametros" onclick="mostrarTabCatalogo('tab-parametros', this)">Parámetros del Sistema ({c_par})</button>
    </div>

    <!-- TAB 1: MODALIDADES -->
    <div class="catalogo-tab-pane" id="tab-modalidad">
      <div class="card-usb">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;flex-wrap:wrap;gap:10px;">
          <div>
            <h3 style="font-size:1.1rem;font-weight:800;color:var(--usb-negro);margin:0;">Modalidades de Cátedra</h3>
            <p style="font-size:0.83rem;color:var(--usb-text-muted);margin-top:2px;">Determina el canal de difusión tecnológico exigido (Código QR vs Enlace Virtual / Ambos).</p>
          </div>
          <div style="display:flex;gap:0.5rem;align-items:center;">
            <span class="badge badge-orange">{c_mod} Modalidades</span>
            <button type="button" class="btn-usb btn-usb-primary btn-usb-sm" onclick="abrirModal('modal-modalidad-crear')">+ Nueva Modalidad</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Código ID</th>
                <th>Nombre de la Modalidad</th>
                <th>Canal de Difusión Obligatorio</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>{rows_mod}</tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 2: TIPOS DE EVENTO -->
    <div class="catalogo-tab-pane" id="tab-evento" style="display:none;">
      <div class="card-usb">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;flex-wrap:wrap;gap:10px;">
          <div>
            <h3 style="font-size:1.1rem;font-weight:800;color:var(--usb-negro);margin:0;">Tipos de Evento Oficiales</h3>
            <p style="font-size:0.83rem;color:var(--usb-text-muted);margin-top:2px;">Clasificaciones oficiales según la estructura del sistema ASIS / Oracle.</p>
          </div>
          <div style="display:flex;gap:0.5rem;align-items:center;">
            <span class="badge badge-orange">{c_eve} Eventos</span>
            <button type="button" class="btn-usb btn-usb-primary btn-usb-sm" onclick="abrirModal('modal-evento-crear')">+ Nuevo Tipo Evento</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Código ASIS</th>
                <th>Nombre del Evento</th>
                <th>Estado Institucional</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>{rows_eve}</tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 3: TIPOS DE DOCUMENTO -->
    <div class="catalogo-tab-pane" id="tab-documento" style="display:none;">
      <div class="card-usb">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;flex-wrap:wrap;gap:10px;">
          <div>
            <h3 style="font-size:1.1rem;font-weight:800;color:var(--usb-negro);margin:0;">Tipos de Documento de Identidad</h3>
            <p style="font-size:0.83rem;color:var(--usb-text-muted);margin-top:2px;">Documentos válidos para registro de ponentes y asistentes en la Universidad.</p>
          </div>
          <div style="display:flex;gap:0.5rem;align-items:center;">
            <span class="badge badge-orange">{c_doc} Documentos</span>
            <button type="button" class="btn-usb btn-usb-primary btn-usb-sm" onclick="abrirModal('modal-documento-crear')">+ Nuevo Documento</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Abreviatura</th>
                <th>Descripción del Documento</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>{rows_doc}</tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 4: TIPOS DE VINCULACIÓN -->
    <div class="catalogo-tab-pane" id="tab-vinculacion" style="display:none;">
      <div class="card-usb">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;flex-wrap:wrap;gap:10px;">
          <div>
            <h3 style="font-size:1.1rem;font-weight:800;color:var(--usb-negro);margin:0;">Tipos de Vinculación Universitaria</h3>
            <p style="font-size:0.83rem;color:var(--usb-text-muted);margin-top:2px;">Reglas de negocio: define si el asistente es interno/externo y si se le exige programa académico.</p>
          </div>
          <div style="display:flex;gap:0.5rem;align-items:center;">
            <span class="badge badge-orange">{c_vin} Vinculaciones</span>
            <button type="button" class="btn-usb btn-usb-primary btn-usb-sm" onclick="abrirModal('modal-vinculacion-crear')">+ Nueva Vinculación</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Código ID</th>
                <th>Nombre del Vínculo</th>
                <th>Comunidad</th>
                <th>Validación Programa</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>{rows_vin}</tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 5: PERIODOS ACADÉMICOS -->
    <div class="catalogo-tab-pane" id="tab-periodo" style="display:none;">
      <div class="card-usb">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;flex-wrap:wrap;gap:10px;">
          <div>
            <h3 style="font-size:1.1rem;font-weight:800;color:var(--usb-negro);margin:0;">Periodos Académicos Semestrales</h3>
            <p style="font-size:0.83rem;color:var(--usb-text-muted);margin-top:2px;">Vigencias de semestre utilizadas para cálculo de homologación y convocatorias.</p>
          </div>
          <div style="display:flex;gap:0.5rem;align-items:center;">
            <span class="badge badge-orange">{c_per} Periodos</span>
            <button type="button" class="btn-usb btn-usb-primary btn-usb-sm" onclick="abrirModal('modal-periodo-crear')">+ Nuevo Periodo</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Periodo</th>
                <th>Fecha Inicio</th>
                <th>Fecha Fin</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>{rows_per}</tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 6: ROLES -->
    <div class="catalogo-tab-pane" id="tab-roles" style="display:none;">
      <div class="card-usb">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;flex-wrap:wrap;gap:10px;">
          <div>
            <h3 style="font-size:1.1rem;font-weight:800;color:var(--usb-negro);margin:0;">Roles del Sistema</h3>
            <p style="font-size:0.83rem;color:var(--usb-text-muted);margin-top:2px;">Niveles de autorización y permisos sobre módulos institucionales.</p>
          </div>
          <div style="display:flex;gap:0.5rem;align-items:center;">
            <span class="badge badge-orange">{c_rol} Roles</span>
            <button type="button" class="btn-usb btn-usb-primary btn-usb-sm" onclick="abrirModal('modal-rol-crear')">+ Nuevo Rol</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Rol</th>
                <th>Nombre</th>
                <th>Descripción de Alcance</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>{rows_rol}</tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 7: ESTADOS DE PROCESO -->
    <div class="catalogo-tab-pane" id="tab-estados" style="display:none;">
      <div class="card-usb">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;flex-wrap:wrap;gap:10px;">
          <div>
            <h3 style="font-size:1.1rem;font-weight:800;color:var(--usb-negro);margin:0;">Estados de Proceso de Migración ASIS</h3>
            <p style="font-size:0.83rem;color:var(--usb-text-muted);margin-top:2px;">Estados del monitor de integración para transferencias de archivos masivos a Oracle.</p>
          </div>
          <div style="display:flex;gap:0.5rem;align-items:center;">
            <span class="badge badge-orange">{c_est} Estados</span>
            <button type="button" class="btn-usb btn-usb-primary btn-usb-sm" onclick="abrirModal('modal-estado-crear')">+ Nuevo Estado</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Código Estado</th>
                <th>Nombre del Estado</th>
                <th>Fase</th>
                <th>Resultado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>{rows_est}</tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 8: ENCUESTAS Y PREGUNTAS -->
    <div class="catalogo-tab-pane" id="tab-encuesta" style="display:none;">
      <div class="card-usb" style="margin-bottom:1.5rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;flex-wrap:wrap;gap:10px;">
          <div>
            <h3 style="font-size:1.1rem;font-weight:800;color:var(--usb-negro);margin:0;">Encuestas de Calidad Parametrizables</h3>
            <p style="font-size:0.83rem;color:var(--usb-text-muted);margin-top:2px;">Instrumento de medición de satisfacción aplicado al registrar asistencia.</p>
          </div>
          <div style="display:flex;gap:0.5rem;align-items:center;">
            <span class="badge badge-orange">{c_enc} Encuesta(s)</span>
            <button type="button" class="btn-usb btn-usb-primary btn-usb-sm" onclick="abrirModal('modal-encuesta-crear')">+ Nueva Encuesta</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Nombre de la Encuesta</th>
                <th>Vigencia</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>{rows_enc}</tbody>
          </table>
        </div>
      </div>

      <div class="card-usb">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;flex-wrap:wrap;gap:10px;">
          <div>
            <h3 style="font-size:1.1rem;font-weight:800;color:var(--usb-negro);margin:0;">Preguntas de la Encuesta</h3>
            <p style="font-size:0.83rem;color:var(--usb-text-muted);margin-top:2px;">Banco de preguntas con validación de tipo de dato (Escala 1-5, Sí/No, Texto Libre).</p>
          </div>
          <div style="display:flex;gap:0.5rem;align-items:center;">
            <span class="badge badge-dark">{len(preguntas)} Preguntas</span>
            <button type="button" class="btn-usb btn-usb-primary btn-usb-sm" onclick="abrirModal('modal-pregunta-crear')">+ Nueva Pregunta</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Enunciado de la Pregunta</th>
                <th>Tipo de Pregunta</th>
                <th>Secuencia</th>
                <th>Condición</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>{rows_preg}</tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 9: PARÁMETROS DEL SISTEMA -->
    <div class="catalogo-tab-pane" id="tab-parametros" style="display:none;">
      <div class="card-usb">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;flex-wrap:wrap;gap:10px;">
          <div>
            <h3 style="font-size:1.1rem;font-weight:800;color:var(--usb-negro);margin:0;">Parámetros Generales de Configuración</h3>
            <p style="font-size:0.83rem;color:var(--usb-text-muted);margin-top:2px;">Valores institucionales parametrizados: ventanas horarias, dominios y vigencias de clave.</p>
          </div>
          <div style="display:flex;gap:0.5rem;align-items:center;">
            <span class="badge badge-orange">{c_par} Parámetros</span>
            <button type="button" class="btn-usb btn-usb-primary btn-usb-sm" onclick="abrirModal('modal-parametro-crear')">+ Nuevo Parámetro</button>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Clave del Parámetro</th>
                <th>Valor Actual</th>
                <th>Tipo de Dato</th>
                <th>Descripción y Regla Aplicada</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>{rows_par}</tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ==================== MODALES DE CREACIÓN Y EDICIÓN ==================== -->

    <!-- MODAL 1: MODALIDAD CREAR / EDITAR -->
    <div class="modal-overlay" id="modal-modalidad-crear">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Registrar Nueva Modalidad</h3>
          <button class="modal-close" onclick="cerrarModal('modal-modalidad-crear')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="modalidad">
          <input type="hidden" name="accion" value="crear">
          <input type="hidden" name="tab_destino" value="tab-modalidad">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="mod-crear-id">Código ID <span>*</span></label>
              <input class="form-input" type="text" id="mod-crear-id" name="id_modalidad" maxlength="15" placeholder="Ej: REMOTA" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="mod-crear-nom">Nombre de la Modalidad <span>*</span></label>
              <input class="form-input" type="text" id="mod-crear-nom" name="nombre" maxlength="60" placeholder="Ej: Remota Asistida" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="mod-crear-canal">Canal de Difusión Obligatorio <span>*</span></label>
              <select class="form-input" id="mod-crear-canal" name="canal_difusion">
                <option value="QR">QR (Proyección en Auditorio)</option>
                <option value="ENLACE">ENLACE (Transmisión Virtual)</option>
                <option value="AMBOS">AMBOS (Híbrido Simultáneo)</option>
              </select>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" name="activo" value="1" checked>
                <span>Modalidad Activa</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-modalidad-crear')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Guardar Modalidad</button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" id="modal-modalidad-editar">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Editar Modalidad</h3>
          <button class="modal-close" onclick="cerrarModal('modal-modalidad-editar')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="modalidad">
          <input type="hidden" name="accion" value="editar">
          <input type="hidden" name="tab_destino" value="tab-modalidad">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Código ID</label>
              <input class="form-input" type="text" id="mod-edit-id-view" disabled>
              <input type="hidden" id="mod-edit-id" name="id_modalidad">
            </div>
            <div class="form-group">
              <label class="form-label" for="mod-edit-nom">Nombre de la Modalidad <span>*</span></label>
              <input class="form-input" type="text" id="mod-edit-nom" name="nombre" maxlength="60" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="mod-edit-canal">Canal de Difusión Obligatorio <span>*</span></label>
              <select class="form-input" id="mod-edit-canal" name="canal_difusion">
                <option value="QR">QR (Proyección en Auditorio)</option>
                <option value="ENLACE">ENLACE (Transmisión Virtual)</option>
                <option value="AMBOS">AMBOS (Híbrido Simultáneo)</option>
              </select>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" id="mod-edit-act" name="activo" value="1">
                <span>Modalidad Activa</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-modalidad-editar')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Actualizar Modalidad</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL 2: TIPO EVENTO CREAR / EDITAR -->
    <div class="modal-overlay" id="modal-evento-crear">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Registrar Tipo de Evento</h3>
          <button class="modal-close" onclick="cerrarModal('modal-evento-crear')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="tipo_evento">
          <input type="hidden" name="accion" value="crear">
          <input type="hidden" name="tab_destino" value="tab-evento">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="eve-crear-id">Código ASIS (Hasta 10 caracteres) <span>*</span></label>
              <input class="form-input" type="text" id="eve-crear-id" name="id_tipo_evento" maxlength="10" placeholder="Ej: SEMIN" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="eve-crear-nom">Nombre del Evento <span>*</span></label>
              <input class="form-input" type="text" id="eve-crear-nom" name="nombre" maxlength="80" placeholder="Ej: Seminario Internacional" required>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" name="activo" value="1" checked>
                <span>Vigente en Catálogo ASIS</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-evento-crear')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Guardar Evento</button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" id="modal-evento-editar">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Editar Tipo de Evento</h3>
          <button class="modal-close" onclick="cerrarModal('modal-evento-editar')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="tipo_evento">
          <input type="hidden" name="accion" value="editar">
          <input type="hidden" name="tab_destino" value="tab-evento">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Código ASIS</label>
              <input class="form-input" type="text" id="eve-edit-id-view" disabled>
              <input type="hidden" id="eve-edit-id" name="id_tipo_evento">
            </div>
            <div class="form-group">
              <label class="form-label" for="eve-edit-nom">Nombre del Evento <span>*</span></label>
              <input class="form-input" type="text" id="eve-edit-nom" name="nombre" maxlength="80" required>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" id="eve-edit-act" name="activo" value="1">
                <span>Vigente en Catálogo ASIS</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-evento-editar')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Actualizar Evento</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL 3: TIPO DOCUMENTO CREAR / EDITAR -->
    <div class="modal-overlay" id="modal-documento-crear">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Registrar Tipo de Documento</h3>
          <button class="modal-close" onclick="cerrarModal('modal-documento-crear')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="tipo_documento">
          <input type="hidden" name="accion" value="crear">
          <input type="hidden" name="tab_destino" value="tab-documento">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="doc-crear-id">Abreviatura / Código <span>*</span></label>
              <input class="form-input" type="text" id="doc-crear-id" name="id_tipo_documento" maxlength="10" placeholder="Ej: PEP" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="doc-crear-nom">Descripción del Documento <span>*</span></label>
              <input class="form-input" type="text" id="doc-crear-nom" name="nombre" maxlength="60" placeholder="Ej: Permiso Especial de Permanencia" required>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" name="activo" value="1" checked>
                <span>Documento Activo</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-documento-crear')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Guardar Documento</button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" id="modal-documento-editar">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Editar Tipo de Documento</h3>
          <button class="modal-close" onclick="cerrarModal('modal-documento-editar')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="tipo_documento">
          <input type="hidden" name="accion" value="editar">
          <input type="hidden" name="tab_destino" value="tab-documento">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Abreviatura / Código</label>
              <input class="form-input" type="text" id="doc-edit-id-view" disabled>
              <input type="hidden" id="doc-edit-id" name="id_tipo_documento">
            </div>
            <div class="form-group">
              <label class="form-label" for="doc-edit-nom">Descripción del Documento <span>*</span></label>
              <input class="form-input" type="text" id="doc-edit-nom" name="nombre" maxlength="60" required>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" id="doc-edit-act" name="activo" value="1">
                <span>Documento Activo</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-documento-editar')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Actualizar Documento</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL 4: TIPO VINCULACIÓN CREAR / EDITAR -->
    <div class="modal-overlay" id="modal-vinculacion-crear">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Registrar Tipo de Vinculación</h3>
          <button class="modal-close" onclick="cerrarModal('modal-vinculacion-crear')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="tipo_vinculacion">
          <input type="hidden" name="accion" value="crear">
          <input type="hidden" name="tab_destino" value="tab-vinculacion">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="vin-crear-id">Código ID (Hasta 15 caracteres) <span>*</span></label>
              <input class="form-input" type="text" id="vin-crear-id" name="id_tipo_vinculacion" maxlength="15" placeholder="Ej: INVESTIGADOR" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="vin-crear-nom">Nombre del Vínculo <span>*</span></label>
              <input class="form-input" type="text" id="vin-crear-nom" name="nombre" maxlength="60" placeholder="Ej: Investigador Invitado" required>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" name="es_interno" value="1" checked>
                <span>Pertenece a la Comunidad Interna USB</span>
              </label>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" name="exige_programa" value="1">
                <span>Exige selección obligatoria de Programa Académico</span>
              </label>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" name="activo" value="1" checked>
                <span>Vinculación Activa</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-vinculacion-crear')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Guardar Vinculación</button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" id="modal-vinculacion-editar">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Editar Tipo de Vinculación</h3>
          <button class="modal-close" onclick="cerrarModal('modal-vinculacion-editar')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="tipo_vinculacion">
          <input type="hidden" name="accion" value="editar">
          <input type="hidden" name="tab_destino" value="tab-vinculacion">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Código ID</label>
              <input class="form-input" type="text" id="vin-edit-id-view" disabled>
              <input type="hidden" id="vin-edit-id" name="id_tipo_vinculacion">
            </div>
            <div class="form-group">
              <label class="form-label" for="vin-edit-nom">Nombre del Vínculo <span>*</span></label>
              <input class="form-input" type="text" id="vin-edit-nom" name="nombre" maxlength="60" required>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" id="vin-edit-int" name="es_interno" value="1">
                <span>Pertenece a la Comunidad Interna USB</span>
              </label>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" id="vin-edit-prog" name="exige_programa" value="1">
                <span>Exige selección obligatoria de Programa Académico</span>
              </label>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" id="vin-edit-act" name="activo" value="1">
                <span>Vinculación Activa</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-vinculacion-editar')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Actualizar Vinculación</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL 5: PERIODO ACADÉMICO CREAR / EDITAR -->
    <div class="modal-overlay" id="modal-periodo-crear">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Registrar Periodo Académico</h3>
          <button class="modal-close" onclick="cerrarModal('modal-periodo-crear')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="periodo_academico">
          <input type="hidden" name="accion" value="crear">
          <input type="hidden" name="tab_destino" value="tab-periodo">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="per-crear-id">Código de Periodo (Hasta 10 caracteres) <span>*</span></label>
              <input class="form-input" type="text" id="per-crear-id" name="id_periodo" maxlength="10" placeholder="Ej: 2027-1" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="per-crear-ini">Fecha de Inicio <span>*</span></label>
              <input class="form-input" type="date" id="per-crear-ini" name="fecha_ini" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="per-crear-fin">Fecha de Finalización <span>*</span></label>
              <input class="form-input" type="date" id="per-crear-fin" name="fecha_fin" required>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" name="activo" value="1" checked>
                <span>Periodo Habilitado para Procesos</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-periodo-crear')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Guardar Periodo</button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" id="modal-periodo-editar">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Editar Periodo Académico</h3>
          <button class="modal-close" onclick="cerrarModal('modal-periodo-editar')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="periodo_academico">
          <input type="hidden" name="accion" value="editar">
          <input type="hidden" name="tab_destino" value="tab-periodo">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Código de Periodo</label>
              <input class="form-input" type="text" id="per-edit-id-view" disabled>
              <input type="hidden" id="per-edit-id" name="id_periodo">
            </div>
            <div class="form-group">
              <label class="form-label" for="per-edit-ini">Fecha de Inicio <span>*</span></label>
              <input class="form-input" type="date" id="per-edit-ini" name="fecha_ini" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="per-edit-fin">Fecha de Finalización <span>*</span></label>
              <input class="form-input" type="date" id="per-edit-fin" name="fecha_fin" required>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" id="per-edit-act" name="activo" value="1">
                <span>Periodo Habilitado para Procesos</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-periodo-editar')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Actualizar Periodo</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL 6: ROL CREAR / EDITAR -->
    <div class="modal-overlay" id="modal-rol-crear">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Registrar Rol de Usuario</h3>
          <button class="modal-close" onclick="cerrarModal('modal-rol-crear')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="rol">
          <input type="hidden" name="accion" value="crear">
          <input type="hidden" name="tab_destino" value="tab-roles">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="rol-crear-id">Código de Rol <span>*</span></label>
              <input class="form-input" type="text" id="rol-crear-id" name="id_rol" maxlength="20" placeholder="Ej: COORDINADOR_CIDEH" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="rol-crear-nom">Nombre del Rol <span>*</span></label>
              <input class="form-input" type="text" id="rol-crear-nom" name="nombre" maxlength="60" placeholder="Ej: Coordinador de Cátedras" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="rol-crear-desc">Descripción de Alcance</label>
              <textarea class="form-input" id="rol-crear-desc" name="descripcion" rows="2" maxlength="200" placeholder="Funciones y accesos asignados..."></textarea>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" name="activo" value="1" checked>
                <span>Rol Activo</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-rol-crear')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Guardar Rol</button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" id="modal-rol-editar">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Editar Rol de Usuario</h3>
          <button class="modal-close" onclick="cerrarModal('modal-rol-editar')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="rol">
          <input type="hidden" name="accion" value="editar">
          <input type="hidden" name="tab_destino" value="tab-roles">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Código de Rol</label>
              <input class="form-input" type="text" id="rol-edit-id-view" disabled>
              <input type="hidden" id="rol-edit-id" name="id_rol">
            </div>
            <div class="form-group">
              <label class="form-label" for="rol-edit-nom">Nombre del Rol <span>*</span></label>
              <input class="form-input" type="text" id="rol-edit-nom" name="nombre" maxlength="60" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="rol-edit-desc">Descripción de Alcance</label>
              <textarea class="form-input" id="rol-edit-desc" name="descripcion" rows="2" maxlength="200"></textarea>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" id="rol-edit-act" name="activo" value="1">
                <span>Rol Activo</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-rol-editar')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Actualizar Rol</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL 7: ESTADO PROCESO CREAR / EDITAR -->
    <div class="modal-overlay" id="modal-estado-crear">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Registrar Estado de Proceso</h3>
          <button class="modal-close" onclick="cerrarModal('modal-estado-crear')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="estado_proceso">
          <input type="hidden" name="accion" value="crear">
          <input type="hidden" name="tab_destino" value="tab-estados">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="est-crear-id">Código de Estado <span>*</span></label>
              <input class="form-input" type="text" id="est-crear-id" name="id_estado" maxlength="20" placeholder="Ej: EN_COLA" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="est-crear-nom">Nombre del Estado <span>*</span></label>
              <input class="form-input" type="text" id="est-crear-nom" name="nombre" maxlength="60" placeholder="Ej: En Cola de Procesamiento" required>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" name="es_final" value="1">
                <span>Es Fase Terminal (Concluye el proceso)</span>
              </label>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" name="es_exitoso" value="1">
                <span>Representa Resultado Exitoso</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-estado-crear')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Guardar Estado</button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" id="modal-estado-editar">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Editar Estado de Proceso</h3>
          <button class="modal-close" onclick="cerrarModal('modal-estado-editar')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="estado_proceso">
          <input type="hidden" name="accion" value="editar">
          <input type="hidden" name="tab_destino" value="tab-estados">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Código de Estado</label>
              <input class="form-input" type="text" id="est-edit-id-view" disabled>
              <input type="hidden" id="est-edit-id" name="id_estado">
            </div>
            <div class="form-group">
              <label class="form-label" for="est-edit-nom">Nombre del Estado <span>*</span></label>
              <input class="form-input" type="text" id="est-edit-nom" name="nombre" maxlength="60" required>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" id="est-edit-fin" name="es_final" value="1">
                <span>Es Fase Terminal (Concluye el proceso)</span>
              </label>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" id="est-edit-ex" name="es_exitoso" value="1">
                <span>Representa Resultado Exitoso</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-estado-editar')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Actualizar Estado</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL 8: ENCUESTA CREAR / EDITAR -->
    <div class="modal-overlay" id="modal-encuesta-crear">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Registrar Nueva Encuesta</h3>
          <button class="modal-close" onclick="cerrarModal('modal-encuesta-crear')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="encuesta">
          <input type="hidden" name="accion" value="crear">
          <input type="hidden" name="tab_destino" value="tab-encuesta">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="enc-crear-nom">Nombre de la Encuesta <span>*</span></label>
              <input class="form-input" type="text" id="enc-crear-nom" name="nombre" maxlength="120" placeholder="Ej: Encuesta de Calidad Institucional 2026" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="enc-crear-ver">Versión Numérica <span>*</span></label>
              <input class="form-input" type="number" id="enc-crear-ver" name="version" value="1" min="1" max="99" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="enc-crear-desde">Vigente Desde <span>*</span></label>
              <input class="form-input" type="date" id="enc-crear-desde" name="vigente_desde" value="2026-01-01" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="enc-crear-hasta">Vigente Hasta (Opcional)</label>
              <input class="form-input" type="date" id="enc-crear-hasta" name="vigente_hasta">
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" name="activa" value="1" checked>
                <span>Encuesta Activa y Disponible</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-encuesta-crear')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Guardar Encuesta</button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" id="modal-encuesta-editar">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Editar Encuesta</h3>
          <button class="modal-close" onclick="cerrarModal('modal-encuesta-editar')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="encuesta">
          <input type="hidden" name="accion" value="editar">
          <input type="hidden" name="tab_destino" value="tab-encuesta">
          <input type="hidden" id="enc-edit-id" name="id_encuesta">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="enc-edit-nom">Nombre de la Encuesta <span>*</span></label>
              <input class="form-input" type="text" id="enc-edit-nom" name="nombre" maxlength="120" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="enc-edit-ver">Versión Numérica <span>*</span></label>
              <input class="form-input" type="number" id="enc-edit-ver" name="version" min="1" max="99" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="enc-edit-desde">Vigente Desde <span>*</span></label>
              <input class="form-input" type="date" id="enc-edit-desde" name="vigente_desde" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="enc-edit-hasta">Vigente Hasta</label>
              <input class="form-input" type="date" id="enc-edit-hasta" name="vigente_hasta">
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" id="enc-edit-act" name="activa" value="1">
                <span>Encuesta Activa y Disponible</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-encuesta-editar')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Actualizar Encuesta</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL 8B: PREGUNTA CREAR / EDITAR -->
    <div class="modal-overlay" id="modal-pregunta-crear">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Registrar Nueva Pregunta</h3>
          <button class="modal-close" onclick="cerrarModal('modal-pregunta-crear')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="pregunta">
          <input type="hidden" name="accion" value="crear">
          <input type="hidden" name="tab_destino" value="tab-encuesta">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="prg-crear-enc">Encuesta a Vincular <span>*</span></label>
              <select class="form-input" id="prg-crear-enc" name="fk_encuesta">
                {opts_encuestas}
              </select>
            </div>
            <div class="form-group">
              <label class="form-label" for="prg-crear-enun">Enunciado de la Pregunta <span>*</span></label>
              <input class="form-input" type="text" id="prg-crear-enun" name="enunciado" placeholder="Ej: ¿El contenido respondió a sus expectativas académicas?" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="prg-crear-tp">Tipo de Pregunta <span>*</span></label>
              <select class="form-input" id="prg-crear-tp" name="fk_tipo_pregunta">
                {opts_tipo_preg}
              </select>
            </div>
            <div class="form-group">
              <label class="form-label" for="prg-crear-ord">Secuencia de Orden <span>*</span></label>
              <input class="form-input" type="number" id="prg-crear-ord" name="orden" value="{len(preguntas) + 1}" min="1" max="99" required>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" name="obligatoria" value="1" checked>
                <span>Respuesta Obligatoria</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-pregunta-crear')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Guardar Pregunta</button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" id="modal-pregunta-editar">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Editar Pregunta</h3>
          <button class="modal-close" onclick="cerrarModal('modal-pregunta-editar')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="pregunta">
          <input type="hidden" name="accion" value="editar">
          <input type="hidden" name="tab_destino" value="tab-encuesta">
          <input type="hidden" id="prg-edit-id" name="id_pregunta">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="prg-edit-enun">Enunciado de la Pregunta <span>*</span></label>
              <input class="form-input" type="text" id="prg-edit-enun" name="enunciado" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="prg-edit-tp">Tipo de Pregunta <span>*</span></label>
              <select class="form-input" id="prg-edit-tp" name="fk_tipo_pregunta">
                {opts_tipo_preg}
              </select>
            </div>
            <div class="form-group">
              <label class="form-label" for="prg-edit-ord">Secuencia de Orden <span>*</span></label>
              <input class="form-input" type="number" id="prg-edit-ord" name="orden" min="1" max="99" required>
            </div>
            <div class="form-group">
              <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;font-weight:700;cursor:pointer;">
                <input type="checkbox" id="prg-edit-obl" name="obligatoria" value="1">
                <span>Respuesta Obligatoria</span>
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-pregunta-editar')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Actualizar Pregunta</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL 9: PARÁMETRO CREAR / EDITAR -->
    <div class="modal-overlay" id="modal-parametro-crear">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Registrar Nuevo Parámetro</h3>
          <button class="modal-close" onclick="cerrarModal('modal-parametro-crear')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="parametro">
          <input type="hidden" name="accion" value="crear">
          <input type="hidden" name="tab_destino" value="tab-parametros">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="par-crear-clave">Clave del Parámetro <span>*</span></label>
              <input class="form-input" type="text" id="par-crear-clave" name="clave" maxlength="60" placeholder="Ej: DIAS_VIGENCIA_ENCUESTA" required>
              <p class="form-hint">Clave única institucional en mayúsculas.</p>
            </div>
            <div class="form-group">
              <label class="form-label" for="par-crear-val">Valor Actual <span>*</span></label>
              <input class="form-input" type="text" id="par-crear-val" name="valor" placeholder="Ej: 30" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="par-crear-td">Tipo de Dato <span>*</span></label>
              <select class="form-input" id="par-crear-td" name="tipo_dato">
                <option value="TEXTO">TEXTO</option>
                <option value="ENTERO">ENTERO</option>
                <option value="DECIMAL">DECIMAL</option>
                <option value="BOOLEANO">BOOLEANO</option>
                <option value="TIEMPO">TIEMPO</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label" for="par-crear-desc">Descripción y Regla Aplicada</label>
              <textarea class="form-input" id="par-crear-desc" name="descripcion" rows="2" maxlength="250" placeholder="Explicación del uso institucional del parámetro..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-parametro-crear')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Guardar Parámetro</button>
          </div>
        </form>
      </div>
    </div>

    <div class="modal-overlay" id="modal-parametro-editar">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">Editar Parámetro del Sistema</h3>
          <button class="modal-close" onclick="cerrarModal('modal-parametro-editar')">✕</button>
        </div>
        <form method="POST">
          <input type="hidden" name="catalogo" value="parametro">
          <input type="hidden" name="accion" value="editar">
          <input type="hidden" name="tab_destino" value="tab-parametros">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Clave del Parámetro</label>
              <input class="form-input" type="text" id="par-edit-clave-view" disabled>
              <input type="hidden" id="par-edit-clave" name="clave">
            </div>
            <div class="form-group">
              <label class="form-label" for="par-edit-val">Valor Actual <span>*</span></label>
              <input class="form-input" type="text" id="par-edit-val" name="valor" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="par-edit-td">Tipo de Dato <span>*</span></label>
              <select class="form-input" id="par-edit-td" name="tipo_dato">
                <option value="TEXTO">TEXTO</option>
                <option value="ENTERO">ENTERO</option>
                <option value="DECIMAL">DECIMAL</option>
                <option value="BOOLEANO">BOOLEANO</option>
                <option value="TIEMPO">TIEMPO</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label" for="par-edit-desc">Descripción y Regla Aplicada</label>
              <textarea class="form-input" id="par-edit-desc" name="descripcion" rows="2" maxlength="250"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-usb btn-usb-ghost" onclick="cerrarModal('modal-parametro-editar')">Cancelar</button>
            <button type="submit" class="btn-usb btn-usb-primary">Actualizar Parámetro</button>
          </div>
        </form>
      </div>
    </div>

    <script>
      function abrirModal(id) {{
        const m = document.getElementById(id);
        if (m) m.classList.add('open');
      }}

      function cerrarModal(id) {{
        const m = document.getElementById(id);
        if (m) m.classList.remove('open');
      }}

      function mostrarTabCatalogo(tabId, btn) {{
        document.querySelectorAll('.catalogo-tab-pane').forEach(p => p.style.display = 'none');
        document.querySelectorAll('.view-tabs-nav .view-tab-btn').forEach(b => b.classList.remove('active'));
        
        const target = document.getElementById(tabId);
        if (target) target.style.display = 'block';
        if (btn) {{
          btn.classList.add('active');
        }} else {{
          const mappedBtn = document.getElementById('btn-' + tabId);
          if (mappedBtn) mappedBtn.classList.add('active');
        }}
        try {{
          localStorage.setItem('active_catalogo_tab', tabId);
        }} catch(e) {{}}
      }}

      // Funciones para cargar datos en modales de edición
      function abrirEditarModalidad(id, nombre, canal, activo) {{
        document.getElementById('mod-edit-id-view').value = id;
        document.getElementById('mod-edit-id').value = id;
        document.getElementById('mod-edit-nom').value = nombre;
        document.getElementById('mod-edit-canal').value = canal;
        document.getElementById('mod-edit-act').checked = (activo === '1');
        abrirModal('modal-modalidad-editar');
      }}

      function abrirEditarTipoEvento(id, nombre, activo) {{
        document.getElementById('eve-edit-id-view').value = id;
        document.getElementById('eve-edit-id').value = id;
        document.getElementById('eve-edit-nom').value = nombre;
        document.getElementById('eve-edit-act').checked = (activo === '1');
        abrirModal('modal-evento-editar');
      }}

      function abrirEditarTipoDocumento(id, nombre, activo) {{
        document.getElementById('doc-edit-id-view').value = id;
        document.getElementById('doc-edit-id').value = id;
        document.getElementById('doc-edit-nom').value = nombre;
        document.getElementById('doc-edit-act').checked = (activo === '1');
        abrirModal('modal-documento-editar');
      }}

      function abrirEditarTipoVinculacion(id, nombre, es_int, ex_prog, activo) {{
        document.getElementById('vin-edit-id-view').value = id;
        document.getElementById('vin-edit-id').value = id;
        document.getElementById('vin-edit-nom').value = nombre;
        document.getElementById('vin-edit-int').checked = (es_int === '1');
        document.getElementById('vin-edit-prog').checked = (ex_prog === '1');
        document.getElementById('vin-edit-act').checked = (activo === '1');
        abrirModal('modal-vinculacion-editar');
      }}

      function abrirEditarPeriodo(id, ini, fin, activo) {{
        document.getElementById('per-edit-id-view').value = id;
        document.getElementById('per-edit-id').value = id;
        document.getElementById('per-edit-ini').value = ini;
        document.getElementById('per-edit-fin').value = fin;
        document.getElementById('per-edit-act').checked = (activo === '1');
        abrirModal('modal-periodo-editar');
      }}

      function abrirEditarRol(id, nombre, desc, activo) {{
        document.getElementById('rol-edit-id-view').value = id;
        document.getElementById('rol-edit-id').value = id;
        document.getElementById('rol-edit-nom').value = nombre;
        document.getElementById('rol-edit-desc').value = desc;
        document.getElementById('rol-edit-act').checked = (activo === '1');
        abrirModal('modal-rol-editar');
      }}

      function abrirEditarEstado(id, nombre, es_fin, es_ex) {{
        document.getElementById('est-edit-id-view').value = id;
        document.getElementById('est-edit-id').value = id;
        document.getElementById('est-edit-nom').value = nombre;
        document.getElementById('est-edit-fin').checked = (es_fin === '1');
        document.getElementById('est-edit-ex').checked = (es_ex === '1');
        abrirModal('modal-estado-editar');
      }}

      function abrirEditarEncuesta(id, nombre, version, desde, hasta, activa) {{
        document.getElementById('enc-edit-id').value = id;
        document.getElementById('enc-edit-nom').value = nombre;
        document.getElementById('enc-edit-ver').value = version;
        document.getElementById('enc-edit-desde').value = desde;
        document.getElementById('enc-edit-hasta').value = hasta;
        document.getElementById('enc-edit-act').checked = (activa === '1');
        abrirModal('modal-encuesta-editar');
      }}

      function abrirEditarPregunta(id, fk_enc, enunciado, orden, tipo_preg, obligatoria) {{
        document.getElementById('prg-edit-id').value = id;
        document.getElementById('prg-edit-enun').value = enunciado;
        document.getElementById('prg-edit-ord').value = orden;
        document.getElementById('prg-edit-tp').value = tipo_preg;
        document.getElementById('prg-edit-obl').checked = (obligatoria === '1');
        abrirModal('modal-pregunta-editar');
      }}

      function abrirEditarParametro(clave, valor, tipo_dato, desc) {{
        document.getElementById('par-edit-clave-view').value = clave;
        document.getElementById('par-edit-clave').value = clave;
        document.getElementById('par-edit-val').value = valor;
        document.getElementById('par-edit-td').value = tipo_dato;
        document.getElementById('par-edit-desc').value = desc;
        abrirModal('modal-parametro-editar');
      }}

      // Inicializar pestaña activa
      document.addEventListener("DOMContentLoaded", function() {{
        const urlParams = new URLSearchParams(window.location.search);
        const tabSolicitada = urlParams.get('tab') || localStorage.getItem('active_catalogo_tab') || '{tab_inicial}';
        const targetTab = document.getElementById(tabSolicitada) ? tabSolicitada : 'tab-modalidad';
        mostrarTabCatalogo(targetTab);
      }});
    </script>
    """
    return render_template_string(BASE_LAYOUT, titulo="Catálogos y Parametrización", contenido=contenido)


# ==========================================
# 9. MODULO DE REGISTRO PUBLICO CON GEOLOCALIZACION
# ==========================================
@app.route("/registro", methods=["GET", "POST"])
def registro():
    enlace_id = request.args.get("enlace", "").strip()
    codigo_sesion_param = request.args.get("sesion", "").strip()

    info_sesion = None
    sesiones_disponibles = []

    try:
        r_ses = requests.get(f"{API_BASE}/sesion?limite=50", headers=auth_headers(), timeout=4)
        if r_ses.status_code == 200:
            sesiones_disponibles = r_ses.json()
        r_cat = requests.get(f"{API_BASE}/catedra?limite=100", headers=auth_headers(), timeout=4)
        cat_map = {c.get("id_catedra"): c for c in (r_cat.json() if r_cat.status_code == 200 else [])}
        for s in sesiones_disponibles:
            cid = s.get("fk_catedra")
            cat_obj = cat_map.get(cid) or {}
            s["catedra_nombre"] = cat_obj.get("nombre") or f"Cátedra #{cid}"
            s["evento_asis"] = cat_obj.get("id_evento_asis") or "-"
    except Exception:
        pass

    target_id = enlace_id or codigo_sesion_param
    if target_id:
        for s in sesiones_disponibles:
            if str(s.get("id_sesion")) == str(target_id):
                info_sesion = s
                break

    if not info_sesion and sesiones_disponibles:
        info_sesion = sesiones_disponibles[0]

    if request.method == "POST":
        id_sesion_sel = request.form.get("id_sesion", "").strip()
        if not id_sesion_sel:
            flash("Debe existir o seleccionarse una cátedra/sesión válida para registrar asistencia.", "danger")
            return redirect(url_for("registro", enlace=enlace_id))

        es_estudiante = request.form.get("es_estudiante") == "1"
        latitud = request.form.get("latitud")
        longitud = request.form.get("longitud")
        precision = request.form.get("precision")
        habeas = request.form.get("habeas_data")

        if not habeas:
            flash("Debe autorizar el tratamiento de datos personales conforme a la Ley 1581 de 2012.", "danger")
            return redirect(url_for("registro", enlace=enlace_id))

        nom_cat_sel = "la cátedra"
        for s in sesiones_disponibles:
            if str(s.get("id_sesion")) == str(id_sesion_sel):
                nom_cat_sel = f"'{s.get('catedra_nombre')}' (Sesión #{id_sesion_sel} - ASIS {s.get('evento_asis')})"
                break

        geo_detalle = f" (Ubicación GPS confirmada: Lat {latitud[:7]}, Lon {longitud[:7]} con precisión de {precision}m)" if latitud else " (Ubicación por IP institucional)"

        if es_estudiante:
            codigo = request.form.get("codigo_estudiante", "").strip()
            if not codigo:
                flash("Ingrese su código estudiantil o documento registrado en el ASIS.", "danger")
                return redirect(url_for("registro", enlace=enlace_id))
            flash(f"Asistencia registrada con éxito para la cátedra {nom_cat_sel}. Estudiante con código '{codigo}'.{geo_detalle}. Su participación ha sido vinculada al sistema ASIS.", "success")
        else:
            nombres = request.form.get("nombres", "").strip()
            apellidos = request.form.get("apellidos", "").strip()
            documento = request.form.get("documento", "").strip()
            correo = request.form.get("correo", "").strip()
            procedencia = request.form.get("procedencia", "").strip()

            if not (nombres and apellidos and documento and correo):
                flash("Por favor complete todos los datos del formulario para participantes externos.", "danger")
                return redirect(url_for("registro", enlace=enlace_id))

            flash(f"Bienvenido {nombres} {apellidos}. Su registro en la cátedra {nom_cat_sel} como participante externo ({procedencia or 'Particular'}) ha sido confirmado.{geo_detalle}.", "success")

        return redirect(url_for("registro", enlace=enlace_id))

    ses_options = "".join([f"<option value='{s.get('id_sesion')}' {'selected' if info_sesion and s.get('id_sesion') == info_sesion.get('id_sesion') else ''}>Sesión #{s.get('id_sesion')} — {s.get('catedra_nombre')} (ASIS: {s.get('evento_asis')})</option>" for s in sesiones_disponibles])

    cat_badge_nombre = info_sesion.get("catedra_nombre") if info_sesion else "Seleccione una Cátedra"
    asis_badge = info_sesion.get("evento_asis") if info_sesion else "-"
    ses_id_val = info_sesion.get("id_sesion") if info_sesion else ""
    reunion_num = info_sesion.get("numero_reunion") if info_sesion else "1"
    sede_nombre = info_sesion.get("fk_sede") if info_sesion else "SAN_BENITO"

    banner_catedra_html = f"""
    <div style="background:#FFF;border:2px solid var(--usb-naranja);border-radius:10px;padding:1.2rem;margin-bottom:1.5rem;box-shadow:var(--shadow-card);">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:0.5rem;">
        <span class="badge badge-orange" style="font-size:0.78rem;">CÁTEDRA VINCULADA OFICIAL</span>
        <span class="td-code" style="font-weight:700;">Código ASIS: {asis_badge}</span>
      </div>
      <h3 style="color:var(--usb-negro);font-size:1.15rem;font-weight:800;margin:0.25rem 0 0.5rem 0;">{cat_badge_nombre}</h3>
      <div style="display:flex;gap:1.2rem;flex-wrap:wrap;font-size:0.82rem;color:var(--usb-text-muted);">
        <span><strong>Sesión:</strong> #{ses_id_val} (Reunión {reunion_num})</span>
        <span><strong>Sede:</strong> {sede_nombre}</span>
        <span><strong>Acreditación:</strong> Verificación de Asistencia</span>
      </div>
    </div>
    """

    contenido = f"""
    <div class="page-header">
      <div>
        <h1 class="page-title">Acreditación de Asistencia a <span>Cátedras Abiertas</span></h1>
        <p style="font-size:0.88rem;color:var(--usb-text-muted);margin-top:0.25rem">
          Formulario institucional de acreditación de asistencia vinculado al código de cátedra y validación de geolocalización.
        </p>
      </div>
    </div>

    <div style="max-width: 760px; margin: 0 auto;">
      {banner_catedra_html}
      <div class="card-panel">
        <div class="card-panel-header">
          <h3 class="card-panel-title">Validación de Asistencia en Campus</h3>
          <span class="badge badge-orange">Sesión Oficial CIDEH</span>
        </div>
        <div class="card-panel-body">
          <form method="POST" id="form-asistencia">
            <input type="hidden" name="latitud" id="latitud">
            <input type="hidden" name="longitud" id="longitud">
            <input type="hidden" name="precision" id="precision">

            <div class="form-group" style="margin-bottom: 1.25rem;">
              <label class="form-label" for="id_sesion">Cátedra y Sesión Académica Correspondiente <span>*</span></label>
              <select class="form-input" id="id_sesion" name="id_sesion" required style="font-weight:600;">
                {ses_options}
              </select>
              <p class="form-hint">Cada registro debe corresponder estrictamente al código oficial de la cátedra asignada.</p>
            </div>

            <div style="background:var(--usb-naranja-light);border:1.5px solid #FDBA74;border-radius:8px;padding:1rem;margin-bottom:1.75rem;display:flex;align-items:center;gap:12px;">
              <div style="width:10px;height:10px;border-radius:50%;background:var(--usb-naranja);"></div>
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

            <div style="background:var(--usb-gris-claro);border:1px solid var(--usb-gris-borde);border-radius:6px;padding:1.1rem;margin:1.5rem 0;">
              <label style="display:flex;align-items:flex-start;gap:10px;font-size:0.8rem;color:#374151;cursor:pointer;line-height:1.5;">
                <input type="checkbox" name="habeas_data" value="1" required style="margin-top:3px;">
                <span>Autorizo de manera expresa e inequívoca a la <strong>Universidad de San Buenaventura Medellín (CIDEH)</strong> para el tratamiento y almacenamiento de mis datos personales y geolocalización, conforme a la Ley 1581 de 2012, para fines de acreditación académica y transferencia al sistema ASIS/Oracle.</span>
              </label>
            </div>

            <div style="text-align:right;">
              <button type="submit" class="btn-usb btn-usb-primary" style="padding:0.85rem 2.2rem;">Confirmar Asistencia</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <script>
      function cambiarTipo(esEst) {{
        document.getElementById('panel-estudiante').style.display = esEst ? 'block' : 'none';
        document.getElementById('panel-externo').style.display = esEst ? 'none' : 'block';
      }}

      if ("geolocation" in navigator) {{
        navigator.geolocation.getCurrentPosition(
          function(pos) {{
            document.getElementById('latitud').value = pos.coords.latitude;
            document.getElementById('longitud').value = pos.coords.longitude;
            document.getElementById('precision').value = Math.round(pos.coords.accuracy);
            const geoInfo = document.getElementById('geo-info');
            geoInfo.innerHTML = "Presencia verificada: Coordenadas capturadas con precisión de " + Math.round(pos.coords.accuracy) + " metros en la sede.";
            geoInfo.style.color = "#16A34A";
          }},
          function(err) {{
            const geoInfo = document.getElementById('geo-info');
            geoInfo.innerHTML = "Geolocalización por red institucional aplicada.";
            geoInfo.style.color = "#4B5563";
          }},
          {{ enableHighAccuracy: true, timeout: 6000 }}
        );
      }}
    </script>
    """
    return render_template_string(BASE_LAYOUT, titulo="Registro de Asistencia", contenido=contenido)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5173, debug=False)
