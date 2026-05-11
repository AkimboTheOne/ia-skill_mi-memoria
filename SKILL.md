---
name: mi-memoria
description: Use this runtime when the user wants to organize, normalize, validate, index, build timelines, detect drift, archive with explicit controls, remember, or apply curated Markdown knowledge for an external Obsidian vault, with explicit preview/write boundaries.
---

# mi-memoria

## Activación

Usa este runtime cuando el usuario quiera organizar, normalizar, validar o recordar conocimiento Markdown para un vault Obsidian externo.

Contextualización para agentes (obligatoria):
- Primero cargar `skill-manifest.json` en la raíz para entender comandos, contratos y metadata (`command_metadata`) sin explorar el código.
- Usar `docs/skill-manifest.json` solo como fallback de compatibilidad si el canónico no está disponible.
- Recurrir a lectura de módulos Python solo cuando el manifiesto no alcance para resolver la tarea.

Activaciones naturales:

- "Organiza esta nota."
- "Convierte esta idea en una nota estructurada."
- "Clasifica este Markdown."
- "Normaliza esta nota."
- "Guarda esta decisión como memoria."

Alias de activación:

- `/mi-memoria`
- `/mem`

### Activación en `prompt`

Usa este formato cuando el usuario esté en un agente conversacional o coding CLI que cargue el skill.

```prompt
/mi-memoria capture "Idea rápida"
/mem review --path workspace/inbox
$mi-memoria summarize --path workspace/inbox
$mem context-build --topic "arquitectura local"
```

```prompt
Organiza esta nota.
Normaliza esta idea sobre arquitectura.
Clasifica este Markdown.
Guarda esta decisión como memoria.
```

### Comandos técnicos en `bash`

Usa este formato para el contrato técnico ejecutable y verificable.

```bash
./bin/mi-memoria capabilities --json
./bin/mi-memoria capture --kind idea --text "Idea rápida"
./bin/mi-memoria daily --append "Nota rápida" --json
./bin/mi-memoria decision new --title "Separar runtime y vault" --decision-status accepted --json
./bin/mi-memoria classify --input workspace/inbox/2026-05-10-idea.md --json
./bin/mi-memoria review --path workspace/inbox --json
./bin/mi-memoria link --input workspace/inbox/2026-05-10-idea.md --preview --json
./bin/mi-memoria summarize --path workspace/inbox --json
./bin/mi-memoria index --path workspace/inbox --json
./bin/mi-memoria timeline --path workspace/inbox --json
./bin/mi-memoria drift-detection --path workspace/inbox --json
./bin/mi-memoria curate --path workspace/inbox --json
./bin/mi-memoria publish --path workspace/inbox --output workspace/exports/pack --format markdown --json
./bin/mi-memoria ask "Normaliza esta nota sobre arquitectura"
./bin/mi-memoria run normalize --input note.md --preview
./bin/mi-memoria run normalize --input note.md --preview --vault-path /path/to/vault
./bin/mi-memoria validate --input note.md
./bin/mi-memoria template list --json
./bin/mi-memoria template generate --name log-diario --type note --description "Registro diario de eventos" --preview
./bin/mi-memoria template sync --vault-path /path/to/vault --json
./bin/mi-memoria apply --input workspace/preview/note.md --vault-path /path/to/vault
./bin/mi-memoria remember --summary "..." --vault-path /path/to/vault
./bin/mi-memoria remember --type decision --summary "..." --vault-path /path/to/vault
./bin/mi-memoria archive --input 30-resources/2026-05-10-nota.md --preview --vault-path /path/to/vault
./bin/mi-memoria context --json
./bin/mi-memoria upgrade --json
```

## Capacidades actuales

- `capture`: capturar ideas/notas rápidas en `workspace/inbox` con `--kind`/`--type`.
- `daily`: crear y mantener notas diarias minimalistas.
- `decision`: registrar decisiones trazables con plantilla estructurada y `decision_status`.
- `classify`: proponer destino taxonómico sin mover automáticamente.
- `review`: revisar calidad estructural y emitir reportes verificables.
- `link`: sugerir wikilinks sin persistir enlaces automáticamente.
- `summarize`: sintetizar nota/carpeta con fuentes trazables.
- `normalize`: producir notas Markdown con frontmatter y secciones estándar.
- `validate`: verificar estructura mínima de notas.
- `remember`: guardar memoria curada, explícita y resumida en el vault por defecto.
- `index`: construir índices navegables con reporte de duplicados.
- `timeline`: construir historial temporal trazable.
- `drift-detection`: detectar deriva estructural/taxonómica con reportes.
- `curate`: producir planes de curaduría sin mutación automática.
- `publish`: exportar subconjuntos de conocimiento sin modificar fuentes; soporta `--format markdown` y `--context-pack`.
- `archive`: archivar en `40-archive` mediante `preview/apply` explícito.
- `query`: consulta contextual local con evidencia trazable.
- `context-build`: construir paquetes de contexto reutilizables y acotados.
- `session`: gestionar sesiones temporales de trabajo con cierre controlado.
- `template`: listar, revisar, generar, validar y aplicar plantillas Markdown.
- `apply`: copiar previews válidos desde el workspace del runtime o del vault hacia un destino final.
- `ask`: activar normalización simple desde lenguaje natural; usa `vault/workspace/preview` si hay vault configurado.
- `context`: mostrar contexto operacional del runtime y workspace visible del vault cuando exista.
- `capabilities`: exponer el contrato operativo actual del CLI.
- `capabilities`: exponer también versión y madurez operativa.
- `capabilities`: exponer metadata por comando para carga rápida de agentes (fuente canónica: `skill-manifest.json` en raíz; espejo compatible: `docs/skill-manifest.json`).
- `upgrade`: actualizar el runtime del skill con `git pull --ff-only` acotado a este repo.

## Documentación de usuario

La documentación curada para usuarios vive en el vault del proyecto, dentro de `docs/30-resources/mi-memoria/`.

- [Hub de documentación de usuario](docs/30-resources/mi-memoria/index.md)
- [Gobernanza documental](docs/documentation-governance.md)
- [Memoria curada del vault](docs/memory/README.md)
- [Taxonomía documental](docs/memory/conventions/documentation-taxonomy.md)
- [Estilo editorial](docs/memory/conventions/editorial-style.md)

## Capacidades planeadas

La revisión documental y alineación contra master-plan es una capacidad propuesta, no implementada en v0.1.

Activaciones como `/mi-memoria review-docs`, `/mem review-docs`, `/mi-memoria align-readme`, `/mem align-readme`, `/mi-memoria review-master-plan` o `/mem review-master-plan` deben tratarse como roadmap hasta que existan en el CLI, estén documentadas como actuales y tengan pruebas.

P5 (MCP/HTTPS/proveedores externos) permanece como roadmap. No debe anunciarse como implementada mientras no existan comandos y pruebas explícitas.

La gobernanza de release/tag/backport para consumo por integraciones está definida en `AGENTS.md` y debe respetarse en toda entrega de versión.

## Reglas

- Producir Markdown válido.
- Mantener frontmatter consistente.
- Priorizar plantillas del vault y usar plantillas CORE solo como fallback con warning.
- Evitar metadata innecesaria.
- Priorizar claridad sobre creatividad.
- No escribir al vault sin una operación explícita.
- Usar `remember --scope runtime` solo para memoria operacional del skill.
- Usar `vault/workspace/preview` como staging visible cuando se indique un vault; no guardar ahí lógica operacional.
- Usar `remember --scope runtime` solo para memoria operacional del skill.
- No presentar capacidades planeadas como disponibles.
- No usar `upgrade` para escribir en el vault ni ejecutar comandos arbitrarios.

## Flujo recomendado P1

Flujo operativo por defecto:

1. `capture` para ingresar ideas en `workspace/inbox`.
2. `classify` para proponer destino (`00/10/20/30/40`) sin mover.
3. `review` para validar estructura y calidad antes de consolidar.
4. `link` para sugerir relaciones internas no persistentes.
5. `summarize` para síntesis trazable.
6. `run normalize --preview` para estandarizar nota.
7. `apply` o `run normalize --write` solo con intención explícita.

Reglas de decisión:

- Si hay ambigüedad material en clasificación, preferir alternativas explícitas.
- Si no hay vault configurado, operar en `runtime/workspace/*`.
- Si hay vault configurado, usar `vault/workspace/*` para staging visible.
- No persistir cambios semánticos automáticos en el vault final sin `apply`/`--write`.
