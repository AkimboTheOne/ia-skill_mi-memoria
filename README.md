# mi-memoria

Runtime local de skills para operar sobre repositorios de conocimiento Markdown, separado del vault de conocimiento.

`mi-memoria` v0.1 implementa una baseline mínima:

- CLI local sin dependencias externas obligatorias.
- Skill `normalize` para convertir texto o Markdown libre en notas Obsidian consistentes.
- Validación de estructura, frontmatter, nombres y secciones mínimas.
- Workspace técnico del runtime y workspace curatorial visible dentro del vault.
- Escritura controlada hacia un vault externo.
- Memoria operacional curada mediante `remember`.
- Setup inicial de vault mediante `scripts/skill_setup.sh`.

## Capacidades actuales v0.1

La fuente operativa para capacidades actuales es:

```bash
./bin/mi-memoria capabilities --json
```

En conversaciones con Codex, `/mem` es alias corto de `/mi-memoria`. El binario local se mantiene como `mi-memoria`.

En v0.1 el runtime expone:

- `normalize`: normaliza Markdown libre hacia una nota Obsidian consistente.
- `validate`: valida frontmatter, secciones mínimas y nombre de archivo.
- `remember`: registra memoria operacional curada y resumida.
- `apply`: aplica un preview validado desde el workspace del runtime o del vault hacia un destino final del vault.
- `ask`: detecta intenciones simples de normalización desde lenguaje natural.
- `context`: reporta runtime, workspace técnico, vault configurado, workspace visible e idioma.
- `capabilities`: lista capacidades, comandos, tipos, estados y destinos soportados.

## Capacidades planeadas

La revisión documental contra master-plan está propuesta para evolución futura. Incluye ideas como `review-docs`, `align-readme` y `review-master-plan`, pero esos comandos no existen en v0.1 y no deben tratarse como funcionalidad implementada.

El objetivo futuro es generar planes o reportes de alineación documental que distingan capacidades reales, gaps, documentación obsoleta y decisiones diferidas.

## Uso rápido

```bash
./bin/mi-memoria capabilities --json
./bin/mi-memoria run normalize --input note.md --preview
./bin/mi-memoria run normalize --input note.md --preview --vault-path /path/to/mi-memoria-vault
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

El vault incluye un `workspace/` visible desde Obsidian con `inbox`, `processing`, `preview` y `exports`. Esa zona es para curaduría y edición puntual; no contiene scripts, logs, dependencias ni lógica operacional del runtime.

## Pruebas

```bash
make test
```

La implementación usa solo librería estándar de Python.
