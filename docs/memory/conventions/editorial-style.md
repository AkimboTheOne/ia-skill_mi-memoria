---
title: "Convención de estilo editorial"
type: memory
status: active
created: 2026-05-11
updated: 2026-05-11
tags: [mi-memoria, style, editorial]
---

# Convención de estilo editorial

## Memoria

Regla activa para títulos, encabezados y texto visible del corpus curado.

## Resumen

Usar sentence case por defecto.

Capitalizar solo la primera palabra.

Conservar mayúsculas internas solo para nombres propios, siglas, términos técnicos, fases P1-P5 y marcas cuya semántica dependa de esa forma.

Usar `prompt` para activación conversacional y ejemplos de intención.

Usar `bash` para comandos técnicos reales, setup, validación y actualización.

## Desarrollo

- Usar `Fecha de referencia`, no `Fecha De Referencia`.
- Usar `Gobernanza documental`, no `Gobernanza Documental`.
- Usar `¿qué es ...?` cuando el texto introduce una pregunta real.
- Mantener mayúsculas en `CLI`, `MCP`, `LLM` y otros acrónimos oficiales.
- No rebajar nombres propios o títulos técnicos que dependan de la capitalización para ser reconocibles.
- Aplicar la misma regla en `docs/`, `memory/` y el corpus curado del vault.
- En documentación de usuario, separar explícitamente activación en `prompt` y ejecución técnica en `bash`.

## Relaciones

- [taxonomía documental](documentation-taxonomy.md)
- [memoria README](../README.md)
- [documentación de usuario](../../30-resources/mi-memoria/index.md)
- [quickstart](../../30-resources/mi-memoria/quickstart.md)

## Pendientes

- Revisar y normalizar el resto de encabezados del vault con esta convención.
- Aplicar esta distinción de `prompt`/`bash` en cualquier página nueva de documentación de usuario.
