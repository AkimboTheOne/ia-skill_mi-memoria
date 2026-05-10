# Memoria de Conversación — Racional de Evolución de `mi-memoria`

## Metadata

| Campo | Valor |
|---|---|
| Proyecto | `mi-memoria` |
| Documento | Memoria de racional de evolución |
| Fecha | 2026-05-08 |
| Estado | Memoria curada |
| Uso esperado | Incorporación a `$VAULT/context/` o memoria histórica del proyecto |

---

# 1. Contexto

Después de definir la baseline v0.1 de `mi-memoria`, se discutió cómo extender el runtime sin caer en sobreingeniería.

La conversación partió de una pregunta clave:

> ¿Los métodos como `capture`, `classify`, `summarize`, etc. se soportan en el LLM para extender ideas?

La respuesta arquitectónica consolidada fue:

> Sí, pero el LLM asiste; no gobierna.

---

# 2. Principio Central Aprobado

Se aprobó el modelo:

```text
Human-governed
Runtime-controlled
LLM-assisted
```

---

## Interpretación

| Capa | Rol |
|---|---|
| Humano | Decide y aprueba |
| Runtime | Controla estructura, persistencia, rutas, validaciones y seguridad |
| LLM | Expande, resume, clasifica, sugiere y razona semánticamente |

---

# 3. Decisión sobre el LLM

El LLM debe poder:

- extender ideas capturadas;
- proponer títulos;
- inferir tags;
- sugerir relaciones;
- resumir carpetas;
- detectar ambigüedad;
- proponer memoria curada.

El LLM NO debe:

- mover archivos sin confirmación;
- reestructurar taxonomías por sí solo;
- archivar conocimiento automáticamente;
- persistir memoria sin curación;
- crear relaciones permanentes sin validación;
- decidir la gobernanza del vault.

---

# 4. Racional de Fases

Se decidió organizar la evolución en cinco fases progresivas.

## P1 — Consolidación Operacional

Primero se debe fortalecer el ciclo básico de trabajo:

```text
capturar → clasificar → revisar → enlazar → resumir
```

Motivo:

- mejora uso cotidiano;
- no introduce infraestructura;
- reduce deuda temprana;
- fortalece el workspace.

---

## P2 — Gobernanza del Conocimiento

Después se debe gobernar el vault:

- índices;
- timelines;
- deriva;
- archivado;
- memoria reflexiva avanzada.

Motivo:

- el conocimiento crece;
- sin gobernanza aparece desorden;
- conviene detectar deriva antes de agregar inteligencia contextual.

---

## P3 — Inteligencia Contextual Local

Luego se debe permitir:

- consultas locales;
- paquetes de contexto;
- sesiones temporales.

Motivo:

- el vault ya tiene estructura;
- las respuestas deben tener evidencia;
- los context packs serán útiles para Codex y otros agentes.

---

## P4 — Flujos Productivos de Conocimiento

Después se formalizan workflows cotidianos:

- captura avanzada;
- notas diarias;
- decisiones;
- curaduría;
- publicación.

Motivo:

- estas funciones tienen mucho valor práctico;
- requieren una base previa de validación, clasificación y contexto;
- no deben aparecer antes de que existan reglas de gobernanza.

---

## P5 — Interoperabilidad Controlada

La interoperabilidad queda al final:

- MCP;
- HTTPS;
- proveedores externos.

Motivo:

- exponer capacidades inmaduras consolida deuda;
- aumenta superficie de riesgo;
- puede romper el principio CLI-first;
- requiere contratos claros y capacidades maduras.

---

# 5. Decisión sobre Interoperabilidad

Se decidió dejar interoperabilidad al final.

La razón principal:

> interoperar temprano equivale a publicar contratos antes de saber si son correctos.

La CLI sigue siendo el contrato operacional primario.

MCP, HTTPS y servicios externos son extensiones futuras, no el núcleo.

---

# 6. Decisión sobre Features 16–20

Las features identificadas como especialmente útiles:

- `capture`;
- `daily`;
- `decision`;
- `curate`;
- `publish`;

fueron agrupadas en P4 como flujos productivos.

Motivo:

- aportan valor cotidiano;
- necesitan reglas previas;
- podrían causar desorden si se implementan demasiado temprano.

---

# 7. Relación con `$VAULT/context/`

Se aclaró que `$VAULT/context/` no es una carpeta de notas comunes.

Debe guardar:

- metaconocimiento;
- decisiones;
- principios;
- resúmenes consolidados;
- convenciones;
- contexto humano persistente.

El conocimiento real vive en:

```text
00-inbox/
10-areas/
20-projects/
30-resources/
40-archive/
```

---

# 8. Riesgos Identificados

| Riesgo | Mitigación |
|---|---|
| LLM gobernando rutas | Runtime controla persistencia |
| Memoria basura | Curación reflexiva |
| Interoperabilidad prematura | P5 diferida |
| Sobrediseño | Fases progresivas |
| Cambios destructivos | Preview y apply explícito |
| Contexto sin evidencia | Trazabilidad a fuentes |

---

# 9. Resultado

Se generó un set de documentos para Codex:

```text
mi-memoria-evolution-master-plan-v0.1.md
mi-memoria-p1-consolidacion-operacional-subcharter-v0.1.md
mi-memoria-p2-gobernanza-conocimiento-subcharter-v0.1.md
mi-memoria-p3-inteligencia-contextual-subcharter-v0.1.md
mi-memoria-p4-flujos-productivos-subcharter-v0.1.md
mi-memoria-p5-interoperabilidad-controlada-subcharter-v0.1.md
```

La estructura permite pedir a Codex planes de implementación por fase sin perder el racional arquitectónico.
