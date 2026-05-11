---
title: "Flujos de trabajo de `mi-memoria`"
type: resource
status: active
created: 2026-05-10
updated: 2026-05-10
tags: [mi-memoria, docs, workflows]
aliases: []
source: "docs/usage.md, docs/architecture.md"
---

# Flujos de Trabajo

## Resumen

Los flujos útiles del skill siguen una secuencia simple:

- capturar;
- clasificar;
- revisar;
- enlazar;
- resumir;
- normalizar;
- aplicar;
- consolidar.

## Desarrollo

### Flujo diario

```mermaid
flowchart LR
  I[Inbox] --> C[Capture]
  C --> V[Validate]
  V --> F[Classify]
  F --> R[Review]
  R --> L[Link]
  L --> S[Summarize]
```

### Flujo de publicación

```mermaid
flowchart LR
  P[Preview] --> A[Apply]
  A --> M[Memory]
  M --> D[Docs]
```

## Regla práctica

Si el archivo todavía necesita decisión humana, se queda en `workspace/`.
Si ya es referencia de uso o documentación, se promueve al vault.

## Relaciones

- [quickstart](./quickstart.md)
- [commands](./commands.md)
- [troubleshooting](./troubleshooting.md)
- [memory README](../../memory/README.md)

## Pendientes

- Incorporar un flujo explícito para [remember](./commands.md) cuando la sección de usuario del [README.md](../../../README.md) sea actualizada.
