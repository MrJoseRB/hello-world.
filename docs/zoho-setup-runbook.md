# 🔧 Zoho — Runbook de setup (data center .com / US)

> Conexión READ-ONLY con Zoho CRM de Unoavanza. Dos partes:
> A) Self Client (credenciales propias, Carril 2) · B) MCP oficial hospedado (Carril 1).
>
> Dominios fijos (.com): `accounts.zoho.com` · `www.zohoapis.com` · `api-console.zoho.com`

## Scopes read-only que usamos

```
ZohoCRM.modules.READ,ZohoCRM.settings.READ,ZohoSearch.securesearch.READ
```

Nada de `.ALL` ni de `WRITE/CREATE/DELETE` en esta fase.

---

## Parte A — Self Client (credenciales propias)

1. Entra a **https://api-console.zoho.com** con la cuenta de Unoavanza.
2. **Add Client → Self Client → Create**. (El tipo *Self Client* no pide redirect URI.)
3. Copia **Client ID** y **Client Secret**.
4. Pestaña **Generate Code**:
   - **Scope**: pega `ZohoCRM.modules.READ,ZohoCRM.settings.READ,ZohoSearch.securesearch.READ`
   - **Time Duration**: 10 minutes
   - **Scope Description**: lo que quieras (ej. "radar read-only")
   - **Create** → copia el **grant code** (⏰ caduca rápido).
5. En tu terminal (tmux), intercambia el código por un refresh token:
   ```bash
   export ZOHO_CLIENT_ID=...        # del paso 3
   export ZOHO_CLIENT_SECRET=...    # del paso 3
   pip install httpx
   python zoho_oauth.py exchange --code <GRANT_CODE>
   ```
6. Guarda en tu `.env` (NO en el chat):
   ```bash
   ZOHO_CLIENT_ID=...
   ZOHO_CLIENT_SECRET=...
   ZOHO_REFRESH_TOKEN=...   # lo imprime el comando anterior
   ```
7. Verifica con una llamada read-only real:
   ```bash
   python zoho_oauth.py test --module Leads
   ```
   Esperado: `HTTP 200` en `settings/modules` y un registro de `Leads`.

> El refresh token no caduca (salvo que lo revoques). Los access tokens se
> regeneran solos desde el refresh token (1 hora de vida c/u).

---

## Parte B — MCP oficial hospedado (scoped a CRM, read-only)

> ⚠️ La consola de Zoho MCP bloquea scraping, así que estos pasos describen el
> flujo general; confirma los nombres exactos de botones en la consola.

1. Entra a la **consola de Zoho MCP** (desde https://www.zoho.com/mcp/ o el
   apartado MCP dentro de Setup del CRM).
2. **Create Server** → selecciona el servicio **CRM**.
3. Define el **scope/permiso del servidor en READ-ONLY** (solo lectura de
   módulos/registros; sin create/update/delete).
4. Zoho genera un **endpoint del servidor MCP** (remoto) + su autenticación.
5. Conéctalo a tu cliente:
   - **Claude Desktop**: añade el servidor remoto en la config de MCP.
   - **Orquestador (Claude API en Railway)**: regístralo como MCP remoto.
6. Prueba 3 consultas read-only sobre datos reales:
   - "¿Cuántos leads se crearon este mes?"
   - "Busca la póliza del cliente <nombre>."
   - "Lista los campos del módulo de pólizas."

---

## Gotchas (recordatorio)

- **Data center**: aquí TODO es `.com`. Si algún día migran a `.eu`/`.in`,
  cambia `ZOHO_ACCOUNTS_DOMAIN` y `ZOHO_API_DOMAIN`.
- **Least privilege**: subir a write solo cuando confíes en el agente.
- **Workflow triggers**: al pasar a escritura, default `trigger:false` para no
  disparar los webhooks de Railway en bucle.
- **Grant code caduca** en minutos: si falla el `exchange`, regenera el código.
