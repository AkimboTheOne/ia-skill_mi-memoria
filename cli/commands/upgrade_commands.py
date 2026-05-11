from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from cli.services.upgrade_service import execute_upgrade


def handle_upgrade(
    *,
    args: Any,
    runtime_root: Path,
    run_git_command: Callable[[list[str]], Any],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    exit_code, payload = execute_upgrade(runtime_root=runtime_root, runner=run_git_command)
    emit(payload, args.json)
    return exit_code
