---
title: "Racional de evolución curado de `mi-memoria`"
type: memory
status: draft
created: 2026-05-10
updated: 2026-05-10
tags: [mi-memoria, roadmap, racional, fases]
aliases: []
source: "docs/roadmap/mi-memoria-conversation-memory-evolution-rationale-v0.1.md"
---

# Racional de evolución curado

## Memoria

Este documento formaliza la idea central: el LLM asiste, pero no gobierna. La evolución de `mi-memoria` se ordena en fases para evitar sobreingeniería y para preservar el control humano y del runtime.

## Fecha de referencia

- 2026-05-10
- Consolida el racional que aparece en el corpus de P1 a P5 y en la historia temprana del repositorio
- Contexto Git: commit `27756d8`

## Relaciones

- [roadmap maestro](./roadmap-maestro.md)
- [charter baseline](./charter-baseline.md)
- [evolution plan](./evolution-plan.md)

## Decisiones clave

- modelo adoptado: `Human-governed / Runtime-controlled / LLM-assisted`;
- el LLM puede sugerir, resumir y clasificar;
- el LLM no puede mover ni persistir conocimiento sin curación;
- la evolución se organiza en P1 a P5;
- la interoperabilidad se deja al final;
- `context/` se reserva para metaconocimiento y gobernanza.

## Riesgo que se evita

- autonomía prematura;
- persistencia indiscriminada;
- exposición de contratos inmaduros;
- expansión de superficie técnica antes de tener base estable.

## Lectura operativa

La regla central es que el modelo de inteligencia contextual no sustituye gobernanza. En el corpus, esto se traduce en:

- humano decide;
- runtime valida y persiste;
- LLM sugiere y sintetiza.

## Ver también

- [roadmap README](./README.md)
- [docs memory README](../README.md)
