# Sub-Charter P1 v0.1 — Consolidación Operacional de `mi-memoria`

## Metadata

| Campo | Valor |
|---|---|
| Proyecto | `mi-memoria` |
| Fase | P1 |
| Nombre | Consolidación Operacional |
| Estado | Propuesta para planificación Codex |
| Baseline requerida | v0.1 |
| Dependencias | `normalize`, `workspace`, `apply`, `remember` básico |

---

# 1. Propósito

P1 busca convertir la baseline inicial en un runtime útil para trabajo cotidiano.

El objetivo no es ampliar infraestructura, sino fortalecer el ciclo básico:

```text
capturar → clasificar → revisar → enlazar → resumir → consolidar
```

Esta fase debe mejorar la calidad del conocimiento sin introducir dependencias externas, MCP, HTTPS, RAG o vector DB.

---

# 2. Features Incluidas

| ID | Feature | Propósito |
|---|---|---|
| F01 | `capture` | Captura rápida de ideas o notas sueltas |
| F02 | `classify` | Clasificación semántica y taxonómica inicial |
| F03 | `review` | Revisión de calidad del vault/workspace |
| F04 | `link` | Sugerencia de wikilinks y relaciones |
| F05 | `summarize` | Síntesis de notas o carpetas |

---

# 3. Feature F01 — `capture`

## Responsabilidad

Capturar contenido rápido desde lenguaje natural, texto plano o archivo, y ubicarlo inicialmente en `workspace/inbox/`.

## Activación

```text
/mi-memoria capture "idea rápida"
/mi-memoria capture --input idea.md
```

## CLI Esperada

```bash
mi-memoria capture --text "idea rápida"
mi-memoria capture --input idea.md
mi-memoria capture --text "..." --json
```

## Runtime

Debe:

- crear archivo en `workspace/inbox/`;
- asignar timestamp;
- generar nombre temporal estable;
- registrar operación;
- no mover al vault automáticamente.

## LLM

Puede:

- expandir la idea;
- proponer título;
- proponer resumen;
- proponer tags;
- formular preguntas pendientes.

## Salida Esperada

```text
workspace/inbox/yyyy-mm-dd-slug.md
```

---

# 4. Feature F02 — `classify`

## Responsabilidad

Clasificar notas del workspace o vault bajo la macro-taxonomía:

```text
00-inbox/
10-areas/
20-projects/
30-resources/
40-archive/
```

## Activación

```text
/mi-memoria classify
```

## CLI Esperada

```bash
mi-memoria classify --input workspace/inbox/note.md
mi-memoria classify --input note.md --json
```

## Runtime

Debe:

- validar que el archivo existe;
- leer frontmatter;
- proponer destino;
- no mover sin `apply`;
- explicar la razón de clasificación.

## LLM

Puede:

- inferir categoría;
- sugerir subdirectorios;
- proponer tags;
- detectar ambigüedad.

## Regla

Cuando exista ambigüedad material, debe producir alternativas, no decidir unilateralmente.

---

# 5. Feature F03 — `review`

## Responsabilidad

Revisar calidad estructural y documental de notas.

## Activación

```text
/mi-memoria review
```

## CLI Esperada

```bash
mi-memoria review --input workspace/processing/note.md
mi-memoria review --path 20-projects/mi-memoria --json
```

## Runtime

Debe revisar:

- frontmatter;
- headings;
- links;
- tags;
- filename;
- ubicación;
- estado;
- campos requeridos.

## LLM

Puede:

- detectar incoherencias semánticas;
- señalar contenido débil;
- sugerir mejoras de claridad.

## Salida Esperada

```text
review-report.md
review-report.json
```

---

# 6. Feature F04 — `link`

## Responsabilidad

Sugerir relaciones internas entre notas usando heurística local y asistencia LLM.

## Activación

```text
/mi-memoria link
```

## CLI Esperada

```bash
mi-memoria link --input note.md
mi-memoria link --input note.md --preview
```

## Runtime

Debe:

- escanear nombres de notas;
- escanear títulos;
- escanear aliases;
- validar formato wikilink;
- no insertar enlaces sin confirmación.

## LLM

Puede:

- sugerir relaciones conceptuales;
- detectar conceptos relacionados;
- explicar por qué un enlace sería útil.

## Restricción

No debe crear enlaces persistentes automáticamente si no existe nota destino o si la relación es especulativa.

---

# 7. Feature F05 — `summarize`

## Responsabilidad

Generar síntesis de una nota, carpeta o conjunto de archivos.

## Activación

```text
/mi-memoria summarize
```

## CLI Esperada

```bash
mi-memoria summarize --input note.md
mi-memoria summarize --path 20-projects/mi-memoria
mi-memoria summarize --path 30-resources/ai --output workspace/preview/summary.md
```

## Runtime

Debe:

- controlar alcance;
- enumerar archivos fuente;
- generar reporte trazable;
- evitar mezclar carpetas no solicitadas.

## LLM

Puede:

- sintetizar;
- extraer decisiones;
- detectar temas;
- proponer pendientes.

---

# 8. Entregables Codex

Codex debe producir un plan de implementación que incluya:

- cambios de estructura;
- comandos CLI;
- contratos de entrada/salida;
- pruebas mínimas;
- ejemplos;
- criterios de aceptación;
- documentación a actualizar.

---

# 9. Criterios de Aceptación P1

P1 se acepta cuando:

- `capture` crea archivos en `workspace/inbox/`;
- `classify` propone destino sin mover automáticamente;
- `review` produce reportes verificables;
- `link` sugiere wikilinks sin persistirlos sin aprobación;
- `summarize` genera síntesis trazable;
- todos los comandos tienen salida humana y JSON;
- se mantiene compatibilidad con `normalize`;
- no se requieren servicios externos.

---

# 10. Revisión de Consistencia

P1 es consistente con el charter base porque:

- refuerza el workspace;
- no modifica directamente el vault sin `apply`;
- mantiene al LLM como asistente;
- no introduce interoperabilidad;
- no usa secretos;
- mejora calidad y trazabilidad;
- reduce riesgo operativo antes de fases más avanzadas.
