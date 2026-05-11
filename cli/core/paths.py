from __future__ import annotations

import os
from pathlib import Path


def resolve_vault_path(vault_path: str | None) -> Path:
    raw = vault_path or os.environ.get("MI_MEMORIA_VAULT_PATH")
    if not raw:
        raise ValueError("Falta vault. Usa --vault-path o MI_MEMORIA_VAULT_PATH.")
    vault = Path(raw).expanduser().resolve()
    if not vault.exists() or not vault.is_dir():
        raise ValueError(f"Vault inválido: {vault}")
    return vault


def resolve_optional_vault_path(vault_path: str | None = None) -> Path | None:
    raw = vault_path or os.environ.get("MI_MEMORIA_VAULT_PATH")
    if not raw:
        return None
    return resolve_vault_path(raw)


def ensure_inside(base: Path, target: Path) -> None:
    base_resolved = base.resolve()
    target_resolved = target.resolve()
    if base_resolved != target_resolved and base_resolved not in target_resolved.parents:
        raise ValueError(f"Destino fuera del vault permitido: {target}")


def resolve_existing_path(raw_path: str, vault: Path | None = None) -> Path:
    path = Path(raw_path)
    if path.exists():
        return path.resolve()
    if vault:
        candidate = (vault / raw_path).resolve()
        if candidate.exists():
            return candidate
    raise ValueError(f"Ruta inválida: {raw_path}")
