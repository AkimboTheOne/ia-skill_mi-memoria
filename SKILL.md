---
name: mi-memoria
description: Use this runtime when the user wants to organize, normalize, validate, remember, or apply curated Markdown knowledge for an external Obsidian vault, with explicit preview/write boundaries.
---

# mi-memoria

## Activación

Usa este runtime cuando el usuario quiera organizar, normalizar, validar o recordar conocimiento Markdown para un vault Obsidian externo.

Activaciones naturales:

- "Organiza esta nota."
- "Convierte esta idea en una nota estructurada."
- "Clasifica este Markdown."
- "Normaliza esta nota."
- "Guarda esta decisión como memoria."

Activación CLI:

```bash
./bin/mi-memoria capabilities --json
./bin/mi-memoria ask "Normaliza esta nota sobre arquitectura"
./bin/mi-memoria run normalize --input note.md --preview
./bin/mi-memoria validate --input note.md
./bin/mi-memoria apply --input workspace/preview/note.md --vault-path /path/to/vault
./bin/mi-memoria remember --summary "..." --vault-path /path/to/vault
./bin/mi-memoria context --json
```

## Capacidades actuales

- `normalize`: producir notas Markdown con frontmatter y secciones estándar.
- `validate`: verificar estructura mínima de notas.
- `remember`: guardar memoria curada, explícita y resumida en el vault por defecto.
- `apply`: copiar previews válidos hacia un vault externo.
- `ask`: activar normalización simple desde lenguaje natural.
- `context`: mostrar contexto operacional del runtime.
- `capabilities`: exponer el contrato operativo actual del CLI.

## Capacidades planeadas

La revisión documental y alineación contra master-plan es una capacidad propuesta, no implementada en v0.1.

Activaciones como `/mi-memoria review-docs`, `/mi-memoria align-readme` o `/mi-memoria review-master-plan` deben tratarse como roadmap hasta que existan en el CLI, estén documentadas como actuales y tengan pruebas.

## Reglas

- Producir Markdown válido.
- Mantener frontmatter consistente.
- Evitar metadata innecesaria.
- Priorizar claridad sobre creatividad.
- No escribir al vault sin una operación explícita.
- Usar `remember --scope runtime` solo para memoria operacional del skill.
- No presentar capacidades planeadas como disponibles.
