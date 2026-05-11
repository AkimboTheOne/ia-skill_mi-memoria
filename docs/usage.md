# Uso

## Captura rápida

```bash
./bin/mi-memoria capture --text "Idea rápida"
./bin/mi-memoria capture --kind idea --text "Idea rápida curada"
./bin/mi-memoria capture --type decision --text "Separar runtime y vault"
./bin/mi-memoria capture --to workspace/processing --text "Entrada de curaduría"
./bin/mi-memoria capture --input note.md --json
```

`capture` guarda en `workspace/inbox` del runtime por defecto, o en `vault/workspace/inbox` si hay vault configurado.

## Daily

```bash
./bin/mi-memoria daily --json
./bin/mi-memoria daily --date 2026-05-10 --append "nota rápida" --summary --json
```

## Decision

```bash
./bin/mi-memoria decision new --title "Separar runtime y vault" --decision-status accepted --json
./bin/mi-memoria decision from-session --session arquitectura-mi-memoria --decision-status proposed --json
./bin/mi-memoria decision list --json
```

## Clasificación (sin mover)

```bash
./bin/mi-memoria classify --input workspace/inbox/2026-05-08-idea.md --json
```

`classify` propone destino y alternativas; no mueve archivos.

## Review

```bash
./bin/mi-memoria review --input workspace/inbox/2026-05-08-idea.md --json
./bin/mi-memoria review --path workspace/inbox --json
```

`review` genera reportes en `workspace/preview`: `*-review-report.md` y `*-review-report.json`.

## Link (sugerencias)

```bash
./bin/mi-memoria link --input workspace/inbox/2026-05-08-idea.md --preview --json
```

`link` sugiere wikilinks; no escribe en la nota fuente.

## Summarize

```bash
./bin/mi-memoria summarize --input workspace/inbox/2026-05-08-idea.md --json
./bin/mi-memoria summarize --path workspace/inbox --output workspace/preview/summary.md --json
```

## Index

```bash
./bin/mi-memoria index --path workspace/inbox --json
```

Genera índice navegable y detección de títulos duplicados sin mover archivos.

## Timeline

```bash
./bin/mi-memoria timeline --path workspace/inbox --json
```

Extrae fechas de frontmatter y marca como `inferred` cuando se deducen.

## Drift detection

```bash
./bin/mi-memoria drift-detection --path workspace/inbox --json
```

Genera `drift-report.md` y `drift-report.json` con deriva verificable.

## Curate

```bash
./bin/mi-memoria curate --path workspace/inbox --json
./bin/mi-memoria curate --path workspace/inbox --report workspace/preview/curation-report.md --json
```

`curate` produce plan/reporte, no ejecuta mutaciones masivas.

## Publish

```bash
./bin/mi-memoria publish --path workspace/inbox --output workspace/exports/pack --format markdown --json
./bin/mi-memoria publish --path workspace/inbox --output workspace/exports/pack --strip-private --format markdown --json
./bin/mi-memoria publish --context-pack workspace/exports/context-pack.json --output workspace/exports/pack-context --json
```

`publish` exporta paquetes sin modificar archivos fuente.

## Estado P5

P5 no está ejecutada en esta versión. No existen comandos `serve`, endpoints HTTPS ni bridge MCP activos en el runtime.

## Query contextual

```bash
./bin/mi-memoria query "runtime separado del vault" --path . --json
```

`query` retorna `results`, `evidence`, `inference` y `uncertainty`.

## Context build

```bash
./bin/mi-memoria context-build --topic "taxonomía" --path . --json
```

Genera `context-pack.md`, `context-pack.json` y `source-map.json` en `workspace/exports`.

## Session temporal

```bash
./bin/mi-memoria session start --name arquitectura-mi-memoria --json
./bin/mi-memoria session add --name arquitectura-mi-memoria --input workspace/inbox/2026-05-08-idea.md --json
./bin/mi-memoria session context --name arquitectura-mi-memoria --json
./bin/mi-memoria session close --name arquitectura-mi-memoria --remember --json
```

`session close --remember` no persiste memoria automáticamente; requiere flujo explícito de curaduría.

## Normalizar con preview

```bash
./bin/mi-memoria run normalize --input note.md --preview
```

Sin vault configurado, el preview queda en `runtime/workspace/preview`.

## Normalizar con preview visible en Obsidian

```bash
./bin/mi-memoria run normalize --input note.md --preview --vault-path /path/to/vault
```

Con `--vault-path` o `MI_MEMORIA_VAULT_PATH`, el preview queda en `vault/workspace/preview`.

## Escribir al vault

```bash
./bin/mi-memoria run normalize --input note.md --write --vault-path /path/to/vault
```

## Aplicar un preview

```bash
./bin/mi-memoria apply --input workspace/preview/archivo.md --vault-path /path/to/vault
```

`apply` acepta previews desde `runtime/workspace/preview` o desde `vault/workspace/preview`.

## Validar

```bash
./bin/mi-memoria validate --input archivo.md --json
```

## Plantillas

```bash
./bin/mi-memoria template list --json
./bin/mi-memoria template show --name note --vault-path /path/to/vault
./bin/mi-memoria template generate --name log-diario --type note --description "Registro diario de eventos" --preview --json
./bin/mi-memoria template validate --input workspace/preview/templates/log-diario.md --json
./bin/mi-memoria template apply --input workspace/preview/templates/log-diario.md --vault-path /path/to/vault --json
```

`template generate` no escribe al vault. Genera previews en `workspace/preview/templates`. `template apply` requiere vault y no sobrescribe templates existentes.

## Memoria

```bash
./bin/mi-memoria remember --summary "Convención aprobada: usar estado draft por defecto." --vault-path /path/to/vault
./bin/mi-memoria remember --type convention --summary "Usar preview antes de apply." --vault-path /path/to/vault
```

`remember` guarda memoria curada en `memory/` del vault por defecto. También puede usar `MI_MEMORIA_VAULT_PATH`.

Si falta `vault/templates/memory.md`, el runtime usa la plantilla CORE y reporta un warning. Para restaurar plantillas base sin sobrescribir las propias:

```bash
./scripts/skill_setup.sh /path/to/vault
```

La memoria interna del runtime es una excepción explícita para modular o actualizar el comportamiento del skill:

```bash
./bin/mi-memoria remember --summary "Convención interna del skill." --scope runtime
```

## Archive gobernado

```bash
./bin/mi-memoria archive --input 30-resources/2026-05-10-nota.md --preview --vault-path /path/to/vault --json
./bin/mi-memoria archive --input 30-resources/2026-05-10-nota.md --apply --vault-path /path/to/vault --json
```
