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
