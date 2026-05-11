---
title: "Flujos de trabajo de `mi-memoria`"
type: resource
status: active
created: 2026-05-10
updated: 2026-05-11
tags: [mi-memoria, docs, workflows]
aliases: []
source: "docs/usage.md, docs/architecture.md"
---

# Flujos de trabajo

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

### Cómo leer esta guía

- Usa los bloques `prompt` para pensar el flujo como usuario o agente.
- Usa los bloques `bash` para ejecutar el flujo real.
- Sigue la secuencia mínima antes de mover algo al vault.
- Si algo requiere decisión humana, permanece en `workspace/`.

### Flujo conceptual

```prompt
Toma una idea rápida y llévala hasta una nota curada.
Revisa un preview antes de aplicar.
Construye un flujo diario para capturar, clasificar y resumir.
```

### Flujo técnico diario

```bash
./bin/mi-memoria capture --kind idea --text "Idea rápida" --json
./bin/mi-memoria classify --input workspace/inbox/nota.md --json
./bin/mi-memoria review --path workspace/inbox --json
./bin/mi-memoria link --input workspace/inbox/nota.md --preview --json
./bin/mi-memoria summarize --path workspace/inbox --json
./bin/mi-memoria run normalize --input note.md --preview --json
./bin/mi-memoria validate --input workspace/preview/note.md --json
./bin/mi-memoria apply --input workspace/preview/note.md --vault-path /path/to/vault --json
```

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

### Decisión rápida

- `workspace/` para captura, revisión y preview.
- `docs/30-resources/` para documentación de usuario.
- `docs/memory/` para criterios, decisiones y convenciones.
- `40-archive/` para material cerrado.

### Escenarios comunes

```prompt
Tengo una nota nueva: ¿la clasifico o la normalizo primero?
Quiero convertir una idea en memoria curada sin mover nada automáticamente.
Necesito revisar un preview antes de aplicarlo al vault.
```

```bash
./bin/mi-memoria daily --append "Nota rápida" --json
./bin/mi-memoria decision new --title "Adoptar sentence case" --decision-status accepted --json
./bin/mi-memoria curate --path workspace/inbox --json
./bin/mi-memoria publish --path workspace/inbox --format markdown --output workspace/exports/pack --json
./bin/mi-memoria archive --input 30-resources/nota.md --preview --vault-path /path/to/vault --json
```

## Relaciones

- [quickstart](./quickstart.md)
- [commands](./commands.md)
- [troubleshooting](./troubleshooting.md)
- [memory README](../../memory/README.md)
- [documentation governance](../../documentation-governance.md)

## Pendientes

- Incorporar un flujo explícito para [remember](./commands.md) cuando la sección de usuario del [README.md](../../../README.md) sea actualizada.
- Añadir un ejemplo de publicación de context pack con foco en documentación de usuario.
