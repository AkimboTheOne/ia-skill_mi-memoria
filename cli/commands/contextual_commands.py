from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


def session_file(*, session_dir: Path, slugify: Callable[[str], str], name: str) -> Path:
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir / f"{slugify(name)}.json"


def handle_session(
    *,
    args: Any,
    session_dir: Path,
    slugify: Callable[[str], str],
    now_stamp: Callable[[], str],
    resolve_existing_path: Callable[[str], Path],
    safe_read_text: Callable[[Path], str],
    strip_existing_frontmatter: Callable[[str], str],
    summarize: Callable[[str], str],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        if args.session_command == "start":
            payload = {"name": args.name, "created": now_stamp(), "status": "open", "active_files": []}
            path = session_file(session_dir=session_dir, slugify=slugify, name=args.name)
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            emit({"ok": True, "command": "session", "action": "start", "session": payload, "session_file": str(path), "message": "Sesión iniciada."}, args.json)
            return 0
        if not args.name:
            raise ValueError("session requiere --name.")
        path = session_file(session_dir=session_dir, slugify=slugify, name=args.name)
        if not path.exists():
            raise ValueError("Sesión no encontrada. Ejecuta session start.")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if args.session_command == "add":
            target = resolve_existing_path(args.input)
            if str(target) not in payload["active_files"]:
                payload["active_files"].append(str(target))
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            emit({"ok": True, "command": "session", "action": "add", "session_file": str(path), "active_files": payload["active_files"], "message": "Archivo agregado a la sesión."}, args.json)
            return 0
        if args.session_command == "context":
            files = [Path(item) for item in payload["active_files"] if Path(item).exists()]
            context_items = [{"file": str(file), "summary": summarize(strip_existing_frontmatter(safe_read_text(file)))} for file in files]
            emit({"ok": True, "command": "session", "action": "context", "name": args.name, "active_files": payload["active_files"], "context": context_items, "message": "Contexto de sesión generado."}, args.json)
            return 0
        if args.session_command == "close":
            payload["status"] = "closed"
            payload["closed"] = now_stamp()
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            remembered = False
            if args.remember:
                remembered = True
            emit({"ok": True, "command": "session", "action": "close", "name": args.name, "remember_requested": remembered, "memory_persisted": False, "message": "Sesión cerrada. No se persistió memoria automáticamente."}, args.json)
            return 0
        raise ValueError(f"Subcomando no soportado: {args.session_command}")
    except Exception as exc:
        emit({"ok": False, "command": "session", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2
