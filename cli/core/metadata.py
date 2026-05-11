from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cli import __version__

RUNTIME_COMMANDS = [
    "ask",
    "explain",
    "context",
    "capabilities",
    "run normalize",
    "validate",
    "remember",
    "apply",
    "template",
    "upgrade",
    "capture",
    "daily",
    "decision",
    "classify",
    "review",
    "link",
    "summarize",
    "index",
    "timeline",
    "drift-detection",
    "curate",
    "publish",
    "archive",
    "query",
    "context-build",
    "session",
    "template sync",
]


def load_skill_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fallback = path.parent / "docs" / path.name
        if fallback.is_file():
            path = fallback
        else:
            raise ValueError(f"Manifest no encontrado: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Manifest inválido: {exc}") from exc


def build_capabilities_payload(
    *,
    manifest_path: Path,
    maturity: str,
    valid_types: list[str],
    valid_decision_statuses: list[str],
    valid_capture_kinds: list[str],
    valid_statuses: list[str],
    valid_destinations: list[str],
) -> dict[str, Any]:
    manifest = load_skill_manifest(manifest_path)
    command_metadata = manifest.get("command_metadata", {})
    missing_metadata = [item for item in RUNTIME_COMMANDS if item not in command_metadata]
    return {
        "ok": True,
        "name": "mi-memoria",
        "version": __version__,
        "maturity": maturity,
        "skills": ["normalize"],
        "commands": RUNTIME_COMMANDS,
        "types": valid_types,
        "decision_statuses": valid_decision_statuses,
        "capture_kinds": valid_capture_kinds,
        "statuses": valid_statuses,
        "destinations": valid_destinations,
        "llm_manifest": str(manifest_path),
        "command_metadata": command_metadata,
        "metadata_warnings": [f"Comandos sin metadata en manifest: {', '.join(missing_metadata)}"] if missing_metadata else [],
    }
