# Arquitectura

`mi-memoria` es un runtime local independiente del vault Markdown.

El runtime contiene CLI, skills, workspace transitorio, harnesses, logs y memoria operacional interna del skill. El vault contiene conocimiento: notas, assets, templates, índices, memoria consolidada del proyecto y un workspace curatorial visible desde Obsidian.

La telemetría operacional del runtime mantiene dos salidas livianas:
- `logs/operations.log` (texto legible)
- `logs/operations.jsonl` (eventos estructurados con mensaje natural simplificado para agentes/LLM)

## Regla central

El runtime opera sobre el vault, nunca dentro del vault. La escritura final al vault requiere `--write` o `apply`.

## Workspaces

- `runtime/workspace`: staging técnico local para inbox, processing, preview y exports cuando no hay vault explícito.
- `runtime/tmp`: temporales efímeros controlados por el runtime y sus pruebas.
- `vault/workspace`: staging curatorial visible desde Obsidian para revisar, editar puntualmente y decidir reubicación.
- `vault/workspace` no debe contener scripts, logs, dependencias, temporales técnicos ni lógica agentic.

`remember` escribe por defecto memoria curada en `memory/` del vault configurado. La memoria del runtime solo se usa con `remember --scope runtime` para decisiones o convenciones que modulan el comportamiento del skill.

`note` es el tipo primitivo del CORE. Las plantillas CORE viven en `skills/core/templates` y actúan como fallback cuando falta la plantilla correspondiente en `vault/templates`. Las plantillas del usuario en el vault siempre tienen prioridad.

## Estructura modular actual

- `cli/main.py`: entrypoint CLI, parser top-level y wiring de handlers.
- `cli/commands/`: handlers por dominio de comando (`analytics`, `contextual`, `normalize`, `production`, `quality`, `runtime`, `safeguard`, `template`, `upgrade`, `capabilities`).
- `cli/core/`: reglas y contratos transversales (`metadata`, `paths`) reutilizables por comandos.
- `cli/services/`: lógica reutilizable de caso de uso (`upgrade_service`, `template_sync`) desacoplada del parser.
- `cli/infra/`: integración con runtime local (`git_tools`, `telemetry`).

La metadata machine-first para agentes/LLM se mantiene de forma canónica en `skill-manifest.json` (raíz), con espejo transitorio en `docs/skill-manifest.json`, y se valida contra `capabilities --json` mediante pruebas automáticas.

## Baseline v0.1

- Python estándar.
- CLI local.
- Workspace transitorio.
- Workspace visible del vault para curaduría.
- Skill inicial `normalize`.
- Sin MCP funcional.
- Sin HTTPS.
- Sin APIs externas.
