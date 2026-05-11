from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def handle_explain(*, args: Any, emit: Callable[[dict[str, Any], bool], None]) -> int:
    emit(
        {
            "ok": True,
            "message": "mi-memoria es un runtime local para normalizar, validar y consolidar notas Markdown en un vault externo.",
        },
        args.json,
    )
    return 0


def handle_context(
    *,
    args: Any,
    runtime_root: Path,
    workspace: Path,
    vault_workspace_name: str,
    resolve_vault_path: Callable[[str | None], Path],
    env_get: Callable[[str, str | None], str | None],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    vault = env_get("MI_MEMORIA_VAULT_PATH", "") or ""
    vault_workspace = ""
    if vault:
        try:
            vault_workspace = str(resolve_vault_path(vault) / vault_workspace_name)
        except ValueError:
            vault_workspace = ""
    data = {
        "ok": True,
        "runtime": str(runtime_root),
        "workspace": str(workspace),
        "vault": vault,
        "vault_workspace": vault_workspace,
        "language": env_get("MI_MEMORIA_DEFAULT_LANGUAGE", "es") or "es",
    }
    emit(
        data
        if args.json
        else {
            **data,
            "message": (
                f"Runtime: {runtime_root}\n"
                f"Workspace runtime: {workspace}\n"
                f"Vault: {vault or '(no configurado)'}\n"
                f"Workspace vault: {vault_workspace or '(no configurado)'}"
            ),
        },
        args.json,
    )
    return 0
