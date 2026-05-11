# Changelog

## Unreleased (pre-p5-madurez)

- `template sync` agrega sincronización segura de plantillas CORE hacia `vault/templates` (solo faltantes, sin sobrescritura) con reportes `.md` + `.json`.
- `capabilities --json` incorpora metadata por comando orientada a carga rápida de contexto por LLM.
- Se introduce `docs/skill-manifest.json` como fuente canónica machine-first para capacidades y metadatos operacionales.
- Refactor modular inicial: extracción de metadata/capabilities (`cli/core/metadata.py`) y servicios de `template sync`/`upgrade` (`cli/services/*`) sin romper contratos CLI.
- Telemetría operacional liviana: se añade `logs/operations.jsonl` en paralelo al log textual existente para trazabilidad orientada a interpretación por LLM.
- Refactor por capa `commands`: `template sync`, `upgrade`, `capabilities` y el resto de subcomandos `template` delegan desde `cli/main.py` a handlers modulares manteniendo contratos JSON y retro-compatibilidad.
- Refactor por capa `commands` extendido: `context`, `explain`, `ask`, `run normalize` y `validate` también delegan a handlers modulares, manteniendo contratos operativos y pruebas existentes.
- Refactor contextual/calidad: `session`, `query`, `context-build`, `classify`, `review`, `link` y `summarize` delegan a módulos `commands` especializados con pruebas retro-compatibles en verde.
- Refactor productivo inicial: `capture`, `daily` y `decision` delegan en `cli/commands/production_commands.py` manteniendo contratos JSON y cobertura de pruebas existente.

## v0.4.1

- Hardening de madurez P4 previo a P5 (sin ejecutar interoperabilidad).
- `capture` agrega compatibilidad roadmap con `--kind` (`idea`, `reference`) y mapeo interno seguro a tipos canónicos.
- `decision` incorpora `decision_status` (`proposed`, `accepted`, `superseded`, `deprecated`) sin romper `status` operacional.
- `publish` agrega `--format markdown` y `--context-pack` para exportación acotada desde artefactos de contexto.
- Mensajes de comandos diagnósticos (`review`, `curate`, `drift-detection`) se estandarizan para distinguir ejecución correcta vs hallazgos de calidad.
- `capabilities --json` alinea `version=0.4.1`, mantiene `maturity=p4-stable` y expone `capture_kinds` y `decision_statuses`.
- Documentación y memoria histórica actualizadas con estado consolidado y gates de preparación P5.
- Doc-governance hardening: README incorpora activación por agente (`/mi-memoria`, `/mem`, `$mi-memoria`, `$mem`) y badges; AGENTS formaliza política de commit/sync/PR/tag/backport `release/vX.Y.Z`.

## v0.4.0

- Implementación P4 con nuevos comandos top-level: `daily`, `decision`, `curate`, `publish`.
- `capture` evoluciona con `--type` y `--to` para captura controlada en `workspace/*` o `vault/workspace/*`.
- `daily` crea/recupera notas diarias, permite `--append` con timestamp y `--summary` no destructivo.
- `decision` agrega ciclo `new`, `from-session` y `list` con plantilla CORE de decisiones trazables.
- `curate` genera plan de curaduría verificable (`.md` + `.json`) sin mutar notas fuente.
- `publish` exporta subconjuntos a `workspace/exports/*` con `README.md`, `manifest.json` y `files/`, con limpieza opcional de metadatos privados.
- `capabilities --json` alinea `version=0.4.0` y `maturity=p4-stable`.
- Cobertura de pruebas ampliada para contratos y restricciones críticas de P4.

## v0.3.0

- Implementación P3 con nuevos comandos top-level: `query`, `context-build`, `session`.
- `query` incorpora búsqueda local por nombre/título/tags/contenido y respuesta con `evidence`, `inference` y `uncertainty`.
- `context-build` genera paquetes de contexto acotados con artefactos `context-pack.md`, `context-pack.json` y `source-map.json`.
- `session` agrega ciclo transitorio `start/add/context/close` sin persistencia automática de memoria.
- `capabilities --json` incluye `maturity` operativa y alinea versión runtime a `0.3.0`.
- Se formaliza política de versionamiento y madurez en `AGENTS.md`.

## v0.1.0

- Baseline inicial del runtime local `mi-memoria`.
- CLI Python estándar.
- Skill `normalize`.
- Validación Markdown/Obsidian mínima.
- Workspace transitorio.
- Workspace curatorial visible dentro del vault para revisión en Obsidian.
- Temporales de prueba contenidos bajo `runtime/tmp/tests`.
- Alias corto de activación `/mem` para el runtime `mi-memoria`.
- Escritura controlada hacia vault externo.
- Memoria curada en vault por defecto; memoria local del runtime solo con `--scope runtime`.
- Setup inicial de vault.

## v0.1.1

- Expansión P1 del CLI con comandos top-level: `capture`, `classify`, `review`, `link`, `summarize`.
- `capture` guarda notas estructuradas en `workspace/inbox` (runtime o `vault/workspace/inbox` cuando hay vault configurado).
- `classify` propone destino (`00-inbox`, `10-areas`, `20-projects`, `30-resources`, `40-archive`) sin mover archivos.
- `classify` prioriza `type` del frontmatter; si infiere semánticamente, responde con `confidence=medium` y alternativas.
- `review` genera reportes verificables en `workspace/preview` (`*-review-report.md` y `*-review-report.json`).
- `link` entrega sugerencias de wikilinks sin persistencia automática.
- `summarize` genera síntesis trazable con lista de fuentes y salida en `workspace/preview` por defecto.
- `capabilities --json` actualizado para exponer capacidades P1 implementadas.
- Cobertura de pruebas ampliada en `tests/test_cli.py` para contratos y restricciones de P1.
- Documentación operativa actualizada en `README.md`, `SKILL.md` y `docs/usage.md`.

## v0.2.0

- Expansión P2 del CLI con comandos top-level: `index`, `timeline`, `drift-detection`, `archive`.
- `index` genera índice navegable en Markdown y contrato JSON con totales y títulos duplicados.
- `timeline` genera línea de tiempo trazable y marca eventos con fecha inferida (`inferred=true`) cuando aplica.
- `drift-detection` detecta deriva verificable (frontmatter, tags duplicados, links rotos, notas huérfanas, aliases redundantes) y emite reporte `.md` + `.json`.
- `archive` incorpora flujo gobernado con `--preview|--apply`, sin borrado ni sobrescritura.
- `remember` evoluciona a `remember+` con `--type` (`decision`, `convention`, `learning`, `constraint`, `taxonomy`) y soporte `--input` como fuente curada.
- `capabilities --json` actualizado con comandos P2 implementados.
- Cobertura de pruebas ampliada en `tests/test_cli.py` para casos exitosos y restricciones críticas de P2.
