---
name: mi-memoria-normalize
description: Transform free-form Markdown into a normalized Obsidian note with frontmatter, standard sections, local preview output, and explicit write behavior for external vault application.
---

# normalize

## Responsabilidad

Transformar entradas Markdown libres en notas consistentes para un vault Obsidian.

El preview local vive en `runtime/workspace/preview` cuando no se indica vault. Si se pasa `--vault-path` o existe `MI_MEMORIA_VAULT_PATH`, el preview se escribe en `vault/workspace/preview` para revisión visible desde Obsidian.

## Salida estándar

```md
---
title:
type:
status:
created:
updated:
tags:
aliases:
source:
---

# Título

## Resumen

## Desarrollo

## Relaciones

## Pendientes
```

## Reglas

- Mantener metadata mínima.
- Sugerir wikilinks con heurísticas locales simples.
- Generar nombres `yyyy-mm-dd-slug.md`.
- No escribir al vault sin operación explícita.
- Tratar `vault/workspace/preview` como staging visible, no como destino final consolidado.
