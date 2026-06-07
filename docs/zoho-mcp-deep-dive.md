# 🔌 Zoho MCP — Deep dive (Unoavanza / Producto Seguros)

> Investigación verificada (jun 2026). Conecta la capa de orquestación de agentes
> (Claude API) con el CRM de Unoavanza. Cimiento del producto modular para corredores.

## TL;DR — estrategia de dos carriles

- **Carril 1 (ahora):** usar el **MCP oficial hospedado de Zoho**, servidor *scoped* a
  CRM, **read-only**, conectado a la capa de orquestación. Cero infra, sin costo extra.
- **Carril 2 (Fase 2, productizar):** **MCP propio en FastAPI/Railway** (fork de
  `junnaisystems/Zoho-CRM-MCP`, Python) para control multi-tenant per-broker.

## Las tres rutas

| Ruta | Qué es | Pros | Contras |
|---|---|---|---|
| **A. Oficial hospedado** | Endpoint remoto que hospeda Zoho, configurado en la consola MCP | Cero infra · oficial · scoping por app · remoto (ideal para Railway y mobile) | Menos control fino · caja cerrada · roadmap de Zoho |
| **B. Self-host FastAPI/Railway** | Fork de `junnaisystems/Zoho-CRM-MCP` (Python) | CRUD completo, bulk, `convert_lead`, related · multi-tenant · stack Python | Mantienes OAuth/hosting/updates |
| **C. Comunitario read-only** | `whiteside-daniel/zohocrm-mcpserver` (Node/Docker) | Rápido de probar · seguro (no escribe) | Node · solo 7 tools de lectura |

## Hechos verificados del MCP oficial

- Pre-construido y **hospedado por Zoho**; cubre CRM, Books, Desk, Projects, Analytics,
  Billing, Cliq y +15 apps.
- **Servidores scoped** (solo-CRM, solo-Billing) o unificados.
- **Sin pricing nuevo**: usa los límites de API de la edición existente (Professional tiene API).
- Compatible con Claude Desktop, Cursor, Windsurf y orquestadores vía Claude API.

## Tools típicos (server Python comunitario, referencia para Carril 2)

`get_modules`, `get_module_fields`, `get_records`, `get_record_by_id`, `create_record`,
`update_record`, `delete_record`, `search_records`, `bulk_create_records`,
`get_related_records`, `convert_lead`, `get_organization_info`, `get_users`.

OAuth via `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_SCOPE`,
`ZOHO_ACCOUNTS_DOMAIN`, `ZOHO_API_DOMAIN`.

## ⚠️ Gotchas específicos de Unoavanza

1. **Data center / región.** La cuenta venezolana puede vivir en `.com` (US), `.eu` o
   `.in`. Fija `ZOHO_ACCOUNTS_DOMAIN` (`accounts.zoho.com/.eu/.in`) y `ZOHO_API_DOMAIN`
   (`zohoapis.com/.eu/.in`). Dominio equivocado = OAuth falla con errores crípticos.
   Confírmalo en la URL del CRM.
2. **Least privilege.** Arrancar solo lectura:
   `ZohoCRM.modules.READ, ZohoCRM.settings.READ, ZohoSearch.securesearch.READ`.
   No dar `modules.ALL` a un agente hasta confiar en su comportamiento.
3. **Workflow triggers → loops.** `create/update_record` pueden disparar workflows; como
   Unoavanza ya tiene webhooks en Railway, esto puede crear loops. Default `trigger: false`.
4. **Edición Professional.** MCP no cobra extra pero consume el API access de la edición;
   vigilar límites de llamadas/día compartidos con el resto de integraciones.

## MVP de esta semana

1. Confirmar región (URL del CRM: `crm.zoho.com` vs `.eu`/`.in`).
2. Crear un **Self Client** en `api-console.zoho.com` → `client_id`/`client_secret`.
3. En la consola de Zoho MCP, crear un server **scoped a CRM, read-only**.
4. Conectarlo a Claude Desktop / orquestador y correr 3 pruebas reales:
   contar leads del mes · buscar póliza de un cliente · listar campos del módulo de pólizas.
5. Documentar scopes + endpoint.

## Fuentes

- Zoho MCP (oficial): https://www.zoho.com/mcp/
- Zoho CRM MCP overview: https://www.zoho.com/crm/developer/docs/mcp/overview.html
- Pricing: https://www.zoho.com/mcp/pricing.html
- `junnaisystems/Zoho-CRM-MCP` (Python, CRUD): https://github.com/junnaisystems/Zoho-CRM-MCP
- `whiteside-daniel/zohocrm-mcpserver` (Node, read-only): https://github.com/whiteside-daniel/zohocrm-mcpserver
