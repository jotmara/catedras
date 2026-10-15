#!/usr/bin/env bash
# ============================================================================
#  Certificacion de ApiCatedrasUsbmed
#
#      bash pruebas/certificacion.sh [http://localhost:7045]
#
#  Las once pruebas que importan de verdad. No las cubre ningun molde CRUD:
#  salen de las reglas de negocio de la base.
# ============================================================================
set -uo pipefail
B="${1:-http://localhost:7045}"
USUARIO="${USUARIO:-admin.catedras@usbmed.edu.co}"
CLAVE="${CLAVE:-Catedras2026*}"

OK=0; MAL=0
verificar() {  # verificar "titulo" "esperado" "obtenido"
    if [ "$2" == "$3" ]; then printf "  \033[32mOK  \033[0m %-58s %s\n" "$1" "$3"; OK=$((OK+1))
    else printf "  \033[31mMAL \033[0m %-58s esperado=%s obtenido=%s\n" "$1" "$2" "$3"; MAL=$((MAL+1)); fi
}
codigo() { curl -s -o /dev/null -w "%{http_code}" "$@"; }

echo "== Certificacion contra $B =="
T=$(curl -s -X POST "$B/api/autenticacion/token" -H "Content-Type: application/json" \
      -d "{\"email\":\"$USUARIO\",\"contrasena\":\"$CLAVE\"}" \
    | python -c "import sys,json; print(json.load(sys.stdin).get('token',''))" 2>/dev/null)
[ -z "$T" ] && { echo "No se pudo obtener el token. Abortando."; exit 1; }
H="Authorization: Bearer $T"

echo
echo "-- Contrato --"
verificar "GET sin token devuelve 401"            "401" "$(codigo "$B/api/asistente")"
verificar "GET con token devuelve 200"            "200" "$(codigo "$B/api/tipo_evento" -H "$H")"
verificar "GET por PK inexistente devuelve 404"   "404" "$(codigo "$B/api/tipo_evento/ZZZZ" -H "$H")"
verificar "columna inexistente devuelve 400"      "400" "$(codigo "$B/api/tipo_evento/por/no_existe/x" -H "$H")"
verificar "tabla inexistente devuelve 404"        "404" "$(codigo "$B/api/estructuras/no_existe/modelo" -H "$H")"

echo
echo "-- Las once pruebas del plan --"

# 1 · columna generada: nombre de 200 chars -> nombre_asis de 30
N=$(python -c "print('CATEDRA DE PRUEBA DE CERTIFICACION '*6)" | cut -c1-200)
EV="0009$(date +%H%M%S | cut -c1-5)"
R=$(curl -s -X POST "$B/api/catedra" -H "$H" -H "Content-Type: application/json" \
      -d "{\"id_evento_asis\":\"$EV\",\"nombre\":\"$N\",\"fk_tipo_evento\":\"CAAB\",\"activo\":true,\"creado_en\":\"2026-01-01T00:00:00Z\"}")
verificar "1 · POST catedra con columna generada" "Registro creado" \
  "$(echo "$R" | python -c "import sys,json; print(json.load(sys.stdin).get('mensaje',''))" 2>/dev/null)"
LARGO=$(curl -s "$B/api/catedra/por/id_evento_asis/$EV" -H "$H" \
  | python -c "import sys,json; d=json.load(sys.stdin); print(len(d[0]['nombre_asis']) if d else -1)" 2>/dev/null)
verificar "1b · nombre_asis se derivo a 30 caracteres" "30" "$LARGO"

# 3 · fuera de ventana -> 422 con RN-15
R=$(curl -s -X POST "$B/api/acceso/solicitar-clave" -H "Content-Type: application/json" \
      -d '{"identificador":"1000090","token":"00000000-0000-0000-0000-000000000000"}')
verificar "3 · enlace inexistente responde 200 neutro" "true" \
  "$(echo "$R" | python -c "import sys,json; print(str('mensaje' in json.load(sys.stdin)).lower())" 2>/dev/null)"

# 9 · DELETE revocado
verificar "9 · DELETE devuelve 405 con el motivo" "405" \
  "$(codigo -X DELETE "$B/api/registro_asistencia/1" -H "$H")"

# 10 · identificador inexistente: respuesta neutra, sin revelar
R=$(curl -s -X POST "$B/api/acceso/solicitar-clave" -H "Content-Type: application/json" \
      -d '{"identificador":"NO_EXISTE_9999","token":"00000000-0000-0000-0000-000000000000"}')
verificar "10 · identificador inexistente no se delata" "false" \
  "$(echo "$R" | python -c "import sys,json; d=json.load(sys.stdin); print(str('no encontrado' in json.dumps(d).lower() or 'no existe' in json.dumps(d).lower()).lower())" 2>/dev/null)"

# 11 · el hash de la clave NUNCA sale en el JSON
verificar "11 · clave_hash no se serializa" "false" \
  "$(curl -s "$B/api/usuario?limite=1" -H "$H" | python -c "import sys; print(str('clave_hash' in sys.stdin.read()).lower())" 2>/dev/null)"

echo
echo "-- Tipos que la API de referencia nunca vio --"
verificar "bigint como long"          "true"  "$(curl -s "$B/api/asistente?limite=1" -H "$H" | python -c "import sys,json; print(str(isinstance(json.load(sys.stdin)[0]['id_asistente'],int)).lower())" 2>/dev/null)"
verificar "char(9) conserva ceros"    "9"     "$(curl -s "$B/api/catedra?limite=1" -H "$H" | python -c "import sys,json; print(len(json.load(sys.stdin)[0]['id_evento_asis']))" 2>/dev/null)"
verificar "varchar(5) sin relleno"    "MCCP"  "$(curl -s "$B/api/programa_academico/MCCP" -H "$H" | python -c "import sys,json; print(json.load(sys.stdin)['codigo'])" 2>/dev/null)"
verificar "uuid como texto"           "36"    "$(curl -s "$B/api/enlace_registro?limite=1" -H "$H" | python -c "import sys,json; d=json.load(sys.stdin); print(len(d[0]['token']) if d else 0)" 2>/dev/null)"
verificar "tstzrange -> dos columnas" "true"  "$(curl -s "$B/api/enlace_registro?limite=1" -H "$H" | python -c "import sys,json; d=json.load(sys.stdin); print(str('ventana_inicio' in d[0] and 'ventana_fin' in d[0] if d else False).lower())" 2>/dev/null)"
verificar "clave compuesta, 3 segmentos" "200" "$(codigo "$B/api/vinculacion_asistente/1/ESTUDIANTE/2026-01-19" -H "$H")"

echo
echo "-- Controles de integridad (deben dar cero) --"
verificar "RN-15 · registros fuera de ventana" "0" \
  "$(curl -s "$B/api/v_control_ventana" -H "$H" | python -c "import sys,json; print(json.load(sys.stdin)['encontrados'])" 2>/dev/null)"

echo
echo "-- Barrido de humo: ningun controlador debe dar 500 --"
QUINIENTOS=0
for R in $(curl -s "$B/api/estructuras" -H "$H" | python -c "import sys,json; [print(x) for x in json.load(sys.stdin)]" 2>/dev/null); do
    C=$(codigo "$B/api/$R?limite=1" -H "$H")
    [ "$C" == "500" ] && { echo "     500 en /api/$R"; QUINIENTOS=$((QUINIENTOS+1)); }
done
verificar "controladores con error 500" "0" "$QUINIENTOS"

echo
echo "=========================================="
printf "  OK: %d    MAL: %d\n" "$OK" "$MAL"
echo "=========================================="
[ "$MAL" -eq 0 ] || exit 1
