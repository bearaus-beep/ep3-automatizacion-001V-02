# EP3 — Implementación de Automatización de Red con Compliance Auditado

**Alumno:** 001V-02  
**Curso:** DRY7122 — Programación y Redes Virtualizadas (SDN-NFV)  
**Institución:** DUOC UC — Escuela de Informática y Telecomunicaciones  

---

## 1. Objetivo del proyecto

El presente proyecto consistió en la incorporación automatizada de un router Cisco CSR1000v a la red corporativa de **Inmobiliaria Central Ltda.**, aplicando el ciclo completo de aprovisionamiento: documentación del estado inicial, configuración automatizada mediante Ansible, y validación independiente vía NETCONF y RESTCONF. El objetivo final fue entregar el equipo en estado operativo y certificado como conforme a los estándares de la empresa.

---

## 2. Alcance

**Dentro del alcance:**
- Captura del estado inicial del router (baseline) con pyATS/Genie.
- Habilitación de NETCONF, RESTCONF e IP HTTP Secure Server.
- Aplicación de configuración corporativa: hostname, banner, NTP, descripción WAN, interfaz Loopback de gestión.
- Validación de la configuración aplicada mediante NETCONF (ncclient) y RESTCONF (requests).
- Generación de certificado de compliance y diff baseline vs. estado final.

**Fuera del alcance:**
- Configuración de routing dinámico (OSPF, BGP, etc.).
- Configuración de VLANs, ACLs o políticas de QoS.
- Integración con sistemas de monitoreo (SNMP, Syslog).

**Herramientas utilizadas:** pyATS/Genie, Ansible (cisco.ios), ncclient, Python requests, Git/GitHub.

---

## 3. Infraestructura utilizada

| Componente | Detalle |
|---|---|
| Estación de trabajo | DEVASC VM (Ubuntu) — devasc@labvm |
| Router cliente | Cisco CSR1000v — 192.168.56.101 |
| Sistema operativo VM | Ubuntu 20.04 LTS |
| Python | 3.8+ |
| Ansible | 2.12+ con colección cisco.ios |
| pyATS / Genie | 23.x |
| ncclient | 0.6.x |
| Git | 2.x |

---

## 4. Tecnologías empleadas y justificación

| Tecnología | Fase | Justificación |
|---|---|---|
| **pyATS / Genie** | Fase 1 y 5 | Permite capturar el estado estructurado del router vía SSH sin requerir NETCONF habilitado, ideal para documentar el estado inicial y generar diffs automáticos entre snapshots. |
| **Ansible** | Fase 2 | Herramienta de aprovisionamiento declarativo e idempotente: permite aplicar configuración reproducible al router y verificar que el estado deseado se mantiene en ejecuciones sucesivas. |
| **NETCONF** | Fase 3 | Protocolo de gestión de red basado en XML que permite consultar el árbol de configuración completo del dispositivo de forma estructurada, sirviendo como validación independiente del aprovisionamiento. |
| **RESTCONF** | Fase 4 | Interfaz REST sobre YANG que permite consultar recursos de configuración individuales en formato JSON mediante URLs específicas, complementando la validación de NETCONF. |

---

## 5. Configuración aplicada

| Parámetro | Valor final en el router |
|---|---|
| Hostname | RTR-INMOCEN |
| IP Loopback10 | 10.1.2.1 |
| Máscara Loopback10 | 255.255.255.0 |
| Descripción GigabitEthernet1 | Enlace-WAN-Valparaiso |
| Banner MOTD | ACCESO RESTRINGIDO - INMOCEN |
| Servidor NTP | 8.8.8.8 |
| NETCONF | Habilitado (puerto 830) |
| RESTCONF | Habilitado |
| IP HTTP Secure Server | Habilitado (puerto 443) |

---

## 6. Resultados de validación

### NETCONF (Fase 3) — 5/5 criterios

| Criterio | Esperado | Resultado |
|---|---|---|
| Hostname corporativo | RTR-INMOCEN | CONFORME |
| IP Loopback10 | 10.1.2.1 | CONFORME |
| Máscara Loopback10 | 255.255.255.0 | CONFORME |
| Descripción WAN (Gi1) | Enlace-WAN-Valparaiso | CONFORME |
| Servidor NTP | 8.8.8.8 | CONFORME |

### RESTCONF (Fase 4) — 4/4 criterios

| Criterio | Esperado | Resultado |
|---|---|---|
| Hostname corporativo | RTR-INMOCEN | CONFORME |
| IP Loopback10 | 10.1.2.1 | CONFORME |
| Descripción WAN (Gi1) | Enlace-WAN-Valparaiso | CONFORME |
| Servidor NTP | 8.8.8.8 | CONFORME |

**Resultado global: CONFORME**

---

## 7. Conclusiones

El router Cisco CSR1000v de **Inmobiliaria Central Ltda.** fue aprovisionado exitosamente con la configuración corporativa estándar. Todos los criterios de validación vía NETCONF (5/5) y RESTCONF (4/4) resultaron CONFORMES. El equipo ha sido entregado a operaciones en estado operativo. El diff generado por Genie entre el baseline inicial y el snapshot final confirma que los cambios configurados corresponden exactamente a los parámetros asignados, sin modificaciones no planificadas. Todo el proceso quedó auditado en el historial de commits del repositorio ep3-automatizacion-001V-02.
