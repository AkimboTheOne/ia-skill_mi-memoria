---
title: "Inicio rápido de `mi-memoria`"
type: resource
status: active
created: 2026-05-10
updated: 2026-05-10
tags: [mi-memoria, docs, quickstart]
aliases: []
source: "docs/usage.md, scripts/skill_setup.sh"
---

# Inicio Rápido

## Resumen

Este es el camino corto para empezar sin pelear con el sistema:

1. inicializa o apunta a un vault;
2. captura una nota;
3. normaliza o valida;
4. clasifica;
5. revisa;
6. aplica o archiva de forma explícita.

## Desarrollo

```bash
./scripts/skill_setup.sh /path/to/mi-memoria-vault
export MI_MEMORIA_VAULT_PATH=/path/to/mi-memoria-vault
./bin/mi-memoria capabilities --json
./bin/mi-memoria capture --kind idea --text "Idea rápida" --json
./bin/mi-memoria validate --input workspace/inbox/<nota>.md --json
```

## Primeros pasos

La secuencia mínima es vault, captura, validación y clasificación.

## Flujo mínimo recomendado

```mermaid
flowchart LR
  A[Capture] --> B[Validate]
  B --> C[Classify]
  C --> D[Review]
  D --> E[Link]
  E --> F[Summarize]
  F --> G[Normalize/Apply]
```

## Atajos útiles

- `./bin/mi-memoria context --json`
- `./bin/mi-memoria query "..." --path . --json`
- `./bin/mi-memoria template list --json`

## Relaciones

- [overview](./overview.md)
- [commands](./commands.md)
- [workflows](./workflows.md)

## Pendientes

- Añadir ejemplos más específicos por tipo de usuario cuando el README maestro se enlace.
