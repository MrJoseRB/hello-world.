#!/usr/bin/env python3
"""
🔌 Zoho CRM MCP server (READ-ONLY) — Carril 2 de Unoavanza.

Servidor MCP propio, remoto (HTTP), construido sobre FastMCP. Reusa el
refresh token del Self Client para exponer 4 tools de SOLO LECTURA a tu capa
de orquestación (Claude API) o a Claude Desktop.

Ejecutar local (tmux):
    export ZOHO_CLIENT_ID=...  ZOHO_CLIENT_SECRET=...  ZOHO_REFRESH_TOKEN=...
    pip install -r requirements.txt
    python zoho_mcp_server.py            # streamable-http en 0.0.0.0:$PORT

Desplegar en Railway: mismo comando como start command; comparte las 3 env vars.
Data center .com por defecto (override con ZOHO_ACCOUNTS_DOMAIN / ZOHO_API_DOMAIN).

NOTA: solo lectura a propósito. Añadir create/update/delete es una decisión
explícita posterior (ojo con los workflow triggers que disparan webhooks).
"""
from __future__ import annotations

import os
import time

import httpx
from mcp.server.fastmcp import FastMCP

ACCOUNTS = os.getenv("ZOHO_ACCOUNTS_DOMAIN", "https://accounts.zoho.com")
API = os.getenv("ZOHO_API_DOMAIN", "https://www.zohoapis.com")

# Cache simple del access token (se regenera desde el refresh token, ~1h vida).
_token: dict[str, object] = {"value": None, "exp": 0.0}


def _access_token() -> str:
    if _token["value"] and time.time() < float(_token["exp"]) - 60:
        return str(_token["value"])
    try:
        creds = {
            "grant_type": "refresh_token",
            "client_id": os.environ["ZOHO_CLIENT_ID"],
            "client_secret": os.environ["ZOHO_CLIENT_SECRET"],
            "refresh_token": os.environ["ZOHO_REFRESH_TOKEN"],
        }
    except KeyError as e:
        raise RuntimeError(f"Falta variable de entorno {e}") from e
    r = httpx.post(f"{ACCOUNTS}/oauth/v2/token", data=creds, timeout=30)
    data = r.json()
    if "access_token" not in data:
        raise RuntimeError(f"No se pudo refrescar el token de Zoho: {data}")
    _token["value"] = data["access_token"]
    _token["exp"] = time.time() + int(data.get("expires_in", 3600))
    return str(_token["value"])


def _get(path: str, params: dict | None = None) -> dict:
    r = httpx.get(
        f"{API}/crm/v7/{path}",
        headers={"Authorization": f"Zoho-oauthtoken {_access_token()}"},
        params=params,
        timeout=30,
    )
    if r.status_code == 204:  # Zoho devuelve 204 cuando no hay resultados
        return {}
    r.raise_for_status()
    return r.json()


mcp = FastMCP(
    "Zoho CRM (read-only)",
    host="0.0.0.0",
    port=int(os.getenv("PORT", "8000")),
)


@mcp.tool()
def list_modules() -> list[dict]:
    """Lista los módulos del CRM con su api_name (Leads, Contacts, Deals y los
    módulos custom de pólizas). Úsalo primero para descubrir el api_name correcto."""
    data = _get("settings/modules")
    return [
        {"api_name": m.get("api_name"), "label": m.get("plural_label")}
        for m in data.get("modules", [])
        if m.get("api_supported")
    ]


@mcp.tool()
def get_module_fields(module: str) -> list[dict]:
    """Lista los campos (api_name, label, tipo) de un módulo. Sirve para saber
    por qué campo filtrar en search_records. 'module' es un api_name de list_modules."""
    data = _get("settings/fields", {"module": module})
    return [
        {
            "api_name": f.get("api_name"),
            "label": f.get("field_label"),
            "type": f.get("data_type"),
        }
        for f in data.get("fields", [])
    ]


@mcp.tool()
def search_records(module: str, criteria: str, per_page: int = 5) -> list[dict]:
    """Busca registros (read-only). 'criteria' usa la sintaxis de Zoho, p. ej.
    (Last_Name:equals:Pérez) o (Email:starts_with:jose). 'module' es un api_name.
    Devuelve hasta 'per_page' registros."""
    data = _get(module + "/search", {"criteria": criteria, "per_page": per_page})
    return data.get("data", [])


@mcp.tool()
def count_records(module: str) -> int:
    """Devuelve el número total de registros de un módulo (p. ej. cuántos Leads)."""
    data = _get(module + "/actions/count")
    return int(data.get("count", 0))


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
