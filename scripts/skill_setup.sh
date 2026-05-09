#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Uso: ./scripts/skill_setup.sh /path/to/mi-memoria-vault" >&2
  exit 2
fi

VAULT="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CORE_TEMPLATES="$ROOT/skills/core/templates"

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
  "$VAULT/memory"

for dir in \
  "$VAULT/00-inbox" \
  "$VAULT/10-areas" \
  "$VAULT/20-projects" \
  "$VAULT/30-resources" \
  "$VAULT/40-archive" \
  "$VAULT/assets" \
  "$VAULT/templates" \
  "$VAULT/indexes" \
  "$VAULT/memory"; do
  touch "$dir/.gitkeep"
done

create_if_missing() {
  local path="$1"
  local content="$2"
  if [ ! -e "$path" ]; then
    printf "%s\n" "$content" > "$path"
  fi
}

copy_template_if_missing() {
  local name="$1"
  local source="$CORE_TEMPLATES/$name.md"
  local destination="$VAULT/templates/$name.md"
  if [ ! -f "$source" ]; then
    echo "Plantilla CORE faltante: $source" >&2
    exit 2
  fi
  if [ ! -e "$destination" ]; then
    cp "$source" "$destination"
  fi
}

copy_template_if_missing "note"
copy_template_if_missing "memory"

create_if_missing "$VAULT/indexes/README.md" "# Índices

Índices del vault mi-memoria."

create_if_missing "$VAULT/memory/README.md" "# Memoria

Memoria curada consolidada del vault."

echo "Vault inicializado: $VAULT"
