#!/usr/bin/env python3
"""
validacion_netconf.py — Fase 3: Validacion via NETCONF
Alumno: 001V-02
Curso: DRY7122 — Programacion y Redes Virtualizadas (SDN-NFV)
"""

import sys
import os
import socket
from datetime import datetime
from ncclient import manager
from lxml import etree
import yaml

# Cargar variables
VARS_PATH = os.path.join(os.path.dirname(__file__), "..", "vars", "vars_001V-02.yaml")
with open(VARS_PATH, "r") as f:
    vars_data = yaml.safe_load(f)

ROUTER_IP         = vars_data["router"]["ip"]
ROUTER_USER       = vars_data["router"]["usuario"]
ROUTER_PASS       = vars_data["router"]["password"]
EXP_HOSTNAME      = vars_data["cliente"]["hostname"]
EXP_LOOPBACK_IP   = vars_data["router"]["loopback_ip"]
EXP_LOOPBACK_MASK = vars_data["router"]["loopback_mask"]
EXP_DESC_WAN      = vars_data["router"]["descripcion_wan"]
EXP_NTP           = vars_data["router"]["ntp_server"]
LOOPBACK_ID       = vars_data["router"]["loopback_id"]
ALUMNO            = vars_data["alumno"]["codigo"]

EVIDENCIAS_DIR = os.path.join(os.path.dirname(__file__), "evidencias")
os.makedirs(EVIDENCIAS_DIR, exist_ok=True)

# Metadatos
print("=" * 60)
print(f"Script      : validacion_netconf.py")
print(f"Alumno      : {ALUMNO}")
print(f"Fecha/Hora  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Host VM     : {socket.gethostname()}")
print(f"Router IP   : {ROUTER_IP}")
print("=" * 60)
print()

NETCONF_FILTER = """
<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <hostname/>
    <interface>
      <GigabitEthernet>
        <name>1</name>
        <description/>
      </GigabitEthernet>
      <Loopback>
        <name/>
        <ip/>
      </Loopback>
    </interface>
    <ntp>
      <server xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ntp">
        <server-list/>
      </server>
    </ntp>
  </native>
</filter>
"""

print(f"[INFO] Conectando al router {ROUTER_IP} via NETCONF puerto 830...")

try:
    with manager.connect(
        host=ROUTER_IP,
        port=830,
        username=ROUTER_USER,
        password=ROUTER_PASS,
        hostkey_verify=False,
        allow_agent=False,
        look_for_keys=False,
        timeout=30
    ) as m:
        print("[INFO] Sesion NETCONF establecida correctamente.")
        print()

        rpc_reply = m.get_config(source="running", filter=NETCONF_FILTER)
        xml_raw = rpc_reply.xml

        raw_path = os.path.join(EVIDENCIAS_DIR, "rpc_reply_raw.xml")
        with open(raw_path, "w", encoding="utf-8") as f:
            root = etree.fromstring(xml_raw.encode("utf-8"))
            pretty = etree.tostring(root, pretty_print=True).decode("utf-8")
            f.write(pretty)
        print(f"[INFO] XML guardado en: evidencias/rpc_reply_raw.xml")
        print()

        ns = {
            "nc":  "urn:ietf:params:xml:ns:netconf:base:1.0",
            "ios": "http://cisco.com/ns/yang/Cisco-IOS-XE-native",
            "ntp": "http://cisco.com/ns/yang/Cisco-IOS-XE-ntp",
        }

        root = etree.fromstring(xml_raw.encode("utf-8"))
        data = root.find(".//ios:native", ns)

        hostname_el = data.find("ios:hostname", ns)
        actual_hostname = hostname_el.text.strip() if hostname_el is not None else "N/A"

        actual_loopback_ip   = "N/A"
        actual_loopback_mask = "N/A"
        for lb in data.findall(".//ios:interface/ios:Loopback", ns):
            lb_name = lb.find("ios:name", ns)
            if lb_name is not None and lb_name.text.strip() == str(LOOPBACK_ID):
                ip_el   = lb.find(".//ios:ip/ios:address/ios:primary/ios:address", ns)
                mask_el = lb.find(".//ios:ip/ios:address/ios:primary/ios:mask", ns)
                if ip_el   is not None: actual_loopback_ip   = ip_el.text.strip()
                if mask_el is not None: actual_loopback_mask = mask_el.text.strip()

        actual_desc_wan = "N/A"
        for gig in data.findall(".//ios:interface/ios:GigabitEthernet", ns):
            gig_name = gig.find("ios:name", ns)
            if gig_name is not None and gig_name.text.strip() == "1":
                desc_el = gig.find("ios:description", ns)
                if desc_el is not None:
                    actual_desc_wan = desc_el.text.strip()

        actual_ntp = "N/A"
        for srv in data.findall(".//ntp:server/ntp:server-list", ns):
            ip_el = srv.find("ntp:ip", ns)
            if ip_el is not None:
                actual_ntp = ip_el.text.strip()
                break

        print("=" * 60)
        print("REPORTE DE VALIDACION NETCONF")
        print("=" * 60)

        resultados = []

        def check(criterio, esperado, obtenido):
            ok = (obtenido.strip() == esperado.strip())
            estado = "[OK]  " if ok else "[FAIL]"
            print(f"{estado} {criterio}")
            print(f"       Esperado : {esperado}")
            print(f"       Obtenido : {obtenido}")
            resultados.append(ok)

        check("Hostname corporativo",  EXP_HOSTNAME,     actual_hostname)
        check("IP Loopback10",         EXP_LOOPBACK_IP,  actual_loopback_ip)
        check("Mascara Loopback10",    EXP_LOOPBACK_MASK,actual_loopback_mask)
        check("Descripcion WAN (Gi1)", EXP_DESC_WAN,     actual_desc_wan)
        check("Servidor NTP",          EXP_NTP,          actual_ntp)

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

except Exception as e:
    print(f"[ERROR] No se pudo conectar via NETCONF: {e}")
    sys.exit(1)
