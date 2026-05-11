from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


def handle_classify(
    *,
    args: Any,
    parse_frontmatter: Callable[[str], dict[str, str]],
    infer_type: Callable[[str, str], str],
    strip_existing_frontmatter: Callable[[str], str],
    extract_title: Callable[[str], str],
    classify: Callable[[str, str], str],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        note = Path(args.input)
        text = note.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        fm_type = frontmatter.get("type", "").strip()
        inferred_type = infer_type(strip_existing_frontmatter(text), extract_title(text))
        note_type = fm_type or inferred_type
        proposed = classify(note_type, text)
        from_frontmatter = bool(fm_type)
        confidence = "high" if from_frontmatter else "medium"
        alternatives: list[str] = []
        if not from_frontmatter:
            if note_type == "project":
                alternatives = ["10-areas", "30-resources"]
            elif note_type == "decision":
                alternatives = ["20-projects", "30-resources"]
            elif note_type == "area":
                alternatives = ["20-projects", "30-resources"]
            elif note_type == "resource":
                alternatives = ["00-inbox", "20-projects"]
            else:
                alternatives = ["10-areas", "30-resources"]
        rationale = (
            f"Clasificado por frontmatter type={note_type}."
            if from_frontmatter
            else f"Clasificado por inferencia semántica type={note_type}; revisar alternativas."
        )
        emit(
            {
                "ok": True,
                "command": "classify",
                "input": str(note),
                "proposed_destination": proposed,
                "confidence": confidence,
                "alternatives": alternatives,
                "rationale": rationale,
                "warnings": [],
                "errors": [],
                "message": f"Destino propuesto: {proposed}",
            },
            args.json,
        )
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "classify", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2


def handle_review(
    *,
    args: Any,
    collect_markdown_files: Callable[[Path], list[Path]],
    validate_text: Callable[[str, str | None], dict[str, Any]],
    ensure_runtime_dirs: Callable[[], None],
    now_date: Callable[[], str],
    preview_dir: Path,
    unique_path: Callable[[Path], Path],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        if not args.input and not args.path:
            raise ValueError("review requiere --input o --path.")
        target = Path(args.input) if args.input else Path(args.path)
        files = collect_markdown_files(target)
        issues: list[dict[str, Any]] = []
        checks = {"files": len(files), "valid_files": 0}
        for file in files:
            validation = validate_text(file.read_text(encoding="utf-8"), file.name)
            if validation["ok"]:
                checks["valid_files"] += 1
            else:
                issues.append({"file": str(file), "errors": validation["errors"], "warnings": validation["warnings"]})
        ensure_runtime_dirs()
        stamp = now_date()
        json_report = unique_path(preview_dir / f"{stamp}-review-report.json")
        md_report = unique_path(preview_dir / f"{stamp}-review-report.md")
        payload = {"ok": not issues, "checks": checks, "issues": issues}
        json_report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        lines = [f"# Review Report ({stamp})", "", f"- Files: {checks['files']}", f"- Valid: {checks['valid_files']}", f"- Issues: {len(issues)}", ""]
        for issue in issues:
            lines.append(f"## {issue['file']}")
            for err in issue["errors"]:
                lines.append(f"- ERROR: {err}")
            for warn in issue["warnings"]:
                lines.append(f"- WARN: {warn}")
            lines.append("")
        md_report.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
        emit(
            {
                "ok": not issues,
                "command": "review",
                "checks": checks,
                "issues": issues,
                "report_paths": {"md": str(md_report), "json": str(json_report)},
                "warnings": [],
                "errors": [],
                "message": "Review ejecutado correctamente; revisar issues de calidad.",
            },
            args.json,
        )
        return 0 if not issues else 1
    except Exception as exc:
        emit({"ok": False, "command": "review", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2


def handle_link(
    *,
    args: Any,
    extract_title: Callable[[str], str],
    suggest_wikilinks: Callable[[str, str], list[str]],
    strip_existing_frontmatter: Callable[[str], str],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        note = Path(args.input)
        text = note.read_text(encoding="utf-8")
        title = extract_title(text)
        suggested = suggest_wikilinks(strip_existing_frontmatter(text), title)
        missing = [f"[[{item}]]" for item in suggested]
        emit(
            {
                "ok": True,
                "command": "link",
                "mode": "preview" if args.preview else "analysis",
                "input": str(note),
                "suggested_links": [f"[[{item}]]" for item in suggested],
                "missing_targets": missing,
                "rationale": "Sugerencias por headings y entidades detectadas localmente.",
                "warnings": [],
                "errors": [],
                "message": "Sugerencias de enlaces generadas sin persistencia.",
            },
            args.json,
        )
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "link", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2


def handle_summarize(
    *,
    args: Any,
    collect_markdown_files: Callable[[Path], list[Path]],
    summarize: Callable[[str], str],
    strip_existing_frontmatter: Callable[[str], str],
    now_date: Callable[[], str],
    preview_dir: Path,
    unique_path: Callable[[Path], Path],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        if not args.input and not args.path:
            raise ValueError("summarize requiere --input o --path.")
        if args.input and args.path:
            raise ValueError("Usa solo uno: --input o --path.")
        sources = collect_markdown_files(Path(args.input) if args.input else Path(args.path))
        if not sources:
            raise ValueError("No se encontraron archivos Markdown para resumir.")
        snippets: list[str] = []
        for source in sources[:20]:
            text = source.read_text(encoding="utf-8")
            snippets.append(f"- {source.name}: {summarize(strip_existing_frontmatter(text))}")
        summary_text = "\n".join(snippets)
        output_path = Path(args.output) if args.output else unique_path(preview_dir / f"{now_date()}-summary.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("# Summary\n\n" + summary_text + "\n", encoding="utf-8")
        emit(
            {
                "ok": True,
                "command": "summarize",
                "output_path": str(output_path),
                "sources": [str(item) for item in sources],
                "summary": summary_text,
                "decisions": [],
                "pending_items": [],
                "warnings": [],
                "errors": [],
                "message": f"Resumen generado: {output_path}",
            },
            args.json,
        )
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "summarize", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2
