# Conectar el MCP nativo de Zoho (read-write) a Claude · Unoavanza

> Meta: tener el servidor MCP oficial de Zoho con permisos de **crear + actualizar
> (sin borrar)** conectado tanto en **claude.ai** como en **Claude Code**.
> Org 910954312 · Zoho CRM Professional · data center `.com`.

## Resumen del flujo
1. Crear el servidor MCP `unoavanza-crm-rw` en la consola de Zoho (+ usuario/perfil sin borrado).  ← único cuello de botella (UI)
2. Conectarlo en **claude.ai** (Connectors).
3. Conectarlo en **Claude Code** (`claude mcp add`).

El candado de seguridad clave vive en **Zoho**: scope sin DELETE + usuario/perfil sin permiso de borrar. Autoriza el OAuth con ese usuario dedicado, **nunca con admin**.

---

## PARTE 1 — Crear el MCP rw en Zoho (consola)

### Opción B — Manual (≈10 min)
*(Las etiquetas exactas pueden variar según la versión de Zoho; busca por la sección indicada.)*

**A. Crear el perfil "Asistente CRM (sin borrado)"**
- Setup → Users and Control → Security Control → **Profiles** → clonar "Standard".
- Nombre: `Asistente CRM (sin borrado)`.
- En permisos por módulo (Contactos, Pólizas, Cobros, Siniestros): habilitar **Ver / Crear / Editar**, **DESACTIVAR Eliminar**.
- Quitar acceso a Setup/Admin.

**B. Crear el usuario dedicado**
- Setup → Users → **Add User**.
- Email: `automation@unoavanza.com` (o el que prefieras).
- Perfil: `Asistente CRM (sin borrado)`.

**C. Crear el servidor MCP**
- Setup → **Developer Space / Developer Hub** → busca **MCP** (o "MCP Servers").
- Crear servidor: nombre `unoavanza-crm-rw`.
- Scope: CRM con **READ + CREATE + UPDATE**. **NO** incluir DELETE.
- Data center: `.com`.
- Guardar y **copiar la URL del endpoint** + el transporte (http/sse).

### Opción A — Que lo haga Cowork (navegador)
Prompt para Cowork:
```
Eres Cowork operando el navegador sobre la consola de Zoho CRM de Unoavanza
(Org 910954312, plan Professional, data center .com). Español, confirmaciones en
tablas. NO modifiques usuarios, datos ni config existentes — solo CREA lo nuevo.
Antes de cualquier paso irreversible, muéstrame un resumen y espera mi OK.

Objetivo: habilitar escritura controlada (crear/actualizar, SIN borrar) vía el MCP
nativo de Zoho, para conectarlo a Claude.

Tareas:
1. Crear PERFIL "Asistente CRM (sin borrado)": Ver/Crear/Editar en Contactos,
   Pólizas, Cobros, Siniestros; DESACTIVAR Eliminar; sin acceso a Setup/Admin.
2. Crear USUARIO dedicado automation@unoavanza.com con ese perfil.
3. Crear servidor MCP "unoavanza-crm-rw": scope CRM con READ+CREATE+UPDATE,
   SIN DELETE, data center .com. Copiar la URL del endpoint y el transporte (http/sse).
4. Reportarme en tabla: perfil, usuario, scopes del MCP y la URL del endpoint.

No autorices OAuth con admin: usa el usuario del paso 2. Si algo se llama distinto
en esta versión de Zoho, descríbeme lo que ves y pregúntame antes de improvisar.
```

---

## PARTE 2 — Conectar en claude.ai
- Settings → **Connectors** → **Add custom connector**.
- Pegar la **URL del endpoint** de `unoavanza-crm-rw`.
- Completar **OAuth** iniciando sesión en Zoho con `automation@unoavanza.com`.
- Usarlo en chats vía *Search and tools* → `unoavanza-crm-rw`.

## PARTE 3 — Conectar en Claude Code (CLI)
```
claude mcp add --transport http unoavanza-crm-rw <URL_DEL_MCP_RW> -s user
```
- `-s user` → disponible en todos tus proyectos.
- Si es SSE: `--transport sse`.
- Primera vez: completa el **OAuth** con el usuario dedicado.
- Verifica con `claude mcp list`.

---

## Notas de seguridad
- El no-borrado se garantiza por **scope (sin DELETE) + perfil del usuario** → vale para claude.ai y Claude Code por igual.
- En Claude Code, además, cada tool call de escritura **pide tu aprobación** antes de ejecutarse (salvo que lo allowlistees).
- Deja el connector read-only (`unoavanza-crm-readonly`) como respaldo.
