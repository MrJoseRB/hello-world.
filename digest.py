#!/usr/bin/env python3
"""
🛰️ AI Market Radar — MVP digest

Barre 3 fuentes (GitHub, arXiv, Hacker News) de los últimos 7 días, las puntúa
contra el portafolio de Jose con Claude Haiku, redacta el "por qué me importa"
con Claude Sonnet para las de score alto, y las escribe en la base de datos de
Notion "🛰️ AI Market Radar".

Uso:
    python digest.py            # barrido completo y escritura en Notion
    python digest.py --dry-run  # imprime resultados sin escribir en Notion

Requiere las variables de entorno:
    ANTHROPIC_API_KEY   clave de la API de Claude
    NOTION_TOKEN        secret de la integración interna de Notion (ntn_...)
    NOTION_DB_ID        id de la database "🛰️ AI Market Radar"
    GITHUB_TOKEN        (opcional) sube el rate limit de la GitHub Search API
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from dataclasses import dataclass, field

import feedparser
import httpx
from anthropic import Anthropic
from notion_client import Client as Notion

# --------------------------------------------------------------------------- #
# Configuración
# --------------------------------------------------------------------------- #
HAIKU = "claude-haiku-4-5-20251001"   # filtrado y scoring en lote (barato)
SONNET = "claude-sonnet-4-6"          # razonamiento del "por qué me importa"

LOOKBACK_DAYS = 7
SCORE_CUTOFF_NOTION = 50      # < 50 no se escribe en Notion (anti-ruido)
SCORE_CUTOFF_REASON = 75      # >= 75 recibe razonamiento de Sonnet

PROJECTS = [
    "Unoavanza",            # CRM Zoho para corredor de seguros
    "Incruise",             # cliente nuevo en discovery
    "YouTube SaaS",         # pipeline de video / Remotion / voice-clone
    "Orquestación Agentes", # Claude API + Codex + Notion, híbrido de modelos
    "Producto Seguros",     # productizar Unoavanza
]

PORTFOLIO_CONTEXT = """\
Portafolio del usuario (úsalo como ÚNICO filtro de relevancia):
1. Unoavanza — CRM en Zoho para corredor de seguros venezolano. Stack: Zoho CRM
   Professional, Kiosk Studio, webhooks en Railway, FastAPI, Notion como cola.
2. Incruise — proyecto cliente nuevo en discovery.
3. Canal YouTube "From Window Cleaner to SaaS Builder" — pipeline de video,
   guion, voice-clone, B-roll, Remotion/render.
4. Capa de orquestación de agentes — Claude API + Codex + Notion, arquitectura
   híbrida Ollama/Groq (rutina) + Claude (razonamiento duro).
5. Producto modular de IA para corredores de seguros (productizar Unoavanza).

NO son relevantes las herramientas genéricas de productividad."""

# Queries de GitHub mapeadas a proyectos del portafolio.
GITHUB_QUERIES = [
    "mcp server",
    "ai agents orchestration",
    "llm framework",
    "crm automation",
    "remotion video",
    "voice clone tts",
    "fastapi llm",
]
# Términos de búsqueda para Hacker News.
HN_QUERIES = ["AI agent", "LLM", "Claude", "insurance AI", "voice clone"]
# Categorías arXiv relevantes a la capa de razonamiento.
ARXIV_CATEGORIES = ["cs.AI", "cs.CL", "cs.MA"]


# --------------------------------------------------------------------------- #
# Modelo de datos
# --------------------------------------------------------------------------- #
@dataclass
class Item:
    name: str
    url: str
    source: str          # GitHub | arXiv | HackerNews
    summary: str         # descripción cruda de la fuente
    # rellenado por Claude:
    relevancia: int = 0
    madurez: int = 0
    integracion: int = 0
    costo_pts: int = 0
    proyectos: list[str] = field(default_factory=list)
    tipo: str = "Repo"
    costo: str = "Free"
    porque: str = ""

    @property
    def score(self) -> int:
        return self.relevancia + self.madurez + self.integracion + self.costo_pts


# --------------------------------------------------------------------------- #
# Fuentes
# --------------------------------------------------------------------------- #
def _since() -> str:
    return (dt.date.today() - dt.timedelta(days=LOOKBACK_DAYS)).isoformat()


def fetch_github() -> list[Item]:
    items: list[Item] = []
    headers = {"Accept": "application/vnd.github+json"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    with httpx.Client(timeout=30, headers=headers) as c:
        for q in GITHUB_QUERIES:
            params = {
                "q": f"{q} created:>={_since()}",
                "sort": "stars",
                "order": "desc",
                "per_page": 5,
            }
            r = c.get("https://api.github.com/search/repositories", params=params)
            if r.status_code != 200:
                print(f"  ! GitHub '{q}': HTTP {r.status_code}", file=sys.stderr)
                continue
            for repo in r.json().get("items", []):
                items.append(
                    Item(
                        name=repo["full_name"],
                        url=repo["html_url"],
                        source="GitHub",
                        summary=(repo.get("description") or "")
                        + f" | ⭐{repo.get('stargazers_count', 0)}"
                        + f" | {repo.get('language') or 'n/a'}",
                    )
                )
    return items


def fetch_arxiv() -> list[Item]:
    cats = "+OR+".join(f"cat:{c}" for c in ARXIV_CATEGORIES)
    url = (
        "http://export.arxiv.org/api/query?"
        f"search_query={cats}&sortBy=submittedDate&sortOrder=descending&max_results=15"
    )
    feed = feedparser.parse(url)
    items: list[Item] = []
    for e in feed.entries:
        items.append(
            Item(
                name=e.title.replace("\n", " ").strip(),
                url=e.link,
                source="arXiv",
                summary=e.summary.replace("\n", " ").strip()[:600],
            )
        )
    return items


def fetch_hackernews() -> list[Item]:
    items: list[Item] = []
    cutoff = int(
        (dt.datetime.now() - dt.timedelta(days=LOOKBACK_DAYS)).timestamp()
    )
    with httpx.Client(timeout=30) as c:
        for q in HN_QUERIES:
            params = {
                "query": q,
                "tags": "story",
                "numericFilters": f"created_at_i>{cutoff},points>30",
                "hitsPerPage": 5,
            }
            r = c.get("http://hn.algolia.com/api/v1/search", params=params)
            if r.status_code != 200:
                continue
            for hit in r.json().get("hits", []):
                link = hit.get("url") or (
                    f"https://news.ycombinator.com/item?id={hit['objectID']}"
                )
                items.append(
                    Item(
                        name=hit.get("title", "(sin título)"),
                        url=link,
                        source="HackerNews",
                        summary=f"{hit.get('points', 0)} pts, "
                        f"{hit.get('num_comments', 0)} comentarios",
                    )
                )
    return items


def dedupe(items: list[Item]) -> list[Item]:
    seen: set[str] = set()
    out: list[Item] = []
    for it in items:
        key = it.url.lower().rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


# --------------------------------------------------------------------------- #
# Scoring (Claude Haiku) + razonamiento (Claude Sonnet)
# --------------------------------------------------------------------------- #
SCORING_PROMPT = f"""\
{PORTFOLIO_CONTEXT}

Eres un analista de inteligencia de mercado. Puntúa CADA item del lote contra
el portafolio usando este rubric (devuelve enteros):

- relevancia (0-40): 0 genérico/productividad, 20 tangencial a 1 proyecto,
  40 ataca un dolor directo de algún proyecto.
- madurez (0-20): 0 paper/pre-alpha, 10 beta con tracción, 20 estable+docs.
- integracion (0-20): 0 reescribir todo, 10 esfuerzo medio,
  20 `pip install`/API REST limpia (encaja en Python/FastAPI/Notion/Railway).
- costo_pts (0-20): 0 enterprise, 10 freemium limitado, 20 OSS/free generoso.

También clasifica:
- proyectos: lista con 0+ de {PROJECTS}
- tipo: uno de [Repo, Modelo, API, Librería, Técnica, Software]
- costo: uno de [Free, Freemium, Pago]

Responde SOLO con un array JSON, un objeto por item EN EL MISMO ORDEN, con las
claves: relevancia, madurez, integracion, costo_pts, proyectos, tipo, costo.
Sin texto adicional, sin markdown."""


def score(client: Anthropic, items: list[Item]) -> None:
    if not items:
        return
    listing = "\n".join(
        f"{i}. [{it.source}] {it.name} — {it.summary}" for i, it in enumerate(items)
    )
    msg = client.messages.create(
        model=HAIKU,
        max_tokens=4096,
        system=SCORING_PROMPT,
        messages=[{"role": "user", "content": f"Items a puntuar:\n{listing}"}],
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1].lstrip("json").strip()
    scores = json.loads(raw)
    for it, s in zip(items, scores):
        it.relevancia = int(s.get("relevancia", 0))
        it.madurez = int(s.get("madurez", 0))
        it.integracion = int(s.get("integracion", 0))
        it.costo_pts = int(s.get("costo_pts", 0))
        it.proyectos = [p for p in s.get("proyectos", []) if p in PROJECTS]
        it.tipo = s.get("tipo", "Repo")
        it.costo = s.get("costo", "Free")


def reason(client: Anthropic, item: Item) -> None:
    msg = client.messages.create(
        model=SONNET,
        max_tokens=400,
        system=PORTFOLIO_CONTEXT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Herramienta: {item.name} ({item.source})\n"
                    f"Descripción: {item.summary}\n"
                    f"Proyectos detectados: {', '.join(item.proyectos) or 'n/a'}\n\n"
                    "En 2-3 frases concretas, explica POR QUÉ ESTO LE IMPORTA AL "
                    "USUARIO específicamente: qué proyecto mejora, qué dolor "
                    "resuelve y qué haría con ello esta semana. Sin relleno."
                ),
            }
        ],
    )
    item.porque = msg.content[0].text.strip()


# --------------------------------------------------------------------------- #
# Notion
# --------------------------------------------------------------------------- #
def write_notion(notion: Notion, db_id: str, item: Item) -> None:
    notion.pages.create(
        parent={"database_id": db_id},
        properties={
            "Herramienta": {"title": [{"text": {"content": item.name[:200]}}]},
            "Relevancia": {"number": item.relevancia},
            "Madurez": {"number": item.madurez},
            "Integración": {"number": item.integracion},
            "Costo (pts)": {"number": item.costo_pts},
            "Proyecto que aplica": {
                "multi_select": [{"name": p} for p in item.proyectos]
            },
            "Fuente": {"select": {"name": item.source}},
            "Tipo": {"select": {"name": item.tipo}},
            "Link": {"url": item.url},
            "Fecha": {"date": {"start": dt.date.today().isoformat()}},
            "Costo": {"select": {"name": item.costo}},
            "Por qué me importa a mí": {
                "rich_text": [{"text": {"content": item.porque[:1900]}}]
            },
            "Estado": {"select": {"name": "Nuevo"}},
        },
    )


# --------------------------------------------------------------------------- #
# Orquestación
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description="AI Market Radar digest")
    ap.add_argument(
        "--dry-run", action="store_true", help="no escribe en Notion, solo imprime"
    )
    args = ap.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: falta ANTHROPIC_API_KEY", file=sys.stderr)
        return 1
    if not args.dry_run and not (os.getenv("NOTION_TOKEN") and os.getenv("NOTION_DB_ID")):
        print("ERROR: faltan NOTION_TOKEN / NOTION_DB_ID (o usa --dry-run)", file=sys.stderr)
        return 1

    print(f"🛰️  AI Market Radar — barrido de los últimos {LOOKBACK_DAYS} días")
    items = dedupe(fetch_github() + fetch_arxiv() + fetch_hackernews())
    print(f"   {len(items)} items únicos recolectados")
    if not items:
        return 0

    client = Anthropic()
    print("   puntuando con Haiku...")
    score(client, items)
    items.sort(key=lambda x: x.score, reverse=True)

    kept = [it for it in items if it.score >= SCORE_CUTOFF_NOTION]
    print(f"   {len(kept)} items pasan el corte (score >= {SCORE_CUTOFF_NOTION})")

    for it in kept:
        if it.score >= SCORE_CUTOFF_REASON:
            reason(client, it)

    if args.dry_run:
        for it in kept:
            print(f"\n[{it.score:>3}] {it.name}  ({it.source})")
            print(f"      R{it.relevancia} M{it.madurez} I{it.integracion} C{it.costo_pts}"
                  f" | {it.tipo} | {it.costo} | {', '.join(it.proyectos) or '—'}")
            print(f"      {it.url}")
            if it.porque:
                print(f"      💡 {it.porque}")
        return 0

    notion = Notion(auth=os.environ["NOTION_TOKEN"])
    db_id = os.environ["NOTION_DB_ID"]
    for it in kept:
        write_notion(notion, db_id, it)
    print(f"   ✅ {len(kept)} páginas escritas en Notion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
