from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def handle_run_normalize(
    *,
    args: Any,
    ensure_runtime_dirs: Callable[[], None],
    read_text_input: Callable[[str | None, str | None], tuple[str, str]],
    resolve_optional_vault_path: Callable[[str | None], Path | None],
    normalize_markdown: Callable[[str, str, Path | None], dict[str, Any]],
    ensure_vault_workspace_dirs: Callable[[Path], None],
    unique_path: Callable[[Path], Path],
    vault_preview_dir: Path,
    runtime_preview_dir: Path,
    resolve_vault_path: Callable[[str | None], Path],
    ensure_inside: Callable[[Path, Path], None],
    log_operation: Callable[[str, str, str, str], None],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    if args.skill != "normalize":
        emit({"ok": False, "message": f"Skill no soportado: {args.skill}", "errors": ["Solo normalize existe en v0.1."]}, args.json)
        return 2
    if args.preview and args.write:
        emit({"ok": False, "message": "Usa solo uno: --preview o --write.", "errors": ["Modo ambiguo."]}, args.json)
        return 2
    if not args.preview and not args.write:
        emit({"ok": False, "message": "Debes usar --preview o --write.", "errors": ["Modo de escritura no especificado."]}, args.json)
        return 2
    try:
        ensure_runtime_dirs()
        if args.preview:
            text, source = read_text_input(args.input, None)
            vault = resolve_optional_vault_path(args.vault_path)
            normalized = normalize_markdown(text, source, vault)
            if vault:
                ensure_vault_workspace_dirs(vault)
                output = unique_path(vault / vault_preview_dir / normalized["filename"])
            else:
                output = unique_path(runtime_preview_dir / normalized["filename"])
            proposed = Path(normalized["classification"]) / normalized["filename"]
            mode = "preview"
        else:
            vault = resolve_vault_path(args.vault_path)
            text, source = read_text_input(args.input, None)
            normalized = normalize_markdown(text, source, vault)
            output = unique_path(vault / normalized["classification"] / normalized["filename"])
            ensure_inside(vault, output)
            output.parent.mkdir(parents=True, exist_ok=True)
            proposed = output.relative_to(vault)
            mode = "write"
        output.write_text(normalized["content"], encoding="utf-8")
        log_operation(f"normalize.{mode}", source, str(output), "ok")
        data = {
            "ok": True,
            "command": "run normalize",
            "mode": mode,
            "input": source,
            "output_path": str(output),
            "proposed_vault_path": str(proposed),
            "filename": normalized["filename"],
            "classification": normalized["classification"],
            "template": normalized["template"],
            "warnings": normalized["warnings"] + normalized["validation"]["warnings"],
            "validation": normalized["validation"],
            "message": f"{mode.capitalize()} generado: {output}",
        }
        emit(data, args.json)
        return 0 if normalized["validation"]["ok"] else 1
    except Exception as exc:
        emit({"ok": False, "message": str(exc), "errors": [str(exc)]}, args.json)
        return 2


def handle_validate(
    *,
    args: Any,
    validate_text: Callable[[str, str | None], dict[str, Any]],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        path = Path(args.input)
        text = path.read_text(encoding="utf-8")
        result = validate_text(text, path.name)
        data = {
            "ok": result["ok"],
            "input": str(path),
            "errors": result["errors"],
            "warnings": result["warnings"],
            "checks": result["checks"],
            "message": "Validación correcta." if result["ok"] else "Validación fallida.",
        }
        emit(data, args.json)
        return 0 if result["ok"] else 1
    except Exception as exc:
        emit({"ok": False, "input": args.input, "errors": [str(exc)], "warnings": [], "checks": {}, "message": str(exc)}, args.json)
        return 2
