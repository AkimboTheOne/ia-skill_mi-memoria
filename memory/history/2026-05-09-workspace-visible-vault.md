---
title: "Workspace visible del vault"
type: memory
status: active
created: 2026-05-09
updated: 2026-05-09
tags: ["mi-memoria", "workspace", "vault", "obsidian"]
source: "correccion-workspace-visible"
---

# Workspace visible del vault

## Memoria

Se diferencia el workspace tecnico del runtime (`runtime/workspace`) del workspace curatorial visible dentro del vault (`vault/workspace`).

El runtime conserva temporales tecnicos y fallback local. El vault debe incluir `workspace/inbox`, `workspace/processing`, `workspace/preview` y `workspace/exports` para revisar, editar y reubicar ideas desde Obsidian sin introducir scripts, logs, dependencias ni logica operacional dentro del vault.

Las pruebas y temporales controlados por el runtime deben preferir `runtime/tmp/tests` o `runtime/tmp` sobre temporales del sistema para evitar diferencias del anfitrion como `/var` frente a `/private/var`.
