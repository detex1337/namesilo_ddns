#!/usr/bin/env python3
"""
NameSilo Dynamic DNS Updater
Actualiza el registro DNS de un dominio con la IP pública del equipo actual.
"""

import requests
import sys
import xml.etree.ElementTree as ET

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
API_KEY  = "aaa011fff100010000000"   # API Key de NameSilo (namesilo.com > Account > API)
DOMAIN   = "google.com"     # Dominio principal
HOST     = "@"                 # Subdominio: "@" = raíz, "www", "sub", etc.
TTL      = 3600                # TTL en segundos (mínimo 3600 en NameSilo)
# ──────────────────────────────────────────────────────────────────────────────

BASE_URL = "https://www.namesilo.com/api"

def get_public_ip() -> str:
    """Obtiene la IP pública del equipo usando varios servicios de respaldo."""
    services = [
        "http://v4.ident.me",
        "https://ip4.nnev.de",
        "https://v4.ifconfig.co",
        "https://ipv4.yunohost.org",
        "https://ipv4.icanhazip.com",
        "https://ipv4.wtfismyip.com/text",
        "https://ipv4.ipecho.roebert.eu",
    ]
    for url in services:
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            ip = resp.text.strip()
            print(f"[✓] IP pública detectada: {ip}  (via {url})")
            return ip
        except Exception:
            continue
    raise RuntimeError("No se pudo obtener la IP pública. Comprueba tu conexión.")

def get_public_ipv6() -> str:
    """Obtiene la IPv6 pública del equipo usando varios servicios de respaldo."""
    services = [
        "http://v6.ident.me",
        "https://ip6.nnev.de",
        "https://v6.ifconfig.co",
        "https://ipv6.yunohost.org",
        "https://ipv6.icanhazip.com",
        "https://ipv6.wtfismyip.com/text",
        "https://ipv6.ipecho.roebert.eu",
    ]
    for url in services:
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            ip = resp.text.strip()
            print(f"[✓] IPv6 pública detectada: {ip}  (via {url})")
            return ip
        except Exception:
            continue
    raise RuntimeError("No se pudo obtener la IPv6 pública. Comprueba tu conexión.")


def api_call(endpoint: str, params: dict) -> ET.Element:
    """Llama a la API de NameSilo y devuelve el elemento raíz XML."""
    params.update({"version": 1, "type": "xml", "key": API_KEY})
    resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=10)
    resp.raise_for_status()
    root = ET.fromstring(resp.text)
    code = root.findtext("reply/code", "")
    detail = root.findtext("reply/detail", "")
    if code != "300":
        raise RuntimeError(f"Error API [{code}]: {detail}")
    return root


def get_dns_records() -> list[dict]:
    """Lista todos los registros DNS del dominio."""
    root = api_call("dnsListRecords", {"domain": DOMAIN})
    records = []
    for r in root.findall("reply/resource_record"):
        records.append({
            "id":    r.findtext("record_id"),
            "host":  r.findtext("host"),
            "type":  r.findtext("type"),
            "value": r.findtext("value"),
            "ttl":   r.findtext("ttl"),
        })
    return records


def find_record(records: list[dict], host: str) -> dict | None:
    """Busca el registro A que coincide con el host indicado."""
    # NameSilo devuelve el host completo (ej: "sub.domain.com" o "domain.com")
    full_host = DOMAIN if host == "@" else f"{host}.{DOMAIN}"
    for r in records:
        if r["type"] == "A" and r["host"] == host:
            return r
    return None

def find_record_v6(records: list[dict], host: str) -> dict | None:
    """Busca el registro AAAA que coincide con el host indicado."""
    # NameSilo devuelve el host completo (ej: "sub.domain.com" o "domain.com")
    full_host = DOMAIN if host == "@" else f"{host}.{DOMAIN}"
    for r in records:
        if r["type"] == "AAAA" and r["host"] == host:
            return r
    return None


def update_record(record_id: str, current_ip: str):
    """Actualiza un registro A o AAAA existente."""
    api_call("dnsUpdateRecord", {
        "domain":    DOMAIN,
        "rrid":      record_id,
        "rrhost":    HOST,
        "rrvalue":   current_ip,
        "rrttl":     TTL,
    })
    print(f"[✓] Registro actualizado correctamente → {current_ip}")


def main():
    print("=" * 50)
    print("  NameSilo Dynamic DNS Updater")
    print("=" * 50)

    # 1. Obtener IP actual
    current_ip = get_public_ip()

    # 2. Obtener registros DNS
    print(f"[…] Consultando registros DNS de {DOMAIN}…")
    records = get_dns_records()

    # 3. Buscar el registro A del host
    record = find_record(records, HOST)

    if record is None:
        print(f"[!] No se encontró registro A para '{HOST}.{DOMAIN}'.")

    elif record["value"] == current_ip:
        print(f"[✓] La IP ya está actualizada ({current_ip}). No se requiere cambio.")

    else:
        print(f"[…] IP antigua: {record['value']} → Nueva: {current_ip}. Actualizando…")
        update_record(record["id"], current_ip)

    print("=" * 50)

    # Para ipv6
    current_ip = get_public_ipv6()

    print(f"[…] Consultando registros DNS de {DOMAIN}…")
    records = get_dns_records()

    record = find_record_v6(records, HOST)

    if record is None:
        print(f"[!] No se encontró registro AAAA para '{HOST}.{DOMAIN}'.")

    elif record["value"] == current_ip:
        print(f"[✓] La IPv6 ya está actualizada ({current_ip}). No se requiere cambio.")

    else:
        print(f"[…] IPv6 antigua: {record['value']} → Nueva: {current_ip}. Actualizando…")
        update_record(record["id"], current_ip)

    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[✗] Error: {e}", file=sys.stderr)
        sys.exit(1)