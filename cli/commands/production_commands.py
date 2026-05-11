from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


def handle_capture(
    *,
    args: Any,
    ensure_runtime_dirs: Callable[[], None],
    resolve_optional_vault_path: Callable[[str | None], Path | None],
    read_text_input: Callable[[str | None, str | None], tuple[str, str]],
    normalize_markdown: Callable[[str, str, Path | None], dict[str, Any]],
    capture_kind_to_type: Callable[[str | None], tuple[str | None, str | None]],
    render_template: Callable[[str, dict[str, Any], dict[str, str]], str],
    resolve_template: Callable[[str, Path | None], dict[str, Any]],
    summarize: Callable[[str], str],
    strip_existing_frontmatter: Callable[[str], str],
    resolve_capture_target: Callable[[str | None, Path | None], Path],
    vault_workspace_name: str,
    ensure_inside: Callable[[Path, Path], None],
    unique_path: Callable[[Path], Path],
    log_operation: Callable[[str, str, str, str], None],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        if not args.text and not args.input:
            raise ValueError("capture requiere --text o --input.")
        ensure_runtime_dirs()
        vault = resolve_optional_vault_path(args.vault_path)
        text, source = read_text_input(args.input, args.text)
        normalized = normalize_markdown(text, source, vault)
        kind_input = args.kind or args.type or normalized["metadata"]["type"]
        capture_kind, mapped_type = capture_kind_to_type(kind_input)
        capture_type = mapped_type or normalized["metadata"]["type"]
        normalized["metadata"]["type"] = capture_type
        normalized["content"] = render_template(
            resolve_template("note", vault)["content"],
            normalized["metadata"],
            {
                "Resumen": summarize(strip_existing_frontmatter(text)),
                "Desarrollo": strip_existing_frontmatter(text) or "Contenido pendiente.",
                "Relaciones": "- Sin relaciones sugeridas.",
                "Pendientes": "- Revisar y consolidar esta captura.",
            },
        )
        target_dir = resolve_capture_target(args.to, vault)
        if vault and (vault / vault_workspace_name).resolve() in target_dir.parents:
            ensure_inside(vault, target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        output = unique_path(target_dir / normalized["filename"])
        output.write_text(normalized["content"], encoding="utf-8")
        log_operation("capture", source, str(output), "ok")
        emit(
            {
                "ok": True,
                "command": "capture",
                "mode": "preview",
                "output_path": str(output),
                "classification": normalized["classification"],
                "capture_kind": capture_kind or capture_type,
                "capture_type": capture_type,
                "warnings": normalized["warnings"] + normalized["validation"]["warnings"],
                "errors": normalized["validation"]["errors"],
                "message": f"Captura creada: {output}",
            },
            args.json,
        )
        return 0 if normalized["validation"]["ok"] else 1
    except Exception as exc:
        emit({"ok": False, "command": "capture", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2


def handle_daily(
    *,
    args: Any,
    ensure_runtime_dirs: Callable[[], None],
    resolve_optional_vault_path: Callable[[str | None], Path | None],
    parse_iso_date: Callable[[str], str],
    now_date: Callable[[], str],
    ensure_vault_workspace_dirs: Callable[[Path], None],
    vault_workspace_name: str,
    ensure_inside: Callable[[Path, Path], None],
    workspace: Path,
    resolve_template: Callable[[str, Path | None], dict[str, Any]],
    core_template_dir: Path,
    render_template: Callable[[str, dict[str, Any], dict[str, str]], str],
    strip_existing_frontmatter: Callable[[str], str],
    summarize: Callable[[str], str],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        ensure_runtime_dirs()
        vault = resolve_optional_vault_path(args.vault_path)
        day = parse_iso_date(args.date) if args.date else now_date()
        if vault:
            ensure_vault_workspace_dirs(vault)
            daily_dir = vault / vault_workspace_name / "daily"
            ensure_inside(vault, daily_dir)
        else:
            daily_dir = workspace / "daily"
        daily_dir.mkdir(parents=True, exist_ok=True)
        daily_path = daily_dir / f"{day}-daily.md"
        created = not daily_path.exists()
        if created:
            metadata = {
                "title": f"Daily {day}",
                "type": "daily",
                "status": "draft",
                "created": day,
                "updated": day,
                "tags": ["mi-memoria", "daily"],
                "aliases": [],
                "source": "daily",
            }
            content = render_template(
                resolve_template("daily" if (core_template_dir / "daily.md").exists() else "note", vault)["content"],
                metadata,
                {
                    "Resumen": "Resumen pendiente.",
                    "Desarrollo": "",
                    "Relaciones": "- Sin relaciones sugeridas.",
                    "Pendientes": "- Revisar y curar al final del día.",
                },
            )
            daily_path.write_text(content, encoding="utf-8")
        if args.append:
            stamp = datetime.now().strftime("%H:%M")
            existing = daily_path.read_text(encoding="utf-8")
            entry = f"- [{stamp}] {args.append.strip()}"
            if "## Desarrollo" in existing:
                existing = existing.replace("## Desarrollo\n\n", f"## Desarrollo\n\n{entry}\n", 1)
            else:
                existing = existing.rstrip() + f"\n\n## Desarrollo\n\n{entry}\n"
            daily_path.write_text(existing, encoding="utf-8")
        summary_text = ""
        if args.summary:
            summary_text = summarize(strip_existing_frontmatter(daily_path.read_text(encoding="utf-8")))
        emit(
            {
                "ok": True,
                "command": "daily",
                "output_path": str(daily_path),
                "created": created,
                "date": day,
                "summary": summary_text,
                "mode": "preview",
                "warnings": [],
                "errors": [],
                "message": f"Daily disponible: {daily_path}",
            },
            args.json,
        )
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "daily", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2


def handle_decision(
    *,
    args: Any,
    resolve_optional_vault_path: Callable[[str | None], Path | None],
    ensure_runtime_dirs: Callable[[], None],
    ensure_vault_workspace_dirs: Callable[[Path], None],
    vault_workspace_name: str,
    ensure_inside: Callable[[Path, Path], None],
    workspace: Path,
    clean_inline: Callable[[str], str],
    now_date: Callable[[], str],
    slugify: Callable[[str], str],
    unique_path: Callable[[Path], Path],
    valid_decision_statuses: list[str],
    core_template_dir: Path,
    resolve_template: Callable[[str, Path | None], dict[str, Any]],
    render_template: Callable[[str, dict[str, Any], dict[str, str]], str],
    session_file: Callable[[str], Path],
    parse_frontmatter: Callable[[str], dict[str, str]],
    safe_read_text: Callable[[Path], str],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        vault = resolve_optional_vault_path(args.vault_path)
        ensure_runtime_dirs()
        if vault:
            ensure_vault_workspace_dirs(vault)
            decisions_dir = vault / vault_workspace_name / "decisions"
            ensure_inside(vault, decisions_dir)
        else:
            decisions_dir = workspace / "decisions"
        decisions_dir.mkdir(parents=True, exist_ok=True)
        if args.decision_command == "new":
            title = clean_inline(args.title)
            if not title:
                raise ValueError("decision new requiere --title.")
            today = now_date()
            filename = f"{today}-decision-{slugify(title)}.md"
            destination = unique_path(decisions_dir / filename)
            metadata = {
                "title": title,
                "type": "decision",
                "status": "draft",
                "created": today,
                "updated": today,
                "tags": ["mi-memoria", "decision"],
                "aliases": [],
                "source": "decision.new",
            }
            decision_status = args.decision_status or "proposed"
            if decision_status not in valid_decision_statuses:
                raise ValueError(f"decision_status inválido: {decision_status}")
            sections = {
                "Contexto": "Contexto pendiente.",
                "Opciones consideradas": "- Opción A\n- Opción B",
                "Decisión tomada": "Decisión pendiente.",
                "Consecuencias": "- Pendiente.",
                "Referencias": "- Pendiente.",
            }
            template_path = core_template_dir / "decision.md"
            content = render_template(
                resolve_template("decision" if template_path.exists() else "note", vault)["content"],
                metadata,
                sections,
            )
            content = content.replace("\n---\n\n", f"\ndecision_status: {decision_status}\n---\n\n", 1)
            destination.write_text(content, encoding="utf-8")
            emit(
                {
                    "ok": True,
                    "command": "decision",
                    "action": "new",
                    "output_path": str(destination),
                    "mode": "preview",
                    "decision_status": decision_status,
                    "warnings": [],
                    "errors": [],
                    "message": f"Decisión creada: {destination}",
                },
                args.json,
            )
            return 0
        if args.decision_command == "from-session":
            session_path = session_file(args.session)
            if not session_path.exists():
                raise ValueError("Sesión no encontrada. Ejecuta session start.")
            payload = json.loads(session_path.read_text(encoding="utf-8"))
            title = f"decision-desde-{slugify(args.session)}"
            today = now_date()
            decision_status = args.decision_status or "proposed"
            if decision_status not in valid_decision_statuses:
                raise ValueError(f"decision_status inválido: {decision_status}")
            destination = unique_path(decisions_dir / f"{today}-{title}.md")
            files = [Path(item) for item in payload.get("active_files", []) if Path(item).exists()]
            context_lines = [f"- {item}" for item in files] or ["- Sin archivos activos."]
            content = (
                f"---\n"
                f"title: {json.dumps('Decisión desde sesión: ' + args.session, ensure_ascii=False)}\n"
                f"type: decision\n"
                f"status: draft\n"
                f"created: {today}\n"
                f"updated: {today}\n"
                f"decision_status: {decision_status}\n"
                f"tags: [\"mi-memoria\", \"decision\", \"session\"]\n"
                f"aliases: []\n"
                f"source: {json.dumps(str(session_path), ensure_ascii=False)}\n"
                f"---\n\n"
                f"# Decisión desde sesión: {args.session}\n\n"
                f"## Contexto\n\n" + "\n".join(context_lines) + "\n\n"
                f"## Opciones consideradas\n\n- Pendiente.\n\n"
                f"## Decisión tomada\n\nPendiente.\n\n"
                f"## Consecuencias\n\n- Pendiente.\n\n"
                f"## Referencias\n\n- {session_path}\n"
            )
            destination.write_text(content, encoding="utf-8")
            emit(
                {
                    "ok": True,
                    "command": "decision",
                    "action": "from-session",
                    "output_path": str(destination),
                    "session": str(session_path),
                    "decision_status": decision_status,
                    "warnings": [],
                    "errors": [],
                    "message": f"Decisión creada desde sesión: {destination}",
                },
                args.json,
            )
            return 0
        if args.decision_command == "list":
            items = sorted(decisions_dir.glob("*.md"))
            resolved_items: list[dict[str, str]] = []
            for item in items:
                fm = parse_frontmatter(safe_read_text(item))
                resolved_items.append(
                    {
                        "path": str(item),
                        "title": fm.get("title", "").strip('"') or item.stem,
                        "status": fm.get("status", ""),
                        "decision_status": fm.get("decision_status", "proposed"),
                    }
                )
            emit(
                {
                    "ok": True,
                    "command": "decision",
                    "action": "list",
                    "count": len(items),
                    "items": resolved_items,
                    "warnings": [],
                    "errors": [],
                    "message": f"Decisiones listadas: {len(items)}",
                },
                args.json,
            )
            return 0
        raise ValueError(f"Subcomando no soportado: {args.decision_command}")
    except Exception as exc:
        emit({"ok": False, "command": "decision", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2
