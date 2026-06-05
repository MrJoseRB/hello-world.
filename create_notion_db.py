#!/usr/bin/env python3
"""
Crea la base de datos "🛰️ AI Market Radar" en Notion vía API REST.

Alternativa al MCP de Notion: úsalo si necesitas recrear la DB desde código
(por ejemplo en otro workspace). En esta sesión la DB ya fue creada vía MCP,
así que normalmente solo necesitas el `database_id` resultante en NOTION_DB_ID.

Requiere:
    NOTION_TOKEN        secret de la integración interna
    NOTION_PARENT_PAGE  id de la página "🤖 AI Operating System"
                        (por defecto: 352f666c-275b-81ef-9766-f2df8e2a79da)

Uso:
    NOTION_PARENT_PAGE=<page_id> python create_notion_db.py
"""
import os
import sys

from notion_client import Client

DEFAULT_PARENT = "352f666c-275b-81ef-9766-f2df8e2a79da"  # 🤖 AI Operating System

SCHEMA = {
    "Herramienta": {"title": {}},
    "Relevancia": {"number": {}},
    "Madurez": {"number": {}},
    "Integración": {"number": {}},
    "Costo (pts)": {"number": {}},
    "Score": {
        "formula": {
            "expression": (
                'prop("Relevancia") + prop("Madurez") '
                '+ prop("Integración") + prop("Costo (pts)")'
            )
        }
    },
    "Proyecto que aplica": {
        "multi_select": {
            "options": [
                {"name": "Unoavanza", "color": "blue"},
                {"name": "Incruise", "color": "purple"},
                {"name": "YouTube SaaS", "color": "red"},
                {"name": "Orquestación Agentes", "color": "green"},
                {"name": "Producto Seguros", "color": "orange"},
            ]
        }
    },
    "Fuente": {
        "select": {
            "options": [
                {"name": "GitHub"}, {"name": "arXiv"}, {"name": "HackerNews"},
                {"name": "HuggingFace"}, {"name": "ProductHunt"}, {"name": "Newsletter"},
            ]
        }
    },
    "Tipo": {
        "select": {
            "options": [
                {"name": "Repo"}, {"name": "Modelo"}, {"name": "API"},
                {"name": "Librería"}, {"name": "Técnica"}, {"name": "Software"},
            ]
        }
    },
    "Link": {"url": {}},
    "Fecha": {"date": {}},
    "Costo": {
        "select": {
            "options": [
                {"name": "Free", "color": "green"},
                {"name": "Freemium", "color": "yellow"},
                {"name": "Pago", "color": "red"},
            ]
        }
    },
    "Por qué me importa a mí": {"rich_text": {}},
    "Estado": {
        "select": {
            "options": [
                {"name": "Nuevo", "color": "blue"},
                {"name": "Revisando", "color": "yellow"},
                {"name": "Probando", "color": "orange"},
                {"name": "Integrado", "color": "green"},
                {"name": "Descartado", "color": "gray"},
            ]
        }
    },
}


def main() -> int:
    token = os.getenv("NOTION_TOKEN")
    if not token:
        print("ERROR: falta NOTION_TOKEN", file=sys.stderr)
        return 1
    parent = os.getenv("NOTION_PARENT_PAGE", DEFAULT_PARENT)
    notion = Client(auth=token)
    db = notion.databases.create(
        parent={"type": "page_id", "page_id": parent},
        icon={"type": "emoji", "emoji": "🛰️"},
        title=[{"type": "text", "text": {"content": "🛰️ AI Market Radar"}}],
        properties=SCHEMA,
    )
    print(f"✅ Database creada: {db['id']}")
    print(f"   Ponla en tu .env como: NOTION_DB_ID={db['id']}")
    print(f"   URL: {db['url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
