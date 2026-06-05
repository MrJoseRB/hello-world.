# 🛰️ AI Market Radar — Plan de acción / "Brain" del proyecto

> Sistema de inteligencia de mercado que monitorea el ecosistema de IA y entrega
> a Notion **solo** lo relevante para el portafolio de Jose, puntuado y razonado.
>
> Estado: **diseño aprobado**, MVP en construcción.
> Branch: `claude/ai-market-monitoring-design-04a8i`

---

## 0. Decisiones tomadas (no asumir, confirmadas con el usuario)

| Decisión        | Valor                          | Implicación de diseño |
|-----------------|--------------------------------|-----------------------|
| Frecuencia      | **Semanal (lunes)**            | Job programado, no agente always-on |
| Presupuesto     | **$10–30/mes**                 | Claude real: Haiku (filtra) + Sonnet (razona) |
| Notion          | **Desde cero**                 | Integración + DB creadas en esta sesión |
| Motor LLM       | **Claude puro**                | Un solo SDK (`anthropic`), sin Ollama/Groq aquí |

---

## 1. Portafolio = filtro de relevancia

1. **Unoavanza** — CRM en Zoho para corredor de seguros venezolano.
   Stack: Zoho CRM Professional, Kiosk Studio, webhooks en Railway, FastAPI,
   Notion como cola de mensajes.
2. **Incruise** — proyecto cliente nuevo en discovery.
3. **Canal YouTube "From Window Cleaner to SaaS Builder"** — pipeline de video,
   guion, voice-clone, B-roll, Remotion/render.
4. **Capa de orquestación de agentes** — Claude API + Codex + Notion,
   arquitectura híbrida Ollama/Groq (rutina) + Claude (razonamiento duro).
5. **Producto modular de IA para corredores de seguros** (productizar Unoavanza).

**Qué cuenta como herramienta:** repos GitHub, software comercial nuevo,
librerías, modelos, APIs, y técnicas/patrones desconocidos que apliquen a lo de
arriba. **NO** herramientas genéricas de productividad.

---

## 2. Enfoques evaluados

### A — Script Python + Railway Cron Job (scheduled) ✅ ELEGIDO
- Reutiliza Railway + FastAPI + Notion que ya existen.
- Corre solo los lunes; costo casi nulo (~1 min/semana).
- Mismo SDK que la capa de orquestación.

### B — Agente always-on en Railway (worker + APScheduler)
- Disparo on-demand, pero paga un contenedor 24/7 para una tarea semanal.
- Sobre-ingeniería para esta cadencia.

### C — Workflow nativo en Notion (Automations / Make / Zapier)
- Cero código de infra, pero no permite scoring/razonamiento con Claude
  sin pegar otra herramienta; lógica atrapada en un GUI no versionable.

**Recomendación: A**, con matiz híbrido → el mismo `digest.py` se ejecuta por
cron los lunes **y** a mano desde `iPhone → Tailscale → Termius → tmux → Claude Code`.

---

## 3. Fuentes a monitorear

| Fuente | Consumo (gratis) | Sirve a |
|---|---|---|
| **GitHub Search API** | REST + token | Orquestación (`ai-agents`, `llm`, `mcp`), Seguros (`crm`), Video (`remotion`) |
| **arXiv API** | `feedparser`, sin auth (`cs.AI`,`cs.CL`,`cs.MA`) | Razonamiento duro / técnicas nuevas |
| **Hacker News (Algolia)** | REST sin auth | Software comercial nuevo + debates SaaS |
| **Hugging Face Hub** | `huggingface_hub` | Voice-clone/TTS (YouTube), modelos |
| **Product Hunt** | GraphQL + token | Software comercial de IA → producto seguros |
| **Newsletters** (Smol AI/AI News, Latent Space, TLDR AI, Ben's Bites, Coverager) | RSS + `feedparser` | Curaduría humana alta señal |
| **Zoho Developer / Release Notes** | RSS | **Unoavanza** (CRM API, Kiosk Studio) |
| **Remotion releases** | GitHub API | Pipeline de video |
| **Anthropic / Groq / Ollama blogs** | RSS | Capa de orquestación |

**MVP usa solo 3:** GitHub + arXiv + Hacker News (APIs gratis, sin auth dolorosa).

---

## 4. Rubric de puntuación (0–100)

| Eje | Peso | Escala |
|---|---|---|
| **Relevancia a portafolio** | 40 | 0 genérico · 20 tangencial a 1 proyecto · 40 ataca dolor directo |
| **Madurez** | 20 | 0 paper/pre-alpha · 10 beta con tracción · 20 estable + docs |
| **Esfuerzo de integración** (inverso) | 20 | 0 reescribir todo · 10 medio · 20 `pip install`/API limpia |
| **Modelo de costo** | 20 | 0 enterprise · 10 freemium limitado · 20 OSS/free generoso |

**Cortes:** ≥75 "acciona esta semana" · 50–74 "en el radar" · <50 se descarta.

---

## 5. Base de datos Notion: `🛰️ AI Market Radar`

Ubicación: `🏢 Jose AI Business HQ → 🤖 AI Operating System`
(page id `352f666c-275b-81ef-9766-f2df8e2a79da`).

> ✅ **DB creada vía MCP** — id `91a123f134be487f8422d728cdd847ab`
> · URL https://app.notion.com/p/91a123f134be487f8422d728cdd847ab
> · sembrada con 1 fila de ejemplo (Remotion, score 82) para validar el esquema.

| Propiedad | Tipo | Notas |
|---|---|---|
| Herramienta | Title | — |
| Score | Formula | suma de los 4 sub-scores (0–100) |
| Relevancia / Madurez / Integración / Costo (pts) | Number | los escribe Claude |
| Proyecto que aplica | Multi-select | Unoavanza, Incruise, YouTube SaaS, Orquestación Agentes, Producto Seguros |
| Fuente | Select | GitHub, arXiv, HackerNews, HuggingFace, ProductHunt, Newsletter |
| Tipo | Select | Repo, Modelo, API, Librería, Técnica, Software |
| Link | URL | — |
| Fecha | Date | detección |
| Costo | Select | Free, Freemium, Pago |
| Por qué me importa a mí | Text | razonamiento de Sonnet, personalizado al portafolio |
| Estado | Status/Select | Nuevo, Revisando, Probando, Integrado, Descartado |

### Qué conectar (setup)
1. `notion.so/my-integrations` → New internal integration → copia el secret (`ntn_...`).
2. Crear la DB (ya creada vía MCP en esta sesión, o con `create_notion_db.py`).
3. DB → `•••` → **Connections** → conectar la integración (sin esto: 404).
4. Copiar `database_id` de la URL (32 chars antes del `?`).
5. Guardar en Railway + `.env` local: `NOTION_TOKEN`, `NOTION_DB_ID`, `ANTHROPIC_API_KEY`.
6. `pip install -r requirements.txt`.

---

## 6. Plan MVP (esta semana)

`digest.py` de ~150 líneas, ejecutable a mano desde tmux:

1. `fetch()` — GitHub + arXiv + HN, últimos 7 días, queries fijas.
2. `dedupe()` — por URL/título.
3. `score()` — Haiku puntúa el lote con el rubric → JSON por item.
4. `reason()` — Sonnet escribe "por qué me importa" para items ≥ 75.
5. `write_notion()` — una página por item en la DB.

Costo por corrida ≈ $0.05–0.20.

```bash
python digest.py            # barrido semanal
python digest.py --dry-run  # imprime sin escribir a Notion
```

**NO en el MVP:** scheduler propio, dashboard, dedupe semántico, vector DB,
las 9 fuentes. Eso mataría el "esta semana".

### Fase 2
- Railway Cron Schedule `0 7 * * 1` → `python digest.py`.
- Añadir fuentes por RSS (newsletters, HF, Zoho, Remotion, blogs de modelos).

---

## 7. Checklist de ejecución

- [x] Diseño aprobado y registrado (este doc)
- [x] DB `🛰️ AI Market Radar` creada en Notion vía MCP
- [x] `digest.py` (3 fuentes + scoring Haiku + reasoning Sonnet + escritura REST)
- [x] `create_notion_db.py` (fallback REST para recrear la DB)
- [x] `requirements.txt` + `README.md` con setup
- [ ] **(Usuario)** crear integración interna + pegar `NOTION_TOKEN`
- [ ] **(Usuario)** conectar la integración a la DB (Connections)
- [ ] **(Usuario)** poner `ANTHROPIC_API_KEY` y `NOTION_DB_ID` en `.env`
- [ ] **(Usuario)** primera corrida `python digest.py --dry-run`
- [ ] Fase 2: Railway cron semanal
