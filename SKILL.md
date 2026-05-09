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
./bin/mi-memoria run normalize --input note.md --preview
./bin/mi-memoria validate --input note.md
./bin/mi-memoria remember --summary "..."
```

## Reglas

- Producir Markdown válido.
- Mantener frontmatter consistente.
- Evitar metadata innecesaria.
- Priorizar claridad sobre creatividad.
- No escribir al vault sin una operación explícita.
