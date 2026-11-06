# Brief para la sesión "Verificar token Railway y health" — casos de ingesta → asistente

Fecha: 2026-11-06 · Repo: `MrJoseRB/unoavanza-zoho-crm` · Origen: sesión "Zoho CRM automations and custom views"

## Contexto (verificado hoy, no re-investigar)

**Gerente vs ejecutivo:** el gerente que decide en `/admin` es **Luis Martínez** (lmmh72@gmail.com,
Administrator). **Luis Manuel Dicurú** (backevseguros@gmail.com) es el ejecutivo de Emisión.

**Agente de ingesta (IDEA-003):** corre en el **MacBook Pro**, repo `~/zoho_crm_project`. Launchd
`com.zoho.crm.ingesta.venezuela` cargado, modo APPLY, `ultimo_ok` = 2026-11-05 21:37 UTC, túnel HTTP 200.
La skill `venezuela-ingesta-operacion` y el acta dicen "iMac" → **documentación desactualizada**.

**Conciliación del reporte de Luis Manuel (WhatsApp 04/11) contra Zoho:**

| Cliente (carpeta) | Tomador en Zoho | Reportado | En Zoho | Estado |
|---|---|---|---|---|
| Sumiservices Capito (19–28/10) | SUMISERVICES CAPITO | 7 | 7 | OK |
| Grupo Oficial Bestune (29/10–03/11) | GRUPO ECOSTA | 18 | 15 | 3 en pendientes `contacto_no_creado` |
| Centro empresarial 3R (30/10–02/11) | CENTRO EMPRESARIAL | 2 | 2 | OK |
| Importadora NATO (27/10–03/11) | KENJICARS IMPORTADORA (?) | 6 | 5 en ventana | Confirmar si KENJICARS = NATO o tomador mal asignado |

**Problemas de calidad de datos detectados:**
- Contactos de empresa duplicados (un contacto por póliza): SUMISERVICES CAPITO ×7, CARS LUNA ×4.
- Nombres de tomador truncados: "CENTRO EMPRESARIAL" (debería ser "…3R, C.A"), "ALCOHOLES Y".
- Pólizas que parecen de prueba (21–26/10): 64-56-20000, 64-56-2000000, 64-56-200001, 64-56-200005,
  64-56-50000, 64-56-10000 (MIGUEL RODRIGUEZ / sin tomador).
- Pólizas creadas por la ingesta sin `Freecuencia_de_Pago` → sus cobros no calculan `Cuota_esperada_USD`.

**Estado del asistente (según el handoff y el código):**
- "Mis casos" (`asistente/casos.py`) lee una planilla fija `asistente/data/casos_revision.csv`
  (32 casos, último cambio 2026-08-03). Los pendientes nuevos de la ingesta NO llegan.
- Bandeja de revisión de gerencia (PR #6) y Sugerencias → reglas (PR #7) operativas.

**Cola de pendientes de la ingesta (foto del repo, ago):** ~1.790 → `cobro_sin_poliza_unica` 604,
`carpeta_no_estandar` 542, `pdf_sin_texto_extraible` 387, `sin_numero_poliza` 134, resto ~120.
La cola en vivo (MacBook) seguramente es mayor.

## Lo que se pide (en este orden)

### A. Ya — cargar los casos actuales al asistente (sin código nuevo)
1. Regenerar la planilla con `scripts/casos_ejecutivos_v3.py` + `scripts/enriquecer_casos_ejecutivos.py`
   a partir de la cola **en vivo** del MacBook (`~/zoho_crm_project/.claude/tasks/evidence/ingesta_pendientes.csv`).
2. Mismo filtro que hoy: clientes con póliza Activa, períodos 2025–2027. Incluir sí o sí los recientes
   (Bestune `contacto_no_creado`, comprobantes de NATO y 3R, cobro sin póliza única, anulación sin número)
   y el caso "¿KENJICARS = Importadora NATO?" para Luis Manuel.
3. `carpeta_no_estandar` (542, carpetas "Banesco Seguros" e "Individuales") **no** como 542 casos:
   una sola tarjeta de decisión para Luis Martínez.
4. Asignación por tipo: emisiones → Luis Manuel, cobros/renovaciones → Francys, siniestros → Rosa.

### B. Después — puente automático pendientes → asistente
- La ingesta envía cada pendiente nuevo al asistente (endpoint autenticado en Railway, guardado en `/data`)
  en vez de una planilla commiteada. `casos.py` lee de ese almacén.
- Cada caso con su `que_hacer` y las pólizas del cliente como contexto. Al resolverse, la ingesta lo marca
  `resuelto` y no lo repite.
- La cadena ejecutivo → bandeja de Luis → aplicar en Zoho → audit log ya existe; no duplicarla.

### C. Después — "propuestas del sistema" en la bandeja de gerencia
- Que la bandeja acepte propuestas generadas por un script de limpieza (no solo cambios de ejecutivos):
  fusionar contactos duplicados, corregir nombres truncados, completar frecuencia de pago, revisar o
  eliminar las pólizas de prueba. Los borrados por el flujo existente (aprobación de un segundo gerente + respaldo).

### D. Backlog
- Mover la ingesta a Railway (hoy depende de que el MacBook esté encendido).
- OCR para comprobantes escaneados y emparejamiento de cobros por mes/monto (v2 del agente).
- Corregir la skill `venezuela-ingesta-operacion` y el acta IDEA-003: MacBook Pro, `~/zoho_crm_project`.

## Reglas
- Karpathy: Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven (verificación obligatoria).
- Dry-run primero. No push a main. No unir PRs sin OK de José (auto-deploy). `DRY_RUN=true` para ejecutivos se mantiene.
- Fuente de verdad primero: repo → Notion → CRM antes de preguntar a José.
- Español, respuestas en tablas.

## Primer paso
Antes de tocar nada: tabla con cada punto (A–D), qué archivos toca, esfuerzo estimado y riesgos. Esperar OK de José.
