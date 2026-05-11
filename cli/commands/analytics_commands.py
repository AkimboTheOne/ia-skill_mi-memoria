from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


def handle_index(
    *,
    args: Any,
    resolve_optional_vault_path: Callable[[str | None], Path | None],
    resolve_existing_path: Callable[[str, Path | None], Path],
    collect_markdown_files: Callable[[Path], list[Path]],
    parse_frontmatter: Callable[[str], dict[str, str]],
    extract_title: Callable[[str], str],
    now_date: Callable[[], str],
    preview_dir: Path,
    unique_path: Callable[[Path], Path],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        vault = resolve_optional_vault_path(args.vault_path)
        target = resolve_existing_path(args.path, vault)
        files = collect_markdown_files(target)
        titles: dict[str, list[str]] = {}
        by_type: dict[str, int] = {}
        lines = [f"# Index ({now_date()})", "", f"- Path: {target}", f"- Files: {len(files)}", "", "## Notes", ""]
        for file in files:
            text = file.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
            title = fm.get("title", "").strip('"') or extract_title(text)
            note_type = fm.get("type", "note")
            by_type[note_type] = by_type.get(note_type, 0) + 1
            rel = str(file.relative_to(target)) if target.is_dir() else file.name
            lines.append(f"- [[{title}]] ({rel})")
            titles.setdefault(title.lower(), []).append(rel)
        duplicates = {k: v for k, v in titles.items() if len(v) > 1}
        output = Path(args.output) if args.output else unique_path(preview_dir / f"{now_date()}-index.md")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
        emit({"ok": True, "command": "index", "input_path": str(target), "output_path": str(output), "totals": {"files": len(files), "by_type": by_type}, "duplicates": duplicates, "warnings": [], "errors": [], "message": f"Index generado: {output}"}, args.json)
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "index", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2


def handle_timeline(
    *,
    args: Any,
    resolve_existing_path: Callable[[str, Path | None], Path],
    collect_markdown_files: Callable[[Path], list[Path]],
    parse_frontmatter: Callable[[str], dict[str, str]],
    extract_title: Callable[[str], str],
    now_date: Callable[[], str],
    preview_dir: Path,
    unique_path: Callable[[Path], Path],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        target_raw = args.path or args.from_path
        if not target_raw:
            raise ValueError("timeline requiere --path o --from.")
        target = resolve_existing_path(target_raw, None)
        files = collect_markdown_files(target)
        events: list[dict[str, Any]] = []
        for file in files:
            text = file.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
            event_date = fm.get("updated") or fm.get("created")
            inferred = False
            if not event_date:
                name_match = re.match(r"^(\d{4}-\d{2}-\d{2})-", file.name)
                if name_match:
                    event_date = name_match.group(1)
                    inferred = True
                else:
                    event_date = "pending"
                    inferred = True
            events.append({"date": event_date, "inferred": inferred, "source": str(file), "title": fm.get("title", "").strip('"') or extract_title(text)})
        events.sort(key=lambda item: item["date"])
        lines = [f"# Timeline ({now_date()})", ""]
        for event in events:
            mark = " (inferred)" if event["inferred"] else ""
            lines.append(f"- {event['date']}{mark}: {event['title']} -> {event['source']}")
        output = Path(args.output) if args.output else unique_path(preview_dir / f"{now_date()}-timeline.md")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
        emit({"ok": True, "command": "timeline", "input_path": str(target), "output_path": str(output), "events": events, "warnings": [], "errors": [], "message": f"Timeline generado: {output}"}, args.json)
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "timeline", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2


def handle_drift_detection(
    *,
    args: Any,
    resolve_existing_path: Callable[[str, Path | None], Path],
    collect_markdown_files: Callable[[Path], list[Path]],
    parse_frontmatter: Callable[[str], dict[str, str]],
    validate_text: Callable[[str, str | None], dict[str, Any]],
    parse_list_field: Callable[[str], list[str]],
    clean_inline: Callable[[str], str],
    now_date: Callable[[], str],
    preview_dir: Path,
    unique_path: Callable[[Path], Path],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        target = resolve_existing_path(args.path, None)
        files = collect_markdown_files(target)
        issues: dict[str, list[dict[str, Any]]] = {"duplicate_tags": [], "invalid_frontmatter": [], "broken_links": [], "orphan_notes": [], "redundant_aliases": []}
        title_index: dict[str, str] = {}
        for file in files:
            text = file.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
            validation = validate_text(text, file.name)
            if not validation["ok"]:
                issues["invalid_frontmatter"].append({"file": str(file), "errors": validation["errors"]})
            tags = parse_list_field(fm.get("tags", ""))
            lowered_tags = [tag.lower() for tag in tags]
            if len(set(lowered_tags)) != len(lowered_tags):
                issues["duplicate_tags"].append({"file": str(file), "tags": tags})
            aliases = parse_list_field(fm.get("aliases", ""))
            if len(set(alias.lower() for alias in aliases)) != len(aliases):
                issues["redundant_aliases"].append({"file": str(file), "aliases": aliases})
            title = fm.get("title", "").strip('"') or clean_inline(text)
            title_index[title.lower()] = str(file)
        for file in files:
            text = file.read_text(encoding="utf-8")
            links = re.findall(r"\[\[([^\]]+)\]\]", text)
            if not links:
                issues["orphan_notes"].append({"file": str(file)})
            for link in links:
                if clean_inline(link).lower() not in title_index:
                    issues["broken_links"].append({"file": str(file), "link": link})
        output = Path(args.output) if args.output else unique_path(preview_dir / f"{now_date()}-drift-report.md")
        json_output = output.with_suffix(".json")
        lines = [f"# Drift Report ({now_date()})", ""]
        for key, values in issues.items():
            lines.extend([f"## {key}", f"- count: {len(values)}", ""])
        output.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
        json_output.write_text(json.dumps({"ok": True, "command": "drift-detection", "issues": issues}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        emit(
            {
                "ok": True,
                "command": "drift-detection",
                "input_path": str(target),
                "report_paths": {"md": str(output), "json": str(json_output)},
                "issues": issues,
                "warnings": [],
                "errors": [],
                "message": "Drift detection ejecutado correctamente; revisar issues reportados.",
            },
            args.json,
        )
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "drift-detection", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2


def handle_curate(
    *,
    args: Any,
    resolve_optional_vault_path: Callable[[str | None], Path | None],
    resolve_existing_path: Callable[[str, Path | None], Path],
    collect_markdown_files: Callable[[Path], list[Path]],
    safe_read_text: Callable[[Path], str],
    parse_frontmatter: Callable[[str], dict[str, str]],
    strip_existing_frontmatter: Callable[[str], str],
    extract_title: Callable[[str], str],
    parse_list_field: Callable[[str], list[str]],
    now_date: Callable[[], str],
    preview_dir: Path,
    unique_path: Callable[[Path], Path],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        vault = resolve_optional_vault_path(args.vault_path)
        target = resolve_existing_path(args.path, vault)
        files = collect_markdown_files(target)
        issues: dict[str, list[dict[str, Any]]] = {
            "weak_notes": [],
            "potential_duplicates": [],
            "redundant_tags": [],
            "orphan_notes": [],
            "stale_notes": [],
        }
        title_map: dict[str, Path] = {}
        now = datetime.now().date()
        for file in files:
            text = safe_read_text(file)
            fm = parse_frontmatter(text)
            body = strip_existing_frontmatter(text)
            title = (fm.get("title", "").strip('"') or extract_title(body)).strip().lower()
            if len(body.split()) < 25:
                issues["weak_notes"].append({"file": str(file), "reason": "contenido breve"})
            if title in title_map:
                issues["potential_duplicates"].append({"file": str(file), "duplicate_of": str(title_map[title])})
            else:
                title_map[title] = file
            tags = parse_list_field(fm.get("tags", ""))
            lowered = [item.lower() for item in tags]
            if len(set(lowered)) != len(lowered):
                issues["redundant_tags"].append({"file": str(file), "tags": tags})
            links = re.findall(r"\[\[([^\]]+)\]\]", text)
            if not links:
                issues["orphan_notes"].append({"file": str(file)})
            updated = fm.get("updated", "").strip()
            if updated:
                try:
                    age = (now - datetime.strptime(updated, "%Y-%m-%d").date()).days
                    if age > 180:
                        issues["stale_notes"].append({"file": str(file), "days": age})
                except ValueError:
                    pass
        report_md = Path(args.report) if args.report else unique_path(preview_dir / f"{now_date()}-curation-report.md")
        report_json = report_md.with_suffix(".json")
        report_md.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"# Curation Report ({now_date()})", "", f"- Path: {target}", f"- Files: {len(files)}", ""]
        for key, value in issues.items():
            lines.extend([f"## {key}", f"- count: {len(value)}", ""])
        report_md.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
        payload = {
            "ok": True,
            "command": "curate",
            "mode": "preview",
            "input_path": str(target),
            "report_paths": {"md": str(report_md), "json": str(report_json)},
            "issues": issues,
            "warnings": [],
            "errors": [],
            "message": "Curate ejecutado correctamente; plan generado sin mutaciones.",
        }
        report_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        emit(payload, args.json)
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "curate", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2


def handle_publish(
    *,
    args: Any,
    resolve_optional_vault_path: Callable[[str | None], Path | None],
    resolve_existing_path: Callable[[str, Path | None], Path],
    safe_read_text: Callable[[Path], str],
    collect_markdown_files: Callable[[Path], list[Path]],
    workspace: Path,
    unique_path: Callable[[Path], Path],
    now_date: Callable[[], str],
    now_stamp: Callable[[], str],
    remove_private_frontmatter: Callable[[str], str],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        vault = resolve_optional_vault_path(args.vault_path)
        if args.format != "markdown":
            raise ValueError("publish soporta únicamente --format markdown en P4.")
        selected_from_context: list[Path] = []
        source_ref = ""
        if args.context_pack:
            context_pack = resolve_existing_path(args.context_pack, vault)
            source_ref = str(context_pack)
            if context_pack.suffix == ".json":
                payload = json.loads(safe_read_text(context_pack))
                for item in payload.get("sources", []):
                    raw = item.get("file") if isinstance(item, dict) else ""
                    if raw and Path(raw).exists():
                        selected_from_context.append(Path(raw).resolve())
            elif context_pack.suffix == ".md":
                selected_from_context.append(context_pack.resolve())
                sibling_json = context_pack.with_suffix(".json")
                if sibling_json.exists():
                    payload = json.loads(safe_read_text(sibling_json))
                    for item in payload.get("sources", []):
                        raw = item.get("file") if isinstance(item, dict) else ""
                        if raw and Path(raw).exists():
                            selected_from_context.append(Path(raw).resolve())
            else:
                raise ValueError("--context-pack debe ser un archivo .md o .json.")
        target = resolve_existing_path(args.path, vault) if args.path else Path(".").resolve()
        files = collect_markdown_files(target) if args.path else []
        if selected_from_context:
            deduped: list[Path] = []
            seen: set[str] = set()
            for file in selected_from_context:
                key = str(file)
                if key not in seen and file.exists() and file.suffix == ".md":
                    seen.add(key)
                    deduped.append(file)
            files = deduped
        if not files:
            raise ValueError("publish no encontró archivos markdown para exportar.")
        output_root = Path(args.output) if args.output else unique_path(workspace / "exports" / f"{now_date()}-publish-pack")
        files_dir = output_root / "files"
        files_dir.mkdir(parents=True, exist_ok=True)
        copied: list[dict[str, str]] = []
        for file in files:
            destination = files_dir / file.name
            content = safe_read_text(file)
            if args.strip_private:
                content = remove_private_frontmatter(content)
            destination.write_text(content, encoding="utf-8")
            copied.append({"source": str(file), "output": str(destination)})
        manifest = {
            "created": now_stamp(),
            "source_path": str(target),
            "context_pack": source_ref,
            "format": args.format,
            "files": copied,
            "strip_private": bool(args.strip_private),
        }
        (output_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        readme = [
            f"# Publish Pack ({now_date()})",
            "",
            f"- Source: {target}",
            f"- Context pack: {source_ref or '(none)'}",
            f"- Format: {args.format}",
            f"- Files: {len(copied)}",
            f"- Strip private metadata: {'yes' if args.strip_private else 'no'}",
            "",
            "Este paquete es una exportación controlada sin mutar los archivos fuente.",
        ]
        (output_root / "README.md").write_text("\n".join(readme).strip() + "\n", encoding="utf-8")
        emit(
            {
                "ok": True,
                "command": "publish",
                "mode": "export",
                "input_path": str(target),
                "output_path": str(output_root),
                "artifacts": {
                    "readme": str(output_root / "README.md"),
                    "manifest": str(output_root / "manifest.json"),
                    "files_dir": str(files_dir),
                },
                "plan": {"format": args.format, "context_pack": source_ref or None},
                "warnings": [],
                "errors": [],
                "message": f"Paquete publicado en: {output_root}",
            },
            args.json,
        )
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "publish", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2
