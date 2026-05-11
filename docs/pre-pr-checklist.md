# Pre-PR Checklist (pre-p5-madurez)

## Objetivo
Checklist de cierre para asegurar que la refactorización modular P4-preP5 mantiene retro-compatibilidad, trazabilidad y documentación alineada antes de abrir PR.

## Verificación técnica
- [x] `make test` en verde.
- [x] Contratos CLI existentes preservados (flags, códigos de salida, estructura JSON principal).
- [x] `capabilities --json` alineado con comandos implementados.
- [x] Metadata LLM en `docs/skill-manifest.json` con test de coherencia.
- [x] Telemetría operacional activa en `logs/operations.log` y `logs/operations.jsonl`.

## Verificación de arquitectura
- [x] `cli/main.py` reducido a parser + wiring + utilidades compartidas pendientes.
- [x] Lógica de comandos distribuida en `cli/commands/*` por dominio.
- [x] Núcleo reutilizable en `cli/core/*`.
- [x] Servicios desacoplados en `cli/services/*`.
- [x] Integraciones runtime en `cli/infra/*`.

## Verificación de gobernanza
- [x] No se introdujeron dependencias externas obligatorias.
- [x] No se añadieron mutaciones silenciosas al vault.
- [x] `workspace/preview` y `workspace/exports` ignorados para evitar ruido operativo.
- [x] Changelog actualizado con los bloques de extracción y validación.

## Pendiente para paso final (no ejecutar aún)
- [ ] Armar resumen final de PR (scope, riesgos, pruebas, comandos verificados).
- [ ] Revisión manual final de docs (`README.md`, `SKILL.md`, `docs/usage.md`, `docs/architecture.md`).
- [ ] Crear PR desde `pre-p5-madurez`.
