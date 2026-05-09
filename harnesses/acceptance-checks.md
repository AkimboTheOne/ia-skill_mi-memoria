# Acceptance Checks

- El CLI funciona localmente.
- `normalize` produce Markdown consistente.
- `--preview` genera salida verificable en `workspace/preview`.
- `--write` requiere vault válido.
- `apply` solo acepta previews.
- `validate` reporta errores y warnings claros.
- `remember` guarda memoria curada.
- `scripts/skill_setup.sh` inicializa un vault externo.
- El vault no recibe logs, scripts ni dependencias del runtime.
- Las capacidades documentadas como actuales coinciden con `./bin/mi-memoria capabilities --json`.
- La suite `make test` pasa antes de publicar cambios documentales.
- Las capacidades futuras se marcan como planeadas, diferidas, roadmap o propuestas.
- `review-docs`, `align-readme` y `review-master-plan` no se documentan como comandos actuales en v0.1.
