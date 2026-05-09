---
name: mi-memoria-normalize
description: Transform free-form Markdown into a normalized Obsidian note with frontmatter, standard sections, local preview output, and explicit write behavior for external vault application.
---

# normalize

## Responsabilidad

Transformar entradas Markdown libres en notas consistentes para un vault Obsidian.

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
