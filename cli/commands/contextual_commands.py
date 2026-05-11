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


def handle_query(
    *,
    args: Any,
    resolve_optional_vault_path: Callable[[str | None], Path | None],
    gather_markdown_scope: Callable[[Path, Path | None], tuple[Path, list[Path]]],
    safe_read_text: Callable[[Path], str],
    parse_frontmatter: Callable[[str], dict[str, str]],
    extract_title: Callable[[str], str],
    parse_list_field: Callable[[str], list[str]],
    strip_existing_frontmatter: Callable[[str], str],
    score_query_match: Callable[[str, str], int],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        vault = resolve_optional_vault_path(args.vault_path)
        raw_scope = args.path or "."
        target, files = gather_markdown_scope(Path(raw_scope), vault)
        matches: list[dict[str, Any]] = []
        for file in files:
            text = safe_read_text(file)
            fm = parse_frontmatter(text)
            title = fm.get("title", "").strip('"') or extract_title(text)
            tags = parse_list_field(fm.get("tags", ""))
            fields = {
                "filename": file.name,
                "title": title,
                "tags": " ".join(tags),
                "content": strip_existing_frontmatter(text),
            }
            score = sum(score_query_match(value, args.query) for value in fields.values())
            if score <= 0:
                continue
            snippets = [line.strip() for line in fields["content"].splitlines() if args.query.lower() in line.lower()][:2]
            evidence = snippets or [title]
            matches.append({"file": str(file), "score": score, "title": title, "tags": tags, "evidence": evidence})
        matches.sort(key=lambda item: item["score"], reverse=True)
        limited = matches[: args.limit]
        has_evidence = bool(limited)
        response = {
            "ok": True,
            "command": "query",
            "query": args.query,
            "scope": str(target),
            "results": limited,
            "evidence": [item["file"] for item in limited],
            "inference": (
                "Se encontraron notas relevantes por coincidencia local en nombre/título/tags/contenido."
                if has_evidence
                else "No hay base para inferencias fuertes con el alcance actual."
            ),
            "uncertainty": "" if has_evidence else "No se encontró evidencia suficiente para responder la consulta.",
            "message": "Consulta contextual completada." if has_evidence else "Consulta sin evidencia suficiente.",
        }
        emit(response, args.json)
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "query", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2


def handle_context_build(
    *,
    args: Any,
    ensure_runtime_dirs: Callable[[], None],
    resolve_optional_vault_path: Callable[[str | None], Path | None],
    gather_markdown_scope: Callable[[Path, Path | None], tuple[Path, list[Path]]],
    safe_read_text: Callable[[Path], str],
    parse_frontmatter: Callable[[str], dict[str, str]],
    extract_title: Callable[[str], str],
    strip_existing_frontmatter: Callable[[str], str],
    score_query_match: Callable[[str, str], int],
    summarize: Callable[[str], str],
    now_date: Callable[[], str],
    workspace: Path,
    unique_path: Callable[[Path], Path],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        ensure_runtime_dirs()
        vault = resolve_optional_vault_path(args.vault_path)
        if not args.path and not args.topic:
            raise ValueError("context-build requiere --path o --topic.")
        if args.path:
            target, files = gather_markdown_scope(Path(args.path), vault)
        else:
            target, files = gather_markdown_scope(Path("."), vault)
        selected: list[dict[str, Any]] = []
        topic = (args.topic or "").lower().strip()
        for file in files:
            text = safe_read_text(file)
            fm = parse_frontmatter(text)
            title = fm.get("title", "").strip('"') or extract_title(text)
            body = strip_existing_frontmatter(text)
            reason = "scope"
            if topic:
                score = score_query_match(f"{title}\n{body}", topic)
                if score <= 0:
                    continue
                reason = "topic-match"
            selected.append({"file": str(file), "title": title, "reason": reason, "excerpt": summarize(body)})
        selected = selected[: args.max_files]
        stamp = now_date()
        base = Path(args.output) if args.output else unique_path(workspace / "exports" / f"{stamp}-context-pack.md")
        base.parent.mkdir(parents=True, exist_ok=True)
        json_path = base.with_suffix(".json")
        source_map_path = base.with_name(base.stem + "-source-map.json")
        md_lines = ["# Context Pack", "", f"- Scope: {target}", f"- Topic: {args.topic or '(none)'}", f"- Selected: {len(selected)}", ""]
        for item in selected:
            md_lines.extend([f"## {item['title']}", f"- Source: {item['file']}", f"- Criteria: {item['reason']}", "", item["excerpt"], ""])
        base.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
        payload = {
            "ok": True,
            "command": "context-build",
            "scope": str(target),
            "topic": args.topic,
            "selection_criteria": {"topic": bool(topic), "max_files": args.max_files},
            "sources": selected,
            "artifacts": {"md": str(base), "json": str(json_path), "source_map": str(source_map_path)},
        }
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        source_map_path.write_text(json.dumps({"sources": [{"file": item["file"], "reason": item["reason"]} for item in selected]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        emit({**payload, "message": f"Context pack generado: {base}"}, args.json)
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "context-build", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2
