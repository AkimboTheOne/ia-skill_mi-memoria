# AGENTS.md

## Principios Operacionales

- El runtime opera sobre un vault externo; nunca debe mezclar lógica operacional dentro del vault.
- Toda escritura fuera del workspace requiere intención explícita (`--write` o `apply`).
- No se deben ejecutar comandos arbitrarios desde el skill.
- No se deben almacenar conversaciones completas como memoria persistente.
- La memoria aceptada debe ser explícita, curada, resumida y útil.

## Límites v0.1

- Sin MCP funcional.
- Sin HTTPS.
- Sin APIs externas.
- Sin secretos, tokens ni credenciales.
- Sin agentes autónomos.

## Contexto de Código (para contributors/agentes)

- Lenguaje: Python estándar (sin dependencias externas obligatorias).
- Entry point CLI: `bin/mi-memoria` y parser/comandos en `cli/main.py`.
- Suite de pruebas: `tests/test_cli.py` (ejecutar con `make test`).
- Plantillas CORE: `skills/core/templates/*.md`.
- Setup mínimo de vault: `scripts/skill_setup.sh`.
- Historial de cambios funcionales: revisar `CHANGELOG.md` antes de diseñar/refactorizar.

## Capacidades P1 implementadas

- `capture`: crea notas en `workspace/inbox` (runtime o vault workspace visible).
- `classify`: propone destino taxonómico con racional; no mueve archivos.
- `review`: emite reportes verificables `.md` y `.json`.
- `link`: sugiere wikilinks sin persistir.
- `summarize`: genera síntesis con trazabilidad de fuentes.

## Reglas de Mutación durante desarrollo

- No romper contratos existentes (`normalize`, `validate`, `remember`, `template`, `apply`, `context`, `capabilities`, `upgrade`).
- Toda escritura final al vault debe seguir siendo explícita (`--write` o `apply`).
- `classify`, `review`, `link`, `summarize` no deben mover ni reubicar notas automáticamente.
- Mantener salida dual: humana y JSON en comandos operacionales.
- `capabilities --json` debe reflejar comandos reales implementados.

## Definición de Terminado (DoD) para cambios de CLI

- Comando accesible desde parser top-level.
- Salida JSON consistente con campos `ok`, `command`, y artefactos/resultados del comando.
- Cobertura mínima en `tests/test_cli.py` para caso exitoso y restricción crítica.
- Documentación alineada en `README.md`, `SKILL.md` y `docs/usage.md`.
- `make test` en verde antes de cerrar la tarea.

## Política de Versionamiento y Madurez

- Esquema canónico:
- `v0.1.x`: baseline y consolidación inicial.
- `v0.2.x`: P2 estabilizado.
- `v0.3.x`: P3 (inteligencia contextual local).
- Campos obligatorios en cada release: `cli/__init__.py::__version__`, `capabilities.version`, `CHANGELOG.md`, `README.md` y `SKILL.md` deben quedar alineados.
- Una fase solo puede marcarse `stable` con comandos implementados, pruebas en verde y documentación alineada.
- Capacidades no implementadas deben quedar explícitamente como `roadmap` o `propuesta`.
- Semántica de madurez operativa:
- `p1-stable`
- `p2-stable`
- `p3-in-progress`
- `p3-stable`
- `capabilities --json` debe exponer siempre la madurez operativa vigente.
