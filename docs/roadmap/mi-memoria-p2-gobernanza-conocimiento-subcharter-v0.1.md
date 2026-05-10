# Sub-Charter P2 v0.1 — Gobernanza del Conocimiento de `mi-memoria`

## Metadata

| Campo | Valor |
|---|---|
| Proyecto | `mi-memoria` |
| Fase | P2 |
| Nombre | Gobernanza del Conocimiento |
| Estado | Propuesta para planificación Codex |
| Dependencias | P1 estabilizado |

---

# 1. Propósito

P2 introduce capacidades de gobernanza sobre el conocimiento ya capturado y consolidado.

Esta fase no busca hacer al sistema “más inteligente” en sentido amplio. Busca hacerlo más mantenible.

El objetivo es responder:

- ¿dónde está el conocimiento?;
- ¿qué está creciendo mal?;
- ¿qué está duplicado?;
- ¿qué está obsoleto?;
- ¿qué debe archivarse?;
- ¿qué índices ayudan a navegar mejor?

---

# 2. Features Incluidas

| ID | Feature | Propósito |
|---|---|---|
| F06 | `index` | Construcción de índices y mapas de contenido |
| F07 | `timeline` | Construcción histórica de decisiones e hitos |
| F08 | `drift-detection` | Detección de deriva semántica y taxonómica |
| F09 | `archive` | Archivado gobernado |
| F10 | `remember+` | Evolución de memoria reflexiva |

---

# 3. Feature F06 — `index`

## Responsabilidad

Generar índices navegables para carpetas, dominios o proyectos.

## Activación

```text
/mi-memoria index
```

## CLI Esperada

```bash
mi-memoria index --path 20-projects/mi-memoria
mi-memoria index --path 30-resources/ai --output indexes/ai.md
mi-memoria index --path 10-areas --json
```

## Runtime

Debe:

- listar notas fuente;
- preservar rutas relativas;
- generar links válidos;
- evitar duplicados;
- no reordenar archivos físicos.

## LLM

Puede:

- proponer agrupaciones;
- generar descripción de secciones;
- detectar temas principales;
- proponer MOCs.

## Salidas Esperadas

```text
index.md
map-of-content.md
index-report.json
```

---

# 4. Feature F07 — `timeline`

## Responsabilidad

Construir líneas de tiempo desde notas, decisiones, hitos o metadata.

## Activación

```text
/mi-memoria timeline
```

## CLI Esperada

```bash
mi-memoria timeline --path 20-projects/mi-memoria
mi-memoria timeline --from context/decisions
```

## Runtime

Debe:

- extraer fechas de frontmatter;
- ordenar eventos;
- preservar referencias a archivos fuente;
- marcar fechas inferidas como inferidas.

## LLM

Puede:

- redactar narrativa histórica;
- agrupar hitos;
- señalar vacíos temporales.

## Regla

No debe inventar fechas. Si una fecha no existe, debe marcarse como pendiente o inferida.

---

# 5. Feature F08 — `drift-detection`

## Responsabilidad

Detectar deriva de conocimiento, taxonomía y convenciones.

## Activación

```text
/mi-memoria drift-detection
```

## CLI Esperada

```bash
mi-memoria drift-detection --path .
mi-memoria drift-detection --path 30-resources --json
```

## Runtime

Debe detectar:

- tags duplicados;
- carpetas divergentes;
- nombres inconsistentes;
- frontmatter incompatible;
- notas huérfanas;
- links rotos;
- alias redundantes.

## LLM

Puede:

- detectar conceptos equivalentes;
- sugerir consolidación;
- explicar riesgos de deriva.

## Salida Esperada

```text
drift-report.md
drift-report.json
```

---

# 6. Feature F09 — `archive`

## Responsabilidad

Mover conocimiento a `40-archive/` bajo reglas explícitas y trazables.

## Activación

```text
/mi-memoria archive
```

## CLI Esperada

```bash
mi-memoria archive --input note.md --preview
mi-memoria archive --input note.md --apply
```

## Runtime

Debe:

- generar plan de archivo;
- validar destino;
- preservar links cuando sea posible;
- registrar operación;
- evitar borrado;
- evitar sobrescritura.

## LLM

Puede:

- justificar archivado;
- detectar si la nota aún parece activa;
- sugerir resumen previo al archivo.

## Regla

Archivar NO es borrar.

---

# 7. Feature F10 — `remember+`

## Responsabilidad

Evolucionar `remember` para registrar memoria reflexiva estructurada.

## Activación

```text
/mi-memoria remember
```

## CLI Esperada

```bash
mi-memoria remember --type decision --summary "..."
mi-memoria remember --type convention --input note.md
mi-memoria remember --type learning --preview
```

## Tipos Permitidos

```text
decision
convention
learning
constraint
taxonomy
```

## Runtime

Debe:

- persistir en ubicación correcta;
- validar tipo;
- exigir resumen;
- registrar fuente;
- evitar duplicados obvios.

## LLM

Puede:

- condensar;
- diferenciar decisión de aprendizaje;
- proponer título;
- proponer relaciones.

## Regla

La memoria debe ser curada. No se persisten conversaciones completas.

---

# 8. Entregables Codex

Codex debe generar plan para:

- comandos CLI nuevos;
- contratos de reports;
- estructuras de índices;
- esquemas de drift report;
- validaciones;
- tests;
- documentación de gobernanza.

---

# 9. Criterios de Aceptación P2

P2 se acepta cuando:

- `index` genera índices navegables;
- `timeline` no inventa fechas;
- `drift-detection` produce reportes accionables;
- `archive` mueve sin destruir;
- `remember+` persiste memoria curada;
- todos los comandos soportan preview;
- todos los reportes son trazables a archivos fuente.

---

# 10. Revisión de Consistencia

P2 es consistente porque:

- actúa sobre conocimiento ya consolidado;
- no introduce interoperabilidad;
- fortalece `$VAULT/context/`;
- mantiene memoria curada;
- evita automatización destructiva;
- mejora mantenibilidad antes de consulta contextual.
