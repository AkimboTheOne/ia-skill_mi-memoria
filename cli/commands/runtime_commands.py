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


def handle_ask(
    *,
    args: Any,
    normalize_markdown: Callable[[str, str], dict[str, Any]],
    ensure_runtime_dirs: Callable[[], None],
    resolve_optional_vault_path: Callable[[], Path | None],
    ensure_vault_workspace_dirs: Callable[[Path], None],
    unique_path: Callable[[Path], Path],
    vault_preview_dir: Path,
    runtime_preview_dir: Path,
    log_operation: Callable[[str, str, str, str], None],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    text = args.text
    lowered = text.lower()
    if any(term in lowered for term in ["normaliza", "organiza", "clasifica", "nota estructurada", "markdown"]):
        normalized = normalize_markdown(text, "ask")
        ensure_runtime_dirs()
        vault = resolve_optional_vault_path()
        if vault:
            ensure_vault_workspace_dirs(vault)
            destination = unique_path(vault / vault_preview_dir / normalized["filename"])
        else:
            destination = unique_path(runtime_preview_dir / normalized["filename"])
        destination.write_text(normalized["content"], encoding="utf-8")
        log_operation("ask.normalize.preview", "inline", str(destination), "ok")
        emit(
            {
                "ok": True,
                "message": f"Preview generado: {destination}",
                "output_path": str(destination),
                "classification": normalized["classification"],
                "validation": normalized["validation"],
            },
            args.json,
        )
        return 0
    emit({"ok": True, "message": "No se detectó una acción automática. Usa run normalize, validate o remember."}, args.json)
    return 0
