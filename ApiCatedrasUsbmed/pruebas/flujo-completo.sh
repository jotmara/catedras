#!/usr/bin/env bash
# ============================================================================
#  Recorrido completo por HTTP:
#    emitir enlace -> QR -> clave al correo -> validar -> registrar ->
#    encuesta -> lote -> archivo plano del ASIS
#
#      bash pruebas/flujo-completo.sh [http://localhost:7045]
#
#  Es la prueba que demuestra que la capa de procesos funciona de verdad, no
#  solo que compila.
# ============================================================================
set -uo pipefail
B="${1:-http://localhost:7045}"
PSQL="${PSQL:-/c/Program Files/PostgreSQL/18/bin/psql.exe}"
export PGPASSWORD="${PGPASSWORD:-postgres}"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

db()  { "$PSQL" -U postgres -h localhost -d catedras -tAc "$1"; }
jq_() { python -c "import sys,json;d=json.load(sys.stdin);$1" 2>/dev/null; }
OK=0; MAL=0
paso() { if [ "$2" == "$3" ]; then printf "   \033[32mOK\033[0m  %-46s %s\n" "$1" "$3"; OK=$((OK+1));
         else printf "   \033[31mMAL\033[0m %-46s esperado=%s obtenido=%s\n" "$1" "$2" "$3"; MAL=$((MAL+1)); fi }

T=$(curl -s -X POST "$B/api/autenticacion/token" -H "Content-Type: application/json" \
      -d '{"email":"admin.catedras@usbmed.edu.co","contrasena":"Catedras2026*"}' | jq_ "print(d['token'])")
[ -z "$T" ] && { echo "Sin token. Abortando."; exit 1; }
H="Authorization: Bearer $T"

SES=$(db "SELECT s.id_sesion FROM catedras.sesion s
            JOIN catedras.catedra c ON c.id_catedra=s.fk_catedra
           WHERE c.id_evento_asis='000099001' AND s.fk_sede='SAN_BENITO'")

# Preparacion: la sesion de prueba se creo el dia que corrio 14-datos-prueba.sql, asi que
# su ventana ya esta cerrada. Se reubica a la hora actual para poder ejercitar el flujo.
# No es un atajo: si no se reubicara, sp_solicitar_clave la rechazaria por RN-15, que es
# exactamente lo que debe hacer.
db "UPDATE catedras.sesion
       SET inicio = date_trunc('hour', now()),
           fin    = date_trunc('hour', now()) + interval '2 hour'
     WHERE id_sesion = $SES" > /dev/null

echo "Sesion de prueba: $SES  (reubicada a la hora actual)"

echo
echo "1 · Emitir el enlace  ·  el boton del documento de requisitos"
E=$(curl -s -X POST "$B/api/enlace/emitir" -H "$H" -H "Content-Type: application/json" \
      -d "{\"id_sesion\":$SES,\"minutos_antes\":180,\"minutos_despues\":180}")
IDE=$(echo "$E" | jq_ "print(d.get('id_enlace',0))")
TOK=$(db "SELECT token FROM catedras.enlace_registro WHERE id_enlace=$IDE")
paso "enlace emitido" "true" "$([ "$IDE" != "0" ] && echo true || echo false)"
echo "       token = $TOK"

echo
echo "2 · Pantalla de bienvenida  ·  anonimo, sin JWT"
V=$(curl -s "$B/api/acceso/enlace/$TOK")
echo "$V" | jq_ "print('       catedra:',d['catedra'][:48]);print('       sede:',d['sede'],'| modalidad:',d['modalidad'])"
paso "ventana abierta" "True" "$(echo "$V" | jq_ "print(d['ventana_abierta'])")"

echo
echo "3 · QR en PNG"
CQR=$(curl -s -o "$TMP/qr.png" -w "%{http_code}" "$B/api/enlace/$IDE/qr" -H "$H")
paso "HTTP del QR" "200" "$CQR"
paso "es un PNG valido" "True" "$(python -c "import sys;print(open(sys.argv[1],'rb').read(8)==bytes([137,80,78,71,13,10,26,10]))" "$TMP/qr.png")"

echo
echo "4 · Solicitar la clave  ·  anonimo"
ASI=$(db "SELECT a.id_asis FROM catedras.asistente a
            JOIN catedras.programa_asistente pa ON pa.fk_asistente=a.id_asistente
           WHERE a.id_asis IS NOT NULL
             AND NOT EXISTS (SELECT 1 FROM catedras.registro_asistencia r
                              WHERE r.fk_asistente=a.id_asistente AND r.fk_sesion=$SES)
           LIMIT 1")
R=$(curl -s -X POST "$B/api/acceso/solicitar-clave" -H "Content-Type: application/json" \
      -d "{\"identificador\":\"$ASI\",\"token\":\"$TOK\"}")
IDC=$(echo "$R" | jq_ "print(d.get('id_clave',0))")
echo "       asistente $ASI  ->  $(echo "$R" | jq_ "print('id_clave',d.get('id_clave'),'| enviado_a',d.get('enviado_a'))")"
paso "clave generada" "true" "$([ "${IDC:-0}" != "0" ] && echo true || echo false)"
paso "correo enmascarado" "true" "$(echo "$R" | jq_ "print(str('*' in str(d.get('enviado_a',''))).lower())")"

echo
echo "5 · En la base solo esta el HASH, nunca la clave"
db "SELECT '       clave_hash: ' || length(clave_hash) || ' bytes | institucional: ' || es_correo_institucional
      FROM catedras.clave_acceso WHERE id_clave=$IDC"

echo
echo "6 · Clave incorrecta  ->  debe rechazar (RN-18)"
CMAL=$(curl -s -o "$TMP/mal.json" -w "%{http_code}" -X POST "$B/api/acceso/validar" \
        -H "Content-Type: application/json" -d "{\"id_clave\":$IDC,\"clave\":\"000000\"}")
paso "no deja pasar" "422" "$CMAL"
python -c "import json,sys;print('      ',json.load(open(sys.argv[1])).get('mensaje','')[:66])" "$TMP/mal.json" 2>/dev/null

echo
echo "7 · Clave correcta  ->  registra"
# El correo esta desactivado en desarrollo, asi que la clave en claro no se puede leer:
# se reescribe el hash con una conocida, con la MISMA sal que usa sp_solicitar_clave.
CLAVE=$(db "SELECT lpad((floor(random()*1000000))::int::text, 6, '0')")
db "UPDATE catedras.clave_acceso
       SET clave_hash = digest('$CLAVE' || enviado_a::text, 'sha256'), intentos = 0, usado_en = NULL
     WHERE id_clave = $IDC" > /dev/null
REG=$(curl -s -X POST "$B/api/acceso/validar" -H "Content-Type: application/json" \
        -d "{\"id_clave\":$IDC,\"clave\":\"$CLAVE\"}")
IDR=$(echo "$REG" | jq_ "print(d.get('id_registro',0))")
paso "registro creado" "true" "$([ "${IDR:-0}" != "0" ] && echo true || echo false)"

echo
echo "8 · Las instantaneas las puso el DISPARADOR, no la API"
db "SELECT '       programa=' || COALESCE(fk_programa_snapshot,'(nulo)') ||
           ' | vinculacion=' || fk_vinculacion_snapshot || ' | origen=' || origen
      FROM catedras.registro_asistencia WHERE id_registro=$IDR"

echo
echo "9 · Registrarse dos veces  ->  409 (RN-21)"
db "UPDATE catedras.clave_acceso SET usado_en=NULL,
       clave_hash=digest('$CLAVE' || enviado_a::text,'sha256') WHERE id_clave=$IDC" > /dev/null
paso "unicidad (sesion, asistente)" "409" \
  "$(curl -s -o /dev/null -w "%{http_code}" -X POST "$B/api/acceso/validar" \
       -H "Content-Type: application/json" -d "{\"id_clave\":$IDC,\"clave\":\"$CLAVE\"}")"

echo
echo "10 · Responder la encuesta"
P1=$(db "SELECT id_pregunta FROM catedras.pregunta ORDER BY orden LIMIT 1")
P2=$(db "SELECT id_pregunta FROM catedras.pregunta ORDER BY orden OFFSET 1 LIMIT 1")
P3=$(db "SELECT id_pregunta FROM catedras.pregunta ORDER BY orden OFFSET 2 LIMIT 1")
P4=$(db "SELECT id_pregunta FROM catedras.pregunta ORDER BY orden OFFSET 3 LIMIT 1")
CENC=$(curl -s -o "$TMP/enc.json" -w "%{http_code}" -X POST "$B/api/acceso/registro/$IDR/encuesta" \
        -H "Content-Type: application/json" \
        -d "{\"respuestas\":[{\"pregunta\":$P1,\"numero\":5},{\"pregunta\":$P2,\"numero\":4},{\"pregunta\":$P3,\"numero\":1},{\"pregunta\":$P4,\"texto\":\"Todo bien\"}]}")
paso "encuesta aceptada" "200" "$CENC"

echo
echo "11 · Generar el lote de migracion"
L=$(curl -s -X POST "$B/api/migracion/sesion/$SES/generar" -H "$H")
paso "lote generado" "true" "$(echo "$L" | jq_ "print(str('id_lote_migracion' in d).lower())")"

echo
echo "12 · EL ARCHIVO PLANO DEL ASIS  ·  el criterio de aceptacion duro"
CARC=$(curl -s -o "$TMP/asis.xlsx" -w "%{http_code}" "$B/api/migracion/sesion/$SES/archivo" -H "$H")
paso "HTTP del archivo" "200" "$CARC"
python - "$TMP/asis.xlsx" <<'PY'
import openpyxl, sys
ws = openpyxl.load_workbook(sys.argv[1]).active
print('       filas=%d  columnas=%d' % (ws.max_row, ws.max_column))
print('       fila 1:', [c.value for c in ws[1]])
n = min(ws.max_row, 50)
pruebas = [
    ('3 columnas exactas',      ws.max_column == 3),
    ('sin fila de encabezado',  str(ws.cell(1,2).value or '').lower() not in ('id_asis','id','emplid')),
    ('ID como TEXTO',           all(isinstance(ws.cell(r,2).value, str) for r in range(1, n+1))),
    ('programa como TEXTO',     all(isinstance(ws.cell(r,3).value, str) for r in range(1, n+1))),
    ('sin espacios sobrantes',  all(str(ws.cell(r,c).value) == str(ws.cell(r,c).value).strip()
                                    for r in range(1, n+1) for c in (2,3))),
    ('reunion es numero',       all(isinstance(ws.cell(r,1).value, int) for r in range(1, n+1))),
]
for t, v in pruebas:
    print('       %s %s' % ('\033[32mOK \033[0m' if v else '\033[31mMAL\033[0m', t))
sys.exit(0 if all(v for _, v in pruebas) else 1)
PY
ARCH=$?
[ $ARCH -eq 0 ] && OK=$((OK+6)) || MAL=$((MAL+1))

echo
echo "=========================================="
printf "  OK: %d    MAL: %d\n" "$OK" "$MAL"
echo "=========================================="
[ "$MAL" -eq 0 ] || exit 1
