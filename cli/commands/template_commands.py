from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


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
