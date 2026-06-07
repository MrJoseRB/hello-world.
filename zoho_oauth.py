#!/usr/bin/env python3
"""
Helper del OAuth de Zoho (Self Client, READ-ONLY) — data center .com (US).

Pasos (resumen; runbook completo en docs/zoho-setup-runbook.md):
1. Crea un Self Client en https://api-console.zoho.com (tipo "Self Client").
2. Pestaña "Generate Code": pega los scopes read-only, elige scope-duration y
   genera el GRANT CODE (¡caduca en minutos!).
3. Exporta credenciales e intercambia el grant code por un refresh token:
       export ZOHO_CLIENT_ID=...   ZOHO_CLIENT_SECRET=...
       python zoho_oauth.py exchange --code <GRANT_CODE>
4. Guarda el refresh_token impreso en tu .env como ZOHO_REFRESH_TOKEN.
5. Prueba una llamada read-only real:
       python zoho_oauth.py test --module Leads

Nunca pegues estos secretos en el chat; viven en .env / variables de Railway.
"""
from __future__ import annotations

import argparse
import os
import sys

import httpx

ACCOUNTS = os.getenv("ZOHO_ACCOUNTS_DOMAIN", "https://accounts.zoho.com")
API = os.getenv("ZOHO_API_DOMAIN", "https://www.zohoapis.com")

# Scopes mínimos read-only para Unoavanza.
READ_ONLY_SCOPES = (
    "ZohoCRM.modules.READ,"
    "ZohoCRM.settings.READ,"
    "ZohoSearch.securesearch.READ"
)


def _creds() -> tuple[str, str]:
    try:
        return os.environ["ZOHO_CLIENT_ID"], os.environ["ZOHO_CLIENT_SECRET"]
    except KeyError as e:
        sys.exit(f"ERROR: falta variable de entorno {e}")


def exchange(code: str) -> int:
    cid, cs = _creds()
    r = httpx.post(
        f"{ACCOUNTS}/oauth/v2/token",
        data={
            "grant_type": "authorization_code",
            "client_id": cid,
            "client_secret": cs,
            "code": code,
        },
        timeout=30,
    )
    data = r.json()
    if "refresh_token" not in data:
        print(f"Sin refresh_token. Respuesta de Zoho: {data}", file=sys.stderr)
        print("Causas típicas: grant code caducado, scopes mal escritos, "
              "o data center equivocado.", file=sys.stderr)
        return 1
    print("✅ OAuth ok.")
    print(f"   access_token (temporal): {data.get('access_token')}")
    print(f"   api_domain: {data.get('api_domain')}")
    print("\nGuarda en tu .env:")
    print(f"   ZOHO_REFRESH_TOKEN={data['refresh_token']}")
    return 0


def access_token() -> str:
    cid, cs = _creds()
    rt = os.environ.get("ZOHO_REFRESH_TOKEN")
    if not rt:
        sys.exit("ERROR: falta ZOHO_REFRESH_TOKEN (corre primero 'exchange').")
    r = httpx.post(
        f"{ACCOUNTS}/oauth/v2/token",
        data={
            "grant_type": "refresh_token",
            "client_id": cid,
            "client_secret": cs,
            "refresh_token": rt,
        },
        timeout=30,
    )
    tok = r.json().get("access_token")
    if not tok:
        sys.exit(f"No se pudo refrescar el access token: {r.json()}")
    return tok


def test(module: str) -> int:
    at = access_token()
    headers = {"Authorization": f"Zoho-oauthtoken {at}"}
    m = httpx.get(f"{API}/crm/v7/settings/modules", headers=headers, timeout=30)
    print(f"GET settings/modules -> HTTP {m.status_code}")
    rec = httpx.get(
        f"{API}/crm/v7/{module}",
        params={"per_page": 1},
        headers=headers,
        timeout=30,
    )
    print(f"GET {module} (1 registro) -> HTTP {rec.status_code}")
    print(rec.text[:400])
    return 0 if m.status_code == 200 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Zoho OAuth read-only helper (.com)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ex = sub.add_parser("exchange", help="grant code -> refresh token")
    ex.add_argument("--code", required=True)
    te = sub.add_parser("test", help="prueba una llamada read-only")
    te.add_argument("--module", default="Leads")
    sub.add_parser("scopes", help="imprime los scopes read-only sugeridos")
    args = ap.parse_args()

    if args.cmd == "exchange":
        return exchange(args.code)
    if args.cmd == "test":
        return test(args.module)
    if args.cmd == "scopes":
        print(READ_ONLY_SCOPES)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
