from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any, Callable


def handle_template_list(
    *,
    args: Any,
    list_template_files: Callable[[Path], list[dict[str, str]]],
    core_template_dir: Path,
    resolve_vault_path: Callable[[str | None], Path],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    vault = resolve_vault_path(args.vault_path) if args.vault_path or os.environ.get("MI_MEMORIA_VAULT_PATH") else None
    core = list_template_files(core_template_dir)
    vault_templates = list_template_files(vault / "templates") if vault else []
    emit(
        {
            "ok": True,
            "command": "template list",
            "core": core,
            "vault": vault_templates,
            "message": f"Templates CORE: {len(core)}; vault: {len(vault_templates)}",
        },
        args.json,
    )
    return 0


def handle_template_show(
    *,
    args: Any,
    resolve_template: Callable[[str, Path | None], dict[str, Any]],
    resolve_vault_path: Callable[[str | None], Path],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        vault = resolve_vault_path(args.vault_path) if args.vault_path or os.environ.get("MI_MEMORIA_VAULT_PATH") else None
        template = resolve_template(args.name, vault)
        emit(
            {
                "ok": True,
                "command": "template show",
                "template": {
                    "name": args.name,
                    "source": template["source"],
                    "path": template["path"],
                },
                "content": template["content"],
                "warnings": template["warnings"],
                "message": f"Template efectivo: {template['path']}",
            },
            args.json,
        )
        return 0
    except Exception as exc:
        emit({"ok": False, "message": str(exc), "errors": [str(exc)]}, args.json)
        return 2


def handle_template_generate(
    *,
    args: Any,
    build_template_content: Callable[..., dict[str, Any]],
    ensure_runtime_dirs: Callable[[], None],
    template_preview_dir: Path,
    unique_path: Callable[[Path], Path],
    slugify: Callable[[str], str],
    log_operation: Callable[[str, str, str, str], None],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    if not args.preview:
        emit({"ok": False, "message": "template generate requiere --preview.", "errors": ["Modo preview requerido."]}, args.json)
        return 2
    try:
        input_text = None
        input_name = ""
        if args.input:
            input_path = Path(args.input)
            input_text = input_path.read_text(encoding="utf-8")
            input_name = input_path.name
        generated = build_template_content(args.name, args.type, input_text, input_name, args.description)
        ensure_runtime_dirs()
        output = unique_path(template_preview_dir / f"{slugify(args.name)}.md")
        output.write_text(generated["content"], encoding="utf-8")
        log_operation("template.generate.preview", args.input or "inline", str(output), "ok")
        emit(
            {
                "ok": True,
                "command": "template generate",
                "mode": "preview",
                "output_path": str(output),
                "template": generated["template"],
                "warnings": generated["warnings"] + generated["validation"]["warnings"],
                "validation": generated["validation"],
                "message": f"Preview de template generado: {output}",
            },
            args.json,
        )
        return 0 if generated["validation"]["ok"] else 1
    except Exception as exc:
        emit({"ok": False, "message": str(exc), "errors": [str(exc)]}, args.json)
        return 2


def handle_template_validate(
    *,
    args: Any,
    validate_template_text: Callable[[str, str | None], dict[str, Any]],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        path = Path(args.input)
        result = validate_template_text(path.read_text(encoding="utf-8"), path.name)
        emit(
            {
                "ok": result["ok"],
                "command": "template validate",
                "input": str(path),
                "errors": result["errors"],
                "warnings": result["warnings"],
                "checks": result["checks"],
                "message": "Template válido." if result["ok"] else "Template inválido.",
            },
            args.json,
        )
        return 0 if result["ok"] else 1
    except Exception as exc:
        emit({"ok": False, "message": str(exc), "errors": [str(exc)]}, args.json)
        return 2


def handle_template_apply(
    *,
    args: Any,
    template_preview_dir: Path,
    validate_template_text: Callable[[str, str | None], dict[str, Any]],
    resolve_vault_path: Callable[[str | None], Path],
    ensure_inside: Callable[[Path, Path], None],
    log_operation: Callable[[str, str, str, str], None],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        source = Path(args.input).resolve()
        preview_root = template_preview_dir.resolve()
        if preview_root != source and preview_root not in source.parents:
            raise ValueError("template apply solo acepta archivos dentro de workspace/preview/templates.")
        if source.suffix != ".md" or not source.is_file():
            raise ValueError("El input de template apply debe ser un archivo Markdown existente.")
        text = source.read_text(encoding="utf-8")
        validation = validate_template_text(text, source.name)
        if not validation["ok"]:
            emit(
                {
                    "ok": False,
                    "command": "template apply",
                    "input": str(source),
                    "errors": validation["errors"],
                    "warnings": validation["warnings"],
                    "checks": validation["checks"],
                    "message": "No se aplicó porque el template no valida.",
                },
                args.json,
            )
            return 1
        vault = resolve_vault_path(args.vault_path)
        destination = vault / "templates" / source.name
        ensure_inside(vault, destination)
        if destination.exists():
            raise ValueError(f"Template ya existe y no se sobrescribe: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        log_operation("template.apply", str(source), str(destination), "ok")
        emit(
            {
                "ok": True,
                "command": "template apply",
                "input": str(source),
                "output_path": str(destination),
                "validation": validation,
                "message": f"Template aplicado al vault: {destination}",
            },
            args.json,
        )
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "template apply", "message": str(exc), "errors": [str(exc)]}, args.json)
        return 2


def handle_template_sync(
    *,
    args: Any,
    resolve_vault_path: Callable[[str | None], Path],
    ensure_inside: Callable[[Path, Path], None],
    preview_dir: Path,
    unique_path: Callable[[Path], Path],
    now_date: Callable[[], str],
    core_template_dir: Path,
    sync_templates_safe: Callable[..., dict[str, Any]],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        vault = resolve_vault_path(args.vault_path)
        vault_templates_dir = vault / "templates"
        ensure_inside(vault, vault_templates_dir)
        report_md = Path(args.report) if args.report else unique_path(preview_dir / f"{now_date()}-template-sync-report.md")
        report_json = report_md.with_suffix(".json")

        sync_data = sync_templates_safe(
            core_templates_dir=core_template_dir,
            vault_templates_dir=vault_templates_dir,
            report_md_path=report_md,
            date_fn=now_date,
        )

        payload = {
            "ok": True,
            "command": "template sync",
            "mode": sync_data["mode"],
            "vault_path": str(vault),
            "artifacts": {"md": str(report_md), "json": str(report_json)},
            "summary": sync_data["summary"],
            "added": sync_data["added"],
            "missing_before_sync": sync_data["missing_before_sync"],
            "skipped": sync_data["skipped"],
            "outdated": sync_data["outdated"],
            "errors": [],
            "warnings": sync_data["warnings"],
            "message": "Sincronización de plantillas completada en modo seguro.",
        }
        report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        emit(payload, args.json)
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "template sync", "message": str(exc), "errors": [str(exc)]}, args.json)
        return 2
