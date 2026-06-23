#!/usr/bin/env python3
"""
generar_certificado.py — Fase 5: Reporte de Compliance
Alumno: 001V-02
Curso: DRY7122 — Programacion y Redes Virtualizadas (SDN-NFV)
"""

import os
import sys
import socket
import glob
from datetime import datetime
import yaml

VARS_PATH = os.path.join(os.path.dirname(__file__), "..", "vars", "vars_001V-02.yaml")
with open(VARS_PATH, "r") as f:
    vars_data = yaml.safe_load(f)

ALUMNO   = vars_data["alumno"]["codigo"]
NOMBRE   = vars_data["alumno"]["nombre"]
EMPRESA  = vars_data["cliente"]["empresa"]
HOSTNAME = vars_data["cliente"]["hostname"]

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
EV_DIR   = os.path.join(os.path.dirname(__file__), "evidencias")

NETCONF_OUTPUT  = os.path.join(BASE_DIR, "fase3_validacion_netconf", "evidencias", "output_validacion_netconf.txt")
RESTCONF_OUTPUT = os.path.join(BASE_DIR, "fase4_validacion_restconf", "evidencias", "output_validacion_restconf.txt")
DIFF_DIR        = os.path.join(EV_DIR, f"diff_{ALUMNO}")

def check_result_file(filepath, label):
    if not os.path.exists(filepath):
        print(f"[WARN] No se encontro el archivo: {filepath}")
        return False, "ARCHIVO NO ENCONTRADO"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if "RESULTADO GLOBAL: CONFORME" in content:
        return True, "CONFORME"
    elif "RESULTADO GLOBAL: NO CONFORME" in content:
        return False, "NO CONFORME"
    else:
        return False, "INDETERMINADO"

def check_diff():
    if not os.path.exists(DIFF_DIR):
        return False, "Directorio de diff no encontrado"
    files = glob.glob(os.path.join(DIFF_DIR, "**", "*"), recursive=True)
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        return False, "Diff vacio — no se detectaron cambios"
    return True, f"{len(files)} archivo(s) de diff generados"

print("=" * 62)
print("GENERANDO CERTIFICADO DE COMPLIANCE")
print("=" * 62)
print()

netconf_ok,  netconf_res  = check_result_file(NETCONF_OUTPUT,  "NETCONF")
restconf_ok, restconf_res = check_result_file(RESTCONF_OUTPUT, "RESTCONF")
diff_ok,     diff_msg     = check_diff()

compliance_global = netconf_ok and restconf_ok
estado_global     = "CONFORME" if compliance_global else "NO CONFORME"
fecha_emision     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

certificado = f"""
╔══════════════════════════════════════════════════════════════╗
║           CERTIFICADO DE COMPLIANCE DE RED                   ║
║       DRY7122 — Programacion y Redes Virtualizadas           ║
╚══════════════════════════════════════════════════════════════╝

DATOS DEL ALUMNO
  Codigo   : {ALUMNO}
  Nombre   : {NOMBRE}

DATOS DEL PROYECTO
  Empresa cliente  : {EMPRESA}
  Hostname router  : {HOSTNAME}
  Host VM          : {socket.gethostname()}
  Fecha emision    : {fecha_emision}

RESULTADOS DE VALIDACION
  ┌─────────────────────────────┬─────────────────┐
  │ Protocolo                   │ Resultado       │
  ├─────────────────────────────┼─────────────────┤
  │ NETCONF  (Fase 3 - 5/5 OK)  │ {netconf_res:<15} │
  │ RESTCONF (Fase 4 - 4/4 OK)  │ {restconf_res:<15} │
  │ Diff baseline vs final      │ {"OK" if diff_ok else "NO OK":<15} │
  └─────────────────────────────┴─────────────────┘

  Detalle diff: {diff_msg}

══════════════════════════════════════════════════════════════
  RESULTADO GLOBAL DE COMPLIANCE: {estado_global}
══════════════════════════════════════════════════════════════

Este certificado confirma que el router {HOSTNAME} de la empresa
{EMPRESA} ha sido aprovisionado, validado y entregado a
operaciones en estado {"OPERATIVO" if compliance_global else "CON OBSERVACIONES"}.

Generado automaticamente por generar_certificado.py
"""

print(certificado)

os.makedirs(EV_DIR, exist_ok=True)
cert_path = os.path.join(EV_DIR, f"certificado_compliance_{ALUMNO}.txt")
with open(cert_path, "w", encoding="utf-8") as f:
    f.write(certificado)

print(f"[INFO] Certificado guardado en: evidencias/certificado_compliance_{ALUMNO}.txt")
