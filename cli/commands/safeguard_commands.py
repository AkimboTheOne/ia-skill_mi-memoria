from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any, Callable


def handle_remember(
    *,
    args: Any,
    clean_inline: Callable[[str], str],
    summarize: Callable[[str], str],
    strip_existing_frontmatter: Callable[[str], str],
    ensure_runtime_dirs: Callable[[], None],
    now_date: Callable[[], str],
    slugify: Callable[[str], str],
    unique_path: Callable[[Path], Path],
    resolve_template: Callable[[str, Path | None], dict[str, Any]],
    resolve_vault_path: Callable[[str | None], Path],
    ensure_inside: Callable[[Path, Path], None],
    render_template: Callable[[str, dict[str, Any], dict[str, str]], str],
    root: Path,
    log_operation: Callable[[str, str, str, str], None],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    if args.summary:
        summary = clean_inline(args.summary)
        source_ref = "summary"
    elif args.input:
        input_path = Path(args.input)
        summary = summarize(strip_existing_frontmatter(input_path.read_text(encoding="utf-8")))
        source_ref = str(input_path)
    else:
        summary = ""
        source_ref = ""
    if not summary:
        emit({"ok": False, "message": "La memoria requiere --summary no vacío.", "errors": ["summary vacío"]}, args.json)
        return 2
    try:
        ensure_runtime_dirs()
        title = summary[:60]
        filename = f"{now_date()}-{slugify(title)}.md"
        if args.scope == "runtime":
            template = resolve_template("memory", None)
            output = unique_path(root / "memory" / "hot" / filename)
        else:
            vault = resolve_vault_path(args.vault_path)
            template = resolve_template("memory", vault)
            output = unique_path(vault / "memory" / filename)
            ensure_inside(vault, output)
            output.parent.mkdir(parents=True, exist_ok=True)
        metadata = {
            "title": title,
            "type": "memory",
            "status": "active",
            "created": now_date(),
            "updated": now_date(),
            "tags": ["mi-memoria", "memory", args.type],
            "aliases": [],
            "source": "remember",
        }
        content = render_template(template["content"], metadata, {"Memoria": summary})
        if "## Contexto" in content:
            content = content.replace("## Contexto\n\n", f"## Contexto\n\n- Tipo: {args.type}\n- Fuente: {source_ref}\n\n")
        elif "## Memoria" in content:
            content = content.replace("## Memoria\n\n", f"## Memoria\n\n- Tipo: {args.type}\n- Fuente: {source_ref}\n\n")
        output.write_text(content, encoding="utf-8")
        log_operation(f"remember.{args.scope}", "summary", str(output), "ok")
        emit(
            {
                "ok": True,
                "scope": args.scope,
                "output_path": str(output),
                "template": {
                    "type": "memory",
                    "source": template["source"],
                    "path": template["path"],
                },
                "memory_type": args.type,
                "source_ref": source_ref,
                "warnings": template["warnings"],
                "message": f"Memoria guardada: {output}",
            },
            args.json,
        )
        return 0
    except Exception as exc:
        emit({"ok": False, "scope": args.scope, "message": str(exc), "errors": [str(exc)]}, args.json)
        return 2


def handle_archive(
    *,
    args: Any,
    resolve_vault_path: Callable[[str | None], Path],
    resolve_existing_path: Callable[[str, Path | None], Path],
    ensure_inside: Callable[[Path, Path], None],
    log_operation: Callable[[str, str, str, str], None],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        vault = resolve_vault_path(args.vault_path)
        source = resolve_existing_path(args.input, vault)
        ensure_inside(vault, source)
        if source.suffix != ".md" or not source.is_file():
            raise ValueError("archive requiere un archivo .md existente.")
        destination = vault / "40-archive" / source.name
        ensure_inside(vault, destination)
        if destination.exists():
            raise ValueError(f"Destino ya existe: {destination}")
        text = source.read_text(encoding="utf-8")
        links = re.findall(r"\[\[([^\]]+)\]\]", text)
        plan = {"source": str(source), "destination": str(destination), "links_detected": len(links), "warnings": ["Archivar no borra contenido; mueve la nota a 40-archive."]}
        if args.preview:
            emit({"ok": True, "command": "archive", "mode": "preview", "plan": plan, "message": "Plan de archivado generado."}, args.json)
            return 0
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        log_operation("archive.apply", str(source), str(destination), "ok")
        emit({"ok": True, "command": "archive", "mode": "apply", "plan": plan, "output_path": str(destination), "message": f"Nota archivada: {destination}"}, args.json)
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "archive", "errors": [str(exc)], "warnings": [], "message": str(exc)}, args.json)
        return 2


def handle_apply(
    *,
    args: Any,
    resolve_vault_path: Callable[[str | None], Path],
    runtime_preview_dir: Path,
    vault_preview_dir_name: str,
    validate_text: Callable[[str, str | None], dict[str, Any]],
    parse_frontmatter: Callable[[str], dict[str, str]],
    classify: Callable[[str, str], str],
    unique_path: Callable[[Path], Path],
    ensure_inside: Callable[[Path, Path], None],
    log_operation: Callable[[str, str, str, str], None],
    emit: Callable[[dict[str, Any], bool], None],
) -> int:
    try:
        source = Path(args.input).resolve()
        vault = resolve_vault_path(args.vault_path)
        preview_root = runtime_preview_dir.resolve()
        vault_preview_root = (vault / vault_preview_dir_name).resolve()
        source_in_runtime_preview = preview_root == source or preview_root in source.parents
        source_in_vault_preview = vault_preview_root == source or vault_preview_root in source.parents
        if not source_in_runtime_preview and not source_in_vault_preview:
            raise ValueError("apply solo acepta archivos dentro de workspace/preview del runtime o del vault.")
        if source.suffix != ".md" or not source.is_file():
            raise ValueError("El input de apply debe ser un archivo Markdown existente.")
        text = source.read_text(encoding="utf-8")
        validation = validate_text(text, source.name)
        if not validation["ok"]:
            emit(
                {
                    "ok": False,
                    "input": str(source),
                    "errors": validation["errors"],
                    "warnings": validation["warnings"],
                    "checks": validation["checks"],
                    "message": "No se aplicó porque la nota no valida.",
                },
                args.json,
            )
            return 1
        frontmatter = parse_frontmatter(text)
        destination_dir = classify(frontmatter.get("type", "note"), text)
        destination = unique_path(vault / destination_dir / source.name)
        ensure_inside(vault, destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        log_operation("apply", str(source), str(destination), "ok")
        emit(
            {
                "ok": True,
                "input": str(source),
                "output_path": str(destination),
                "proposed_vault_path": str(destination.relative_to(vault)),
                "validation": validation,
                "message": f"Nota aplicada al vault: {destination}",
            },
            args.json,
        )
        return 0
    except Exception as exc:
        emit({"ok": False, "message": str(exc), "errors": [str(exc)]}, args.json)
        return 2
