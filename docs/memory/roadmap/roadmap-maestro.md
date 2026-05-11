---
title: "Roadmap maestro de `mi-memoria`"
type: memory
status: draft
created: 2026-05-10
updated: 2026-05-10
tags: [mi-memoria, roadmap, memoria, gobernanza]
aliases: []
source: "sintesis-roadmap"
---
# Roadmap Maestro

## Memoria

Este documento consolida el histórico de decisiones de `mi-memoria` en una sola línea narrativa:

- el runtime es independiente del vault;
- la memoria persistente debe ser curada, no un volcado de conversaciones;
- la CLI local es el contrato primario;
- la evolución se organiza por fases;
- la interoperabilidad se difiere hasta que la base local esté madura.

La documentación fuente fue absorbida desde `docs/roadmap/` y el staging paralelo de `docs/00-inbox/roadmap/`. Este maestro no modifica esos originales; los sintetiza para organización documental y futura aplicación al vault definitivo.

## Relaciones

- [charter baseline](./charter-baseline.md)
- [evolution rationale](./evolution-rationale.md)
- [evolution plan](./evolution-plan.md)
- [P1 consolidación operacional](./p1-consolidacion-operacional.md)
- [P2 gobernanza del conocimiento](./p2-gobernanza-conocimiento.md)
- [P3 inteligencia contextual](./p3-inteligencia-contextual.md)
- [P4 flujos productivos](./p4-flujos-productivos.md)
- [P5 interoperabilidad controlada](./p5-interoperabilidad-controlada.md)

## Cronología Validada

- 2026-05-08: baseline inicial y separación runtime/vault consolidada en `v0.1.0`.
- 2026-05-10: P1 entra como expansión operativa con `capture`, `classify`, `review`, `link` y `summarize`.
- 2026-05-10: P2 formaliza gobernanza con `index`, `timeline`, `drift-detection`, `archive` y `remember` evolutivo.
- 2026-05-10: P3 introduce `query`, `context-build` y `session`.
- 2026-05-10: P4 formaliza `daily`, `decision`, `curate` y `publish`, con `capture` avanzado.
- 2026-05-10: P5 queda diferida; la documentación de cierre pre-P5 valida contratos, no interoperabilidad.

## Corpus De Origen

Fuentes revisadas:

- `docs/roadmap/mi-memoria-charter-baseline-v0.1.md`
- `docs/roadmap/mi-memoria-conversation-memory-evolution-rationale-v0.1.md`
- `docs/roadmap/mi-memoria-evolution-master-plan-v0.1.md`
- `docs/roadmap/mi-memoria-p1-consolidacion-operacional-subcharter-v0.1.md`
- `docs/roadmap/mi-memoria-p2-gobernanza-conocimiento-subcharter-v0.1.md`
- `docs/roadmap/mi-memoria-p3-inteligencia-contextual-subcharter-v0.1.md`
- `docs/roadmap/mi-memoria-p4-flujos-productivos-subcharter-v0.1.md`
- `docs/roadmap/mi-memoria-p5-interoperabilidad-controlada-subcharter-v0.1.md`
- Réplicas de trabajo en `docs/00-inbox/roadmap/`

## Decisiones Consolidadas

### 1. Separación arquitectónica

`mi-memoria` es un runtime. El vault es un repositorio de conocimiento. Esa separación no es decorativa; define permisos, rutas y límites operacionales.

### 2. Memoria curada

La persistencia válida no es conversación completa. Solo deben conservarse decisiones, convenciones, aprendizajes, restricciones y resúmenes útiles.

### 3. Evolución por fases

La ruta aprobada es:

1. P1 Consolidación Operacional
2. P2 Gobernanza del Conocimiento
3. P3 Inteligencia Contextual Local
4. P4 Flujos Productivos de Conocimiento
5. P5 Interoperabilidad Controlada

### 4. LLM asistido, no gobernante

El LLM puede expandir, resumir, clasificar y sugerir, pero no mover, archivar o redefinir la taxonomía sin control del runtime y del usuario.

### 5. CLI-first

La CLI es el contrato operativo primario. Cualquier capa adicional debe preservar ese contrato.

### 6. Interoperabilidad diferida

MCP, HTTPS y proveedores externos quedan al final. Exponer contratos inmaduros antes de tiempo aumenta deuda y riesgo.

## Mapa Operativo Por Fase

### P1

Objetivo: cerrar el ciclo básico de trabajo cotidiano.

- `capture`
- `classify`
- `review`
- `link`
- `summarize`

### P2

Objetivo: gobernar el crecimiento del conocimiento.

- `index`
- `timeline`
- `drift-detection`
- `archive`
- `remember` evolucionado

### P3

Objetivo: construir contexto local trazable.

- `query`
- `context-build`
- `session`

### P4

Objetivo: formalizar workflows productivos.

- `capture` avanzado
- `daily`
- `decision`
- `curate`
- `publish`

### P5

Objetivo: interoperabilidad controlada y segura.

- MCP bridge
- HTTPS runtime
- external providers

## Reglas Que Deben Permanecer

- el runtime no se incrusta dentro del vault;
- no se escriben memorias indiscriminadas;
- no se mueven notas sin intención explícita;
- no se publican capacidades inmaduras;
- no se pierde trazabilidad entre síntesis y fuentes.

## Lectura Operativa

Este corpus debe leerse como una secuencia documental:

1. fundamento arquitectónico;
2. racional de evolución;
3. plan por fases;
4. curación por fase;
5. aplicación explícita al vault definitivo.

## Preparación Para Vault Definitivo

Estos documentos curados están listos para aplicar cuando se decida el destino final en el vault. La intención actual es mantenerlos como staging visible, con rutas reproducibles y referencias preservadas.

- [roadmap README](./README.md)
- [docs memory README](../README.md)

## Ver también

- [README raíz](../../../README.md)
- [Documentación de usuario](../../30-resources/mi-memoria/index.md)
