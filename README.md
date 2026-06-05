# 🛰️ AI Market Radar

Sistema de inteligencia de mercado que monitorea el ecosistema de IA y escribe
en Notion **solo** lo relevante para el portafolio de Jose, ya puntuado (0–100)
y con un razonamiento de "por qué me importa a mí".

> Diseño completo y plan de acción: [`docs/ai-market-radar-design.md`](docs/ai-market-radar-design.md)

## Cómo funciona (MVP)

```
GitHub + arXiv + Hacker News  →  Claude Haiku (puntúa)  →  Claude Sonnet
        (últimos 7 días)            con el rubric            (razona top ≥75)
                                                                   │
                                                                   ▼
                                                    Notion · 🛰️ AI Market Radar
```

## Setup (una sola vez)

1. **Crear la integración de Notion**
   - Ve a https://www.notion.so/my-integrations → *New integration* → tipo
     **Internal** → nómbrala `AI Market Radar Bot`.
   - Copia el **Internal Integration Secret** (empieza con `ntn_...`).

2. **Conectar la integración a la base de datos**
   - La DB `🛰️ AI Market Radar` ya vive en `🏢 Jose AI Business HQ → 🤖 AI Operating System`.
   - Ábrela → menú `•••` (arriba a la derecha) → **Connections** → conecta
     `AI Market Radar Bot`.
   - ⚠️ Sin este paso la API devuelve **404** aunque el token sea válido.

3. **Variables de entorno** (crea un `.env` local y/o ponlas en Railway)

   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   export NOTION_TOKEN=ntn_...
   export NOTION_DB_ID=91a123f134be487f8422d728cdd847ab   # ya creada en tu workspace
   export GITHUB_TOKEN=ghp_...    # opcional, sube el rate limit de GitHub
   ```

4. **Instalar dependencias**

   ```bash
   pip install -r requirements.txt
   ```

## Uso

```bash
python digest.py --dry-run   # prueba: imprime resultados, NO escribe en Notion
python digest.py             # barrido real y escritura en Notion
```

Flujo mobile-first: `iPhone → Tailscale → Termius → tmux → Claude Code`.

## Recrear la base de datos (opcional)

La DB ya fue creada vía MCP. Si necesitas recrearla por API REST:

```bash
NOTION_PARENT_PAGE=352f666c-275b-81ef-9766-f2df8e2a79da python create_notion_db.py
```

## Fase 2 — automatización semanal

Añade un **Cron Schedule** en tu proyecto Railway existente:

```
0 7 * * 1   python digest.py
```

(lunes 7am). Comparte las mismas variables de entorno que tu FastAPI actual.
