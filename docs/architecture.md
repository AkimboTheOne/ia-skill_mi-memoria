# Arquitectura

`mi-memoria` es un runtime local independiente del vault Markdown.

El runtime contiene CLI, skills, workspace transitorio, harnesses, logs y memoria operacional interna del skill. El vault contiene conocimiento: notas, assets, templates, índices y memoria consolidada del proyecto.

## Regla central

El runtime opera sobre el vault, nunca dentro del vault. La escritura al vault requiere una operación explícita.

`remember` escribe por defecto memoria curada en `memory/` del vault configurado. La memoria del runtime solo se usa con `remember --scope runtime` para decisiones o convenciones que modulan el comportamiento del skill.

## Baseline v0.1

- Python estándar.
- CLI local.
- Workspace transitorio.
- Skill inicial `normalize`.
- Sin MCP funcional.
- Sin HTTPS.
- Sin APIs externas.
