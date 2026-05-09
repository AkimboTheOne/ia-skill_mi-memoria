# Validación

La validación v0.1 comprueba:

- Frontmatter delimitado por `---`.
- Campos obligatorios: `title`, `type`, `status`, `created`, `updated`, `tags`.
- Tipos válidos: `note`, `decision`, `project`, `resource`, `area`, `memory`.
- Estados válidos: `draft`, `review`, `active`, `archived`.
- Secciones mínimas para notas estándar: `Resumen`, `Desarrollo`, `Relaciones`, `Pendientes`.
- Sección mínima para `type: memory`: `Memoria`.
- Nombre de archivo `yyyy-mm-dd-slug.md` cuando se valida desde archivo.

La validación no ejecuta código ni consulta servicios externos.

## Integridad documental

La documentación debe validarse contra el comportamiento implementado:

- `./bin/mi-memoria capabilities --json` es la fuente para capacidades actuales del CLI.
- `make test` debe pasar antes de considerar consistente una actualización documental.
- Toda referencia a capacidades futuras debe marcarse explícitamente como planeada, diferida, roadmap o propuesta.
- Comandos no implementados como `review-docs`, `align-readme` o `review-master-plan` no deben aparecer como uso actual.
- Los límites de `AGENTS.md` siguen vigentes: sin MCP funcional, sin HTTPS, sin APIs externas, sin secretos y sin agentes autónomos.
