from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def execute_upgrade(
    *,
    runtime_root: Path,
    runner: Callable[[list[str]], Any],
) -> tuple[int, dict[str, Any]]:
    runtime = str(runtime_root)
    command = ["git", "-C", runtime, "pull", "--ff-only"]
    try:
        git_dir = runner(["git", "-C", runtime, "rev-parse", "--git-dir"])
        if git_dir.returncode != 0:
            return 2, {
                "ok": False,
                "command": "upgrade",
                "runtime": runtime,
                "stdout": git_dir.stdout,
                "stderr": git_dir.stderr,
                "returncode": git_dir.returncode,
                "message": "No se pudo actualizar: el runtime no está dentro de un repositorio Git.",
            }

        remote = runner(["git", "-C", runtime, "remote", "get-url", "origin"])
        if remote.returncode != 0:
            return 2, {
                "ok": False,
                "command": "upgrade",
                "runtime": runtime,
                "stdout": remote.stdout,
                "stderr": remote.stderr,
                "returncode": remote.returncode,
                "message": "No se pudo actualizar: el runtime no tiene remoto origin configurado.",
            }

        result = runner(command)
        ok = result.returncode == 0
        return (0 if ok else 1), {
            "ok": ok,
            "command": "upgrade",
            "runtime": runtime,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "message": "Skill actualizado con git pull --ff-only." if ok else "No se pudo actualizar el skill con git pull --ff-only.",
        }
    except FileNotFoundError as exc:
        return 2, {
            "ok": False,
            "command": "upgrade",
            "runtime": runtime,
            "stdout": "",
            "stderr": str(exc),
            "returncode": 127,
            "message": "No se pudo actualizar: Git no está disponible.",
        }
