#!/usr/bin/env python3
"""
validacion_restconf.py — Fase 4: Validacion via RESTCONF
Alumno: 001V-02
Curso: DRY7122 — Programacion y Redes Virtualizadas (SDN-NFV)
"""

import sys
import os
import json
import socket
from datetime import datetime
import requests
import yaml
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VARS_PATH = os.path.join(os.path.dirname(__file__), "..", "vars", "vars_001V-02.yaml")
with open(VARS_PATH, "r") as f:
    vars_data = yaml.safe_load(f)

ROUTER_IP       = vars_data["router"]["ip"]
ROUTER_USER     = vars_data["router"]["usuario"]
ROUTER_PASS     = vars_data["router"]["password"]
EXP_HOSTNAME    = vars_data["cliente"]["hostname"]
EXP_LOOPBACK_IP = vars_data["router"]["loopback_ip"]
EXP_DESC_WAN    = vars_data["router"]["descripcion_wan"]
EXP_NTP         = vars_data["router"]["ntp_server"]
LOOPBACK_ID     = vars_data["router"]["loopback_id"]
ALUMNO          = vars_data["alumno"]["codigo"]

BASE_URL = f"https://{ROUTER_IP}/restconf/data"
HEADERS  = {"Accept": "application/yang-data+json"}
AUTH     = (ROUTER_USER, ROUTER_PASS)
RESP_DIR = os.path.join(os.path.dirname(__file__), "evidencias", "responses")
os.makedirs(RESP_DIR, exist_ok=True)

print("=" * 60)
print(f"Script      : validacion_restconf.py")
print(f"Alumno      : {ALUMNO}")
print(f"Fecha/Hora  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Host VM     : {socket.gethostname()}")
print(f"Router IP   : {ROUTER_IP}")
print("=" * 60)
print()

def restconf_get(endpoint, filename):
    url = f"{BASE_URL}/{endpoint}"
    print(f"[GET] {url}")
    try:
        resp = requests.get(url, headers=HEADERS, auth=AUTH, verify=False, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        out_path = os.path.join(RESP_DIR, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"      Guardado en: evidencias/responses/{filename}")
        return data
    except requests.exceptions.RequestException as e:
        print(f"      [ERROR] {e}")
        return None

print("--- Consultando endpoints RESTCONF ---")
print()

data_hostname   = restconf_get("Cisco-IOS-XE-native:native/hostname", "get_hostname.json")
data_loopback   = restconf_get(f"ietf-interfaces:interfaces/interface=Loopback{LOOPBACK_ID}", "get_loopback.json")
data_interfaces = restconf_get("ietf-interfaces:interfaces/interface=GigabitEthernet1", "get_interfaces.json")
data_ntp        = restconf_get("Cisco-IOS-XE-native:native/ntp", "get_ntp.json")

print()

def safe_get(d, *keys):
    for k in keys:
        if not isinstance(d, dict):
            return "N/A"
        d = d.get(k, {})
    return str(d) if d else "N/A"

actual_hostname = "N/A"
if data_hostname:
    actual_hostname = safe_get(data_hostname, "Cisco-IOS-XE-native:hostname")

actual_loopback_ip = "N/A"
if data_loopback:
    iface = data_loopback.get("ietf-interfaces:interface", {})
    ipv4  = iface.get("ietf-ip:ipv4", {})
    addrs = ipv4.get("address", [])
    if addrs:
        actual_loopback_ip = addrs[0].get("ip", "N/A")

actual_desc_wan = "N/A"
if data_interfaces:
    iface = data_interfaces.get("ietf-interfaces:interface", {})
    actual_desc_wan = iface.get("description", "N/A")

actual_ntp = "N/A"
if data_ntp:
    ntp_block   = data_ntp.get("Cisco-IOS-XE-native:ntp", {})
    ntp_server  = ntp_block.get("Cisco-IOS-XE-ntp:server", {})
    server_list = ntp_server.get("server-list", [])
    if server_list:
        actual_ntp = server_list[0].get("ip-address", server_list[0].get("ip", "N/A"))

print("=" * 60)
print("REPORTE DE VALIDACION RESTCONF")
print("=" * 60)

resultados = []

def check(criterio, esperado, obtenido):
    ok = (str(obtenido).strip() == str(esperado).strip())
    estado = "[OK]  " if ok else "[FAIL]"
    print(f"{estado} {criterio}")
    print(f"       Esperado : {esperado}")
    print(f"       Obtenido : {obtenido}")
    resultados.append(ok)

check("Hostname corporativo",  EXP_HOSTNAME,    actual_hostname)
check("IP Loopback10",         EXP_LOOPBACK_IP, actual_loopback_ip)
check("Descripcion WAN (Gi1)", EXP_DESC_WAN,    actual_desc_wan)
check("Servidor NTP",          EXP_NTP,         actual_ntp)

print()
aprobados = sum(resultados)
total     = len(resultados)
print(f"Criterios CONFORMES: {aprobados}/{total}")
print()

if all(resultados):
    print("╔══════════════════════════════════╗")
    print("║   RESULTADO GLOBAL: CONFORME     ║")
    print("╚══════════════════════════════════╝")
else:
    print("╔══════════════════════════════════╗")
    print("║  RESULTADO GLOBAL: NO CONFORME   ║")
    print("╚══════════════════════════════════╝")
print()
