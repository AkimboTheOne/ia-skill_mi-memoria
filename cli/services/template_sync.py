from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Callable


def sync_templates_safe(
    *,
    core_templates_dir: Path,
    vault_templates_dir: Path,
    report_md_path: Path,
    date_fn: Callable[[], str],
) -> dict[str, Any]:
    core_templates = sorted(core_templates_dir.glob("*.md"))
    if not core_templates:
        raise ValueError("No se encontraron plantillas CORE para sincronizar.")

    vault_templates_dir.mkdir(parents=True, exist_ok=True)
    added: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    missing: list[str] = []
    outdated: list[dict[str, str]] = []

    for core_template in core_templates:
        destination = vault_templates_dir / core_template.name
        if not destination.exists():
            shutil.copy2(core_template, destination)
            added.append({"name": core_template.stem, "source": str(core_template), "destination": str(destination)})
            missing.append(core_template.name)
            continue
        core_content = core_template.read_text(encoding="utf-8")
        vault_content = destination.read_text(encoding="utf-8")
        if core_content != vault_content:
            outdated.append({"name": core_template.stem, "core": str(core_template), "vault": str(destination)})
        skipped.append({"name": core_template.stem, "reason": "exists"})

    lines = [
        f"# Template Sync Report ({date_fn()})",
        "",
        f"- Vault templates: {vault_templates_dir}",
        f"- Core templates: {len(core_templates)}",
        f"- Added: {len(added)}",
        f"- Skipped(existing): {len(skipped)}",
        f"- Outdated(detected): {len(outdated)}",
        "",
        "## Added",
        *(f"- {item['name']}: {item['destination']}" for item in added),
        "",
        "## Outdated",
        *(f"- {item['name']}: vault difiere de CORE ({item['vault']})" for item in outdated),
    ]
    report_md_path.parent.mkdir(parents=True, exist_ok=True)
    report_md_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")

    return {
        "mode": "safe-sync",
        "summary": {
            "core_templates": len(core_templates),
            "added": len(added),
            "skipped_existing": len(skipped),
            "outdated_detected": len(outdated),
        },
        "added": added,
        "missing_before_sync": missing,
        "skipped": skipped,
        "outdated": outdated,
        "warnings": ["Modo seguro: no se sobrescribieron plantillas existentes del vault."],
    }
