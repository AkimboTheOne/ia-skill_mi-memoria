#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Uso: ./scripts/skill_setup.sh /path/to/mi-memoria-vault" >&2
  exit 2
fi

VAULT="$1"

if [ -e "$VAULT" ] && [ ! -d "$VAULT" ]; then
  echo "La ruta existe y no es un directorio: $VAULT" >&2
  exit 2
fi

mkdir -p "$VAULT"

if [ ! -w "$VAULT" ]; then
  echo "Sin permisos de escritura en: $VAULT" >&2
  exit 2
fi

mkdir -p \
  "$VAULT/00-inbox" \
  "$VAULT/10-areas" \
  "$VAULT/20-projects" \
  "$VAULT/30-resources" \
  "$VAULT/40-archive" \
  "$VAULT/assets" \
  "$VAULT/templates" \
  "$VAULT/indexes" \
  "$VAULT/memory" \
  "$VAULT/workspace/inbox" \
  "$VAULT/workspace/processing" \
  "$VAULT/workspace/preview" \
  "$VAULT/workspace/exports"

for dir in \
  "$VAULT/00-inbox" \
  "$VAULT/10-areas" \
  "$VAULT/20-projects" \
  "$VAULT/30-resources" \
  "$VAULT/40-archive" \
  "$VAULT/assets" \
  "$VAULT/templates" \
  "$VAULT/indexes" \
  "$VAULT/memory" \
  "$VAULT/workspace/inbox" \
  "$VAULT/workspace/processing" \
  "$VAULT/workspace/preview" \
  "$VAULT/workspace/exports"; do
  touch "$dir/.gitkeep"
done

create_if_missing() {
  local path="$1"
  local content="$2"
  if [ ! -e "$path" ]; then
    printf "%s\n" "$content" > "$path"
  fi
}

create_if_missing "$VAULT/templates/note.md" "---
title:
type: note
status: draft
created:
updated:
tags: []
aliases: []
source:
---

# Título

## Resumen

## Desarrollo

## Relaciones

## Pendientes"

create_if_missing "$VAULT/indexes/README.md" "# Índices

Índices del vault mi-memoria."

create_if_missing "$VAULT/memory/README.md" "# Memoria

Memoria curada consolidada del vault."

create_if_missing "$VAULT/workspace/README.md" "# Workspace

Zona visible de curaduría para Obsidian.

- \`inbox\`: entradas pendientes de organizar.
- \`processing\`: notas en edición puntual.
- \`preview\`: previews generados por el runtime antes de aplicar.
- \`exports\`: salidas curadas o paquetes temporales.

Este directorio no contiene lógica operacional, scripts, logs ni dependencias del runtime."

echo "Vault inicializado: $VAULT"
