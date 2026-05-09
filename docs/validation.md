# Validación

La validación v0.1 comprueba:

- Frontmatter delimitado por `---`.
- Campos obligatorios: `title`, `type`, `status`, `created`, `updated`, `tags`.
- Tipos válidos: `note`, `decision`, `project`, `resource`, `area`.
- Estados válidos: `draft`, `review`, `active`, `archived`.
- Secciones mínimas: `Resumen`, `Desarrollo`, `Relaciones`, `Pendientes`.
- Nombre de archivo `yyyy-mm-dd-slug.md` cuando se valida desde archivo.

La validación no ejecuta código ni consulta servicios externos.
