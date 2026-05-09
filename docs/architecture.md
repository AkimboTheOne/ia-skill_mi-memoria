# Arquitectura

`mi-memoria` es un runtime local independiente del vault Markdown.

El runtime contiene CLI, skills, workspace transitorio, harnesses, logs y memoria operacional. El vault contiene conocimiento: notas, assets, templates, índices, memoria consolidada y un workspace curatorial visible desde Obsidian.

## Regla central

El runtime opera sobre el vault, nunca dentro del vault. La escritura final al vault requiere `--write` o `apply`.

## Workspaces

- `runtime/workspace`: staging técnico local para inbox, processing, preview y exports cuando no hay vault explícito.
- `runtime/tmp`: temporales efímeros controlados por el runtime y sus pruebas.
- `vault/workspace`: staging curatorial visible desde Obsidian para revisar, editar puntualmente y decidir reubicación.
- `vault/workspace` no debe contener scripts, logs, dependencias, temporales técnicos ni lógica agentic.

## Baseline v0.1

- Python estándar.
- CLI local.
- Workspace transitorio.
- Workspace visible del vault para curaduría.
- Skill inicial `normalize`.
- Sin MCP funcional.
- Sin HTTPS.
- Sin APIs externas.
