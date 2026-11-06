# Reglas operativas — Unoavanza CRM

## 📑 Fuente de verdad primero (regla anti-preguntas)

**Antes de preguntarle al usuario cualquier dato operativo** (módulos, campos,
responsables/ejecutivos, mapeos, estructura del CRM, decisiones ya tomadas),
consultar en este orden:

1. El repo `unoavanza-zoho-crm` — `CLAUDE.md`, `docs/`, código y configs.
2. Notion — CRM Operations, Decision Log, Runbooks, Inbox Diario.
3. El CRM vía MCP (`unoavanza-crm-readonly` / `unoavanza-crm-rw`).

Solo preguntar al usuario lo que **no esté** en ninguna de esas fuentes. Si falta
acceso a una fuente, **pedir el acceso** — no suplirlo preguntando algo ya documentado.

> Alineado con el principio Karpathy: *fuente única = Notion* + *Think Before Coding*
> (no asumir, pero tampoco preguntar lo ya documentado). Toda sesión de trabajo debe
> arrancar con **repo + Notion conectados**.

---

## Bloque para pegar en el `CLAUDE.md` del repo `unoavanza-zoho-crm`

```markdown
## Fuente de verdad primero (regla anti-preguntas)

Antes de preguntar al usuario cualquier dato operativo (módulos, campos,
responsables, mapeos, estructura, decisiones ya tomadas), consulta en orden:
1. Este repo: CLAUDE.md, docs/, código, configs.
2. Notion: CRM Operations, Decision Log, Runbooks, Inbox Diario.
3. El CRM vía MCP de Zoho.
Solo pregunta al usuario lo que no esté en ninguna de esas fuentes. Si falta
acceso a una fuente, pide el acceso — no lo suplas preguntando lo ya documentado.
```

*Añadido: 2026-10-01 · Pendiente replicar en Notion (Acuerdo de Eficiencia) cuando se resuelva el límite de bloques.*
