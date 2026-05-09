# Validación

La validación v0.1 comprueba:

- Frontmatter delimitado por `---`.
- Campos obligatorios: `title`, `type`, `status`, `created`, `updated`, `tags`.
- Tipos válidos: `note`, `decision`, `project`, `resource`, `area`.
- Estados válidos: `draft`, `review`, `active`, `archived`.
- Secciones mínimas: `Resumen`, `Desarrollo`, `Relaciones`, `Pendientes`.
- Nombre de archivo `yyyy-mm-dd-slug.md` cuando se valida desde archivo.

La validación no ejecuta código ni consulta servicios externos.

Los previews validables pueden vivir en `runtime/workspace/preview` o en `vault/workspace/preview`. La ubicación no cambia las reglas de frontmatter, secciones ni nombre de archivo.

## Integridad documental

La documentación debe validarse contra el comportamiento implementado:

- `./bin/mi-memoria capabilities --json` es la fuente para capacidades actuales del CLI.
- `make test` debe pasar antes de considerar consistente una actualización documental.
- Las pruebas deben crear temporales propios bajo `runtime/tmp/tests` para evitar depender de particularidades del host.
- `scripts/skill_setup.sh` debe crear el workspace visible del vault para revisión en Obsidian.
- Toda referencia a capacidades futuras debe marcarse explícitamente como planeada, diferida, roadmap o propuesta.
- Comandos no implementados como `review-docs`, `align-readme` o `review-master-plan` no deben aparecer como uso actual.
- Los límites de `AGENTS.md` siguen vigentes: sin MCP funcional, sin HTTPS, sin APIs externas, sin secretos y sin agentes autónomos.
