from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from cli.core.metadata import build_capabilities_payload


def handle_capabilities(
    *,
    args: Any,
    manifest_path: Path,
    maturity: str,
    valid_types: list[str],
    valid_decision_statuses: list[str],
    valid_capture_kinds: list[str],
    valid_statuses: list[str],
    valid_destinations: list[str],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        data = build_capabilities_payload(
            manifest_path=manifest_path,
            maturity=maturity,
            valid_types=valid_types,
            valid_decision_statuses=valid_decision_statuses,
            valid_capture_kinds=valid_capture_kinds,
            valid_statuses=valid_statuses,
            valid_destinations=valid_destinations,
        )
        emit(data, args.json)
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "capabilities", "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2
