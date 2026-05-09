# mi-memoria

Runtime local de skills para operar sobre repositorios de conocimiento Markdown, separado del vault de conocimiento.

`mi-memoria` v0.1 implementa una baseline mínima:

- CLI local sin dependencias externas obligatorias.
- Skill `normalize` para convertir texto o Markdown libre en notas Obsidian consistentes.
- Validación de estructura, frontmatter, nombres y secciones mínimas.
- Workspace transitorio con preview seguro.
- Escritura controlada hacia un vault externo.
- Memoria curada del proyecto en el vault mediante `remember`.
- Setup inicial de vault mediante `scripts/skill_setup.sh`.

## Capacidades actuales v0.1

La fuente operativa para capacidades actuales es:

```bash
./bin/mi-memoria capabilities --json
```

En v0.1 el runtime expone:

- `normalize`: normaliza Markdown libre hacia una nota Obsidian consistente.
- `validate`: valida frontmatter, secciones mínimas y nombre de archivo.
- `remember`: registra memoria curada y resumida en `memory/` del vault por defecto.
- `apply`: aplica un preview validado hacia un vault externo.
- `ask`: detecta intenciones simples de normalización desde lenguaje natural.
- `context`: reporta runtime, workspace, vault configurado e idioma.
- `capabilities`: lista capacidades, comandos, tipos, estados y destinos soportados.

## Capacidades planeadas

La revisión documental contra master-plan está propuesta para evolución futura. Incluye ideas como `review-docs`, `align-readme` y `review-master-plan`, pero esos comandos no existen en v0.1 y no deben tratarse como funcionalidad implementada.

El objetivo futuro es generar planes o reportes de alineación documental que distingan capacidades reales, gaps, documentación obsoleta y decisiones diferidas.

## Uso rápido

```bash
./bin/mi-memoria capabilities --json
./bin/mi-memoria run normalize --input note.md --preview
./bin/mi-memoria validate --input workspace/preview/2026-05-08-nota.md
./bin/mi-memoria apply --input workspace/preview/2026-05-08-nota.md --vault-path /path/to/mi-memoria-vault
./bin/mi-memoria remember --summary "Se adopta Python estándar para v0.1." --vault-path /path/to/mi-memoria-vault
```

También puede configurarse el vault por entorno:

```bash
export MI_MEMORIA_VAULT_PATH=/path/to/mi-memoria-vault
```

Con el vault configurado, `remember` escribe por defecto en `memory/` del vault. La memoria interna del runtime solo debe usarse para comportamiento operacional del skill:

```bash
./bin/mi-memoria remember --summary "Convención interna del skill." --scope runtime
```

Las plantillas del vault tienen prioridad. Si falta una plantilla primitiva del vault, el runtime usa la plantilla CORE de `skills/core/templates` y emite un warning recomendando restaurarla con `scripts/skill_setup.sh` o crear una plantilla propia.

## Inicializar un vault

```bash
./scripts/skill_setup.sh /path/to/mi-memoria-vault
```

El script crea la estructura mínima y copia las plantillas CORE `note` y `memory` sin sobrescribir archivos existentes. Puede volver a ejecutarse sobre un vault existente para agregar plantillas faltantes.

## Pruebas

```bash
make test
```

La implementación usa solo librería estándar de Python.
