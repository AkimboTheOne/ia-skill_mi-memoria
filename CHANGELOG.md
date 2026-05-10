# Changelog

## v0.1.0

- Baseline inicial del runtime local `mi-memoria`.
- CLI Python estándar.
- Skill `normalize`.
- Validación Markdown/Obsidian mínima.
- Workspace transitorio.
- Workspace curatorial visible dentro del vault para revisión en Obsidian.
- Temporales de prueba contenidos bajo `runtime/tmp/tests`.
- Alias corto de activación `/mem` para el runtime `mi-memoria`.
- Escritura controlada hacia vault externo.
- Memoria curada en vault por defecto; memoria local del runtime solo con `--scope runtime`.
- Setup inicial de vault.

## v0.1.1

- Expansión P1 del CLI con comandos top-level: `capture`, `classify`, `review`, `link`, `summarize`.
- `capture` guarda notas estructuradas en `workspace/inbox` (runtime o `vault/workspace/inbox` cuando hay vault configurado).
- `classify` propone destino (`00-inbox`, `10-areas`, `20-projects`, `30-resources`, `40-archive`) sin mover archivos.
- `classify` prioriza `type` del frontmatter; si infiere semánticamente, responde con `confidence=medium` y alternativas.
- `review` genera reportes verificables en `workspace/preview` (`*-review-report.md` y `*-review-report.json`).
- `link` entrega sugerencias de wikilinks sin persistencia automática.
- `summarize` genera síntesis trazable con lista de fuentes y salida en `workspace/preview` por defecto.
- `capabilities --json` actualizado para exponer capacidades P1 implementadas.
- Cobertura de pruebas ampliada en `tests/test_cli.py` para contratos y restricciones de P1.
- Documentación operativa actualizada en `README.md`, `SKILL.md` y `docs/usage.md`.
