---
title: "Charter baseline curado de `mi-memoria`"
type: memory
status: draft
created: 2026-05-10
updated: 2026-05-10
tags: [mi-memoria, roadmap, baseline, memoria]
aliases: []
source: "docs/roadmap/mi-memoria-charter-baseline-v0.1.md"
---

# Charter baseline curado

## Memoria

La baseline define a `mi-memoria` como un runtime local separado del vault de conocimiento. El objetivo es operar sobre Markdown de forma controlada, incremental y verificable.

## Fecha de referencia

- 2026-05-08
- Validado en `CHANGELOG.md` como baseline `v0.1.0`
- Contexto Git: commit `6239c2e`

## Relaciones

- [roadmap maestro](./roadmap-maestro.md)
- [evolution rationale](./evolution-rationale.md)
- [evolution plan](./evolution-plan.md)

## Decisiones clave

- runtime y vault son repositorios distintos;
- la memoria persistente debe ser curada;
- la arquitectura debe crecer por fases;
- el primer skill oficial es `normalize`;
- la activación puede ser natural, slash command o CLI;
- la interoperabilidad no forma parte de la baseline.

## Qué se conserva

- separación técnica;
- minimalismo operacional;
- skills pequeños y desacoplados;
- salidas verificables;
- memoria reflexiva y útil.

## Implicación documental

Este charter no se usa como nota operativa diaria. Se conserva como fundamento arquitectónico y referencia de gobernanza.

## Lectura operativa

Esta pieza es fundacional. No describe features de fase, sino restricciones que siguen vigentes:

- separación runtime/vault;
- memoria curada;
- crecimiento incremental;
- activación CLI y slash command;
- `normalize` como primer skill.

## Ver también

- [roadmap README](./README.md)
- [docs memory README](../README.md)
