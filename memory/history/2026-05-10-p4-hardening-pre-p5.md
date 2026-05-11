---
title: "Hardening P4 previo a P5"
type: memory
status: active
created: 2026-05-10
updated: 2026-05-10
tags: ["mi-memoria", "memory", "p4", "p5-readiness"]
aliases: []
source: "release-0.4.1"
---

# Hardening P4 previo a P5

## Memoria

Se consolidó un hardening de madurez para P4 con el objetivo de eliminar brechas entre roadmap y contratos reales del CLI antes de iniciar interoperabilidad P5.

Cambios clave:

- `capture` ahora soporta intención curatorial (`--kind`) y compatibilidad roadmap para `idea` y `reference` con mapeo seguro a tipos canónicos.
- `decision` incorpora `decision_status` como estado ADR ligero independiente del `status` operacional de nota.
- `publish` incorpora `--format markdown` y `--context-pack` para exportaciones controladas desde artefactos de contexto.
- mensajes de diagnóstico (`review`, `curate`, `drift-detection`) distinguen mejor ejecución del comando vs hallazgos de calidad.

Riesgos mitigados:

- desalineación documental vs implementación real de P4;
- ambigüedad en estado de decisiones;
- falta de contrato explícito para publicación por context-pack;
- preparación incompleta para gates de P5.

## Contexto

P5 permanece diferida. No se implementó MCP bridge, HTTPS runtime ni proveedores externos.

Gates de entrada a P5:

- exposición inicial read-only;
- no ampliar permisos respecto a CLI local;
- pruebas offline y mocks obligatorios;
- bloqueo explícito de operaciones destructivas remotas.
