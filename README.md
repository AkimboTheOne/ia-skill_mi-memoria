# mi-memoria

Runtime local de skills para operar sobre repositorios de conocimiento Markdown, separado del vault de conocimiento.

`mi-memoria` v0.1 implementa una baseline mínima:

- CLI local sin dependencias externas obligatorias.
- Skill `normalize` para convertir texto o Markdown libre en notas Obsidian consistentes.
- Validación de estructura, frontmatter, nombres y secciones mínimas.
- Workspace transitorio con preview seguro.
- Escritura controlada hacia un vault externo.
- Memoria operacional curada mediante `remember`.
- Setup inicial de vault mediante `scripts/skill_setup.sh`.

## Uso rápido

```bash
./bin/mi-memoria capabilities --json
./bin/mi-memoria run normalize --input note.md --preview
./bin/mi-memoria validate --input workspace/preview/2026-05-08-nota.md
./bin/mi-memoria apply --input workspace/preview/2026-05-08-nota.md --vault-path /path/to/mi-memoria-vault
./bin/mi-memoria remember --summary "Se adopta Python estándar para v0.1."
```

También puede configurarse el vault por entorno:

```bash
export MI_MEMORIA_VAULT_PATH=/path/to/mi-memoria-vault
```

## Inicializar un vault

```bash
./scripts/skill_setup.sh /path/to/mi-memoria-vault
```

El script crea la estructura mínima sin sobrescribir archivos existentes.

## Pruebas

```bash
make test
```

La implementación usa solo librería estándar de Python.
