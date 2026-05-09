# Arquitectura

`mi-memoria` es un runtime local independiente del vault Markdown.

El runtime contiene CLI, skills, workspace transitorio, harnesses, logs y memoria operacional. El vault contiene conocimiento: notas, assets, templates, índices y memoria consolidada.

## Regla central

El runtime opera sobre el vault, nunca dentro del vault. La escritura al vault requiere una operación explícita.

## Baseline v0.1

- Python estándar.
- CLI local.
- Workspace transitorio.
- Skill inicial `normalize`.
- Sin MCP funcional.
- Sin HTTPS.
- Sin APIs externas.
