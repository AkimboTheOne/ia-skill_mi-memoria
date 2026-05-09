from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "workspace"
PREVIEW_DIR = WORKSPACE / "preview"
VAULT_WORKSPACE = Path("workspace")
VAULT_PREVIEW_DIR = VAULT_WORKSPACE / "preview"
LOG_FILE = ROOT / "logs" / "operations.log"

REQUIRED_FIELDS = ["title", "type", "status", "created", "updated", "tags"]
VALID_TYPES = ["note", "decision", "project", "resource", "area"]
VALID_STATUSES = ["draft", "review", "active", "archived"]
VALID_DESTINATIONS = ["00-inbox", "10-areas", "20-projects", "30-resources", "40-archive"]
STANDARD_SECTIONS = ["Resumen", "Desarrollo", "Relaciones", "Pendientes"]


def now_date() -> str:
    return datetime.now().date().isoformat()


def now_stamp() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def ensure_runtime_dirs() -> None:
    for path in [
        WORKSPACE / "inbox",
        WORKSPACE / "processing",
        PREVIEW_DIR,
        WORKSPACE / "exports",
        ROOT / "logs",
        ROOT / "tmp",
        ROOT / "memory" / "hot",
        ROOT / "memory" / "history",
        ROOT / "memory" / "conventions",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def ensure_vault_workspace_dirs(vault: Path) -> None:
    for path in [
        vault / VAULT_WORKSPACE / "inbox",
        vault / VAULT_WORKSPACE / "processing",
        vault / VAULT_PREVIEW_DIR,
        vault / VAULT_WORKSPACE / "exports",
    ]:
        ensure_inside(vault, path)
        path.mkdir(parents=True, exist_ok=True)


def emit(data: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    if data.get("ok"):
        print(data.get("message", "OK"))
    else:
        print(data.get("message", "Error"), file=sys.stderr)
        for error in data.get("errors", []):
            print(f"- {error}", file=sys.stderr)


def log_operation(action: str, source: str, destination: str, result: str) -> None:
    ensure_runtime_dirs()
    line = f"{now_stamp()}\taction={action}\tsource={source}\tdestination={destination}\tresult={result}\n"
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(line)


def read_text_input(input_path: str | None, inline_text: str | None = None) -> tuple[str, str]:
    if inline_text:
        return inline_text, "inline"
    if input_path:
        path = Path(input_path)
        return path.read_text(encoding="utf-8"), str(path)
    if not sys.stdin.isatty():
        return sys.stdin.read(), "stdin"
    raise ValueError("No se recibió input. Usa --input, texto inline o stdin.")


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return slug or "nota"


def extract_title(text: str) -> str:
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+)$", line.strip())
        if match:
            return clean_inline(match.group(1))
    for line in text.splitlines():
        cleaned = clean_inline(line.strip())
        if cleaned:
            return cleaned[:80]
    return "Nota sin titulo"


def clean_inline(value: str) -> str:
    value = re.sub(r"^[#>*\-\s]+", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def infer_type(text: str, title: str) -> str:
    haystack = f"{title}\n{text}".lower()
    if any(term in haystack for term in ["decisión", "decision", "acuerdo", "se adopta"]):
        return "decision"
    if any(term in haystack for term in ["proyecto", "project", "roadmap"]):
        return "project"
    if any(term in haystack for term in ["área", "area", "responsabilidad"]):
        return "area"
    if any(term in haystack for term in ["referencia", "resource", "recurso", "bibliografía"]):
        return "resource"
    return "note"


def classify(note_type: str, text: str) -> str:
    haystack = text.lower()
    if "archivar" in haystack or "archive" in haystack:
        return "40-archive"
    if note_type == "project":
        return "20-projects"
    if note_type == "area":
        return "10-areas"
    if note_type in {"resource", "decision"}:
        return "30-resources"
    return "00-inbox"


def infer_tags(note_type: str, text: str) -> list[str]:
    tags = ["mi-memoria", note_type]
    lowered = text.lower()
    candidates = {
        "arquitectura": ["arquitectura", "architecture"],
        "decision": ["decisión", "decision", "acuerdo"],
        "proyecto": ["proyecto", "project"],
        "validacion": ["validación", "validacion", "validation"],
    }
    for tag, terms in candidates.items():
        if any(term in lowered for term in terms) and tag not in tags:
            tags.append(tag)
    return tags[:6]


def suggest_wikilinks(text: str, title: str) -> list[str]:
    links: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^#{2,6}\s+(.+)$", line.strip())
        if match:
            candidate = clean_inline(match.group(1))
            if candidate and candidate.lower() != title.lower():
                links.append(candidate)
    words = re.findall(r"\b[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚáéíóúñÑ]{4,}(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚáéíóúñÑ]{3,})?\b", text)
    for word in words:
        candidate = clean_inline(word)
        if candidate and candidate.lower() != title.lower():
            links.append(candidate)
    deduped: list[str] = []
    seen: set[str] = set()
    for link in links:
        key = link.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(link)
    return deduped[:5]


def summarize(text: str) -> str:
    cleaned = " ".join(clean_inline(line) for line in text.splitlines() if clean_inline(line))
    if not cleaned:
        return "Resumen pendiente."
    first_sentence = re.split(r"(?<=[.!?])\s+", cleaned)[0]
    return first_sentence[:240].strip() or "Resumen pendiente."


def strip_existing_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            return text[end + 4 :].lstrip()
    return text.strip()


def format_list(values: list[str]) -> str:
    if not values:
        return "[]"
    return "[" + ", ".join(json.dumps(value, ensure_ascii=False) for value in values) + "]"


def build_frontmatter(metadata: dict[str, Any]) -> str:
    return "\n".join(
        [
            "---",
            f"title: {json.dumps(metadata['title'], ensure_ascii=False)}",
            f"type: {metadata['type']}",
            f"status: {metadata['status']}",
            f"created: {metadata['created']}",
            f"updated: {metadata['updated']}",
            f"tags: {format_list(metadata['tags'])}",
            f"aliases: {format_list(metadata['aliases'])}",
            f"source: {json.dumps(metadata['source'], ensure_ascii=False)}",
            "---",
        ]
    )


def normalize_markdown(text: str, source: str) -> dict[str, Any]:
    body = strip_existing_frontmatter(text)
    title = extract_title(body)
    note_type = infer_type(body, title)
    destination = classify(note_type, body)
    date = now_date()
    filename = f"{date}-{slugify(title)}.md"
    links = suggest_wikilinks(body, title)
    metadata = {
        "title": title,
        "type": note_type,
        "status": "draft",
        "created": date,
        "updated": date,
        "tags": infer_tags(note_type, body),
        "aliases": [],
        "source": source,
    }
    relation_lines = "\n".join(f"- [[{link}]]" for link in links) if links else "- Sin relaciones sugeridas."
    normalized = "\n\n".join(
        [
            build_frontmatter(metadata),
            f"# {title}",
            "## Resumen\n\n" + summarize(body),
            "## Desarrollo\n\n" + (body or "Contenido pendiente."),
            "## Relaciones\n\n" + relation_lines,
            "## Pendientes\n\n- Revisar y consolidar esta nota antes de moverla a estado activo.",
        ]
    )
    validation = validate_text(normalized, filename)
    return {
        "content": normalized + "\n",
        "filename": filename,
        "classification": destination,
        "metadata": metadata,
        "wikilinks": links,
        "validation": validation,
    }


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    raw = text[4:end].strip()
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def validate_text(text: str, filename: str | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    frontmatter = parse_frontmatter(text)
    for field in REQUIRED_FIELDS:
        if not frontmatter.get(field):
            errors.append(f"Falta frontmatter requerido: {field}")
    note_type = frontmatter.get("type", "")
    status = frontmatter.get("status", "")
    if note_type and note_type not in VALID_TYPES:
        errors.append(f"Tipo inválido: {note_type}")
    if status and status not in VALID_STATUSES:
        errors.append(f"Estado inválido: {status}")
    if "tags" in frontmatter and not frontmatter["tags"].startswith("["):
        warnings.append("tags debería declararse como lista YAML inline.")
    for section in STANDARD_SECTIONS:
        if f"## {section}" not in text:
            errors.append(f"Falta sección requerida: {section}")
    if filename and not re.match(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$", Path(filename).name):
        errors.append("Nombre de archivo no cumple yyyy-mm-dd-slug.md")
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "checks": {
            "frontmatter": bool(frontmatter),
            "required_fields": all(frontmatter.get(field) for field in REQUIRED_FIELDS),
            "sections": all(f"## {section}" in text for section in STANDARD_SECTIONS),
            "filename": filename is None or not any("Nombre de archivo" in error for error in errors),
        },
    }


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    index = 2
    while True:
        candidate = parent / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def resolve_vault_path(vault_path: str | None) -> Path:
    raw = vault_path or os.environ.get("MI_MEMORIA_VAULT_PATH")
    if not raw:
        raise ValueError("Falta vault. Usa --vault-path o MI_MEMORIA_VAULT_PATH.")
    vault = Path(raw).expanduser().resolve()
    if not vault.exists() or not vault.is_dir():
        raise ValueError(f"Vault inválido: {vault}")
    return vault


def resolve_optional_vault_path(vault_path: str | None = None) -> Path | None:
    raw = vault_path or os.environ.get("MI_MEMORIA_VAULT_PATH")
    if not raw:
        return None
    return resolve_vault_path(raw)


def ensure_inside(base: Path, target: Path) -> None:
    base_resolved = base.resolve()
    target_resolved = target.resolve()
    if base_resolved != target_resolved and base_resolved not in target_resolved.parents:
        raise ValueError(f"Destino fuera del vault permitido: {target}")


def command_capabilities(args: argparse.Namespace) -> int:
    data = {
        "ok": True,
        "name": "mi-memoria",
        "version": "0.1.0",
        "skills": ["normalize"],
        "commands": ["ask", "explain", "context", "capabilities", "run normalize", "validate", "remember", "apply"],
        "types": VALID_TYPES,
        "statuses": VALID_STATUSES,
        "destinations": VALID_DESTINATIONS,
    }
    emit(data, args.json)
    return 0


def command_explain(args: argparse.Namespace) -> int:
    emit(
        {
            "ok": True,
            "message": "mi-memoria es un runtime local para normalizar, validar y consolidar notas Markdown en un vault externo.",
        },
        args.json,
    )
    return 0


def command_context(args: argparse.Namespace) -> int:
    vault = os.environ.get("MI_MEMORIA_VAULT_PATH", "")
    vault_workspace = ""
    if vault:
        try:
            vault_workspace = str(resolve_vault_path(vault) / VAULT_WORKSPACE)
        except ValueError:
            vault_workspace = ""
    data = {
        "ok": True,
        "runtime": str(ROOT),
        "workspace": str(WORKSPACE),
        "vault": vault,
        "vault_workspace": vault_workspace,
        "language": os.environ.get("MI_MEMORIA_DEFAULT_LANGUAGE", "es"),
    }
    emit(
        data
        if args.json
        else {
            **data,
            "message": (
                f"Runtime: {ROOT}\n"
                f"Workspace runtime: {WORKSPACE}\n"
                f"Vault: {vault or '(no configurado)'}\n"
                f"Workspace vault: {vault_workspace or '(no configurado)'}"
            ),
        },
        args.json,
    )
    return 0


def command_ask(args: argparse.Namespace) -> int:
    text = args.text
    lowered = text.lower()
    if any(term in lowered for term in ["normaliza", "organiza", "clasifica", "nota estructurada", "markdown"]):
        normalized = normalize_markdown(text, "ask")
        ensure_runtime_dirs()
        vault = resolve_optional_vault_path()
        if vault:
            ensure_vault_workspace_dirs(vault)
            destination = unique_path(vault / VAULT_PREVIEW_DIR / normalized["filename"])
        else:
            destination = unique_path(PREVIEW_DIR / normalized["filename"])
        destination.write_text(normalized["content"], encoding="utf-8")
        log_operation("ask.normalize.preview", "inline", str(destination), "ok")
        emit(
            {
                "ok": True,
                "message": f"Preview generado: {destination}",
                "output_path": str(destination),
                "classification": normalized["classification"],
                "validation": normalized["validation"],
            },
            args.json,
        )
        return 0
    emit({"ok": True, "message": "No se detectó una acción automática. Usa run normalize, validate o remember."}, args.json)
    return 0


def command_run(args: argparse.Namespace) -> int:
    if args.skill != "normalize":
        emit({"ok": False, "message": f"Skill no soportado: {args.skill}", "errors": ["Solo normalize existe en v0.1."]}, args.json)
        return 2
    if args.preview and args.write:
        emit({"ok": False, "message": "Usa solo uno: --preview o --write.", "errors": ["Modo ambiguo."]}, args.json)
        return 2
    if not args.preview and not args.write:
        emit({"ok": False, "message": "Debes usar --preview o --write.", "errors": ["Modo de escritura no especificado."]}, args.json)
        return 2
    try:
        text, source = read_text_input(args.input)
        normalized = normalize_markdown(text, source)
        ensure_runtime_dirs()
        if args.preview:
            vault = resolve_optional_vault_path(args.vault_path)
            if vault:
                ensure_vault_workspace_dirs(vault)
                output = unique_path(vault / VAULT_PREVIEW_DIR / normalized["filename"])
            else:
                output = unique_path(PREVIEW_DIR / normalized["filename"])
            proposed = Path(normalized["classification"]) / normalized["filename"]
            mode = "preview"
        else:
            vault = resolve_vault_path(args.vault_path)
            output = unique_path(vault / normalized["classification"] / normalized["filename"])
            ensure_inside(vault, output)
            output.parent.mkdir(parents=True, exist_ok=True)
            proposed = output.relative_to(vault)
            mode = "write"
        output.write_text(normalized["content"], encoding="utf-8")
        log_operation(f"normalize.{mode}", source, str(output), "ok")
        data = {
            "ok": True,
            "command": "run normalize",
            "mode": mode,
            "input": source,
            "output_path": str(output),
            "proposed_vault_path": str(proposed),
            "filename": normalized["filename"],
            "classification": normalized["classification"],
            "warnings": normalized["validation"]["warnings"],
            "validation": normalized["validation"],
            "message": f"{mode.capitalize()} generado: {output}",
        }
        emit(data, args.json)
        return 0 if normalized["validation"]["ok"] else 1
    except Exception as exc:
        emit({"ok": False, "message": str(exc), "errors": [str(exc)]}, args.json)
        return 2


def command_validate(args: argparse.Namespace) -> int:
    try:
        path = Path(args.input)
        text = path.read_text(encoding="utf-8")
        result = validate_text(text, path.name)
        data = {
            "ok": result["ok"],
            "input": str(path),
            "errors": result["errors"],
            "warnings": result["warnings"],
            "checks": result["checks"],
            "message": "Validación correcta." if result["ok"] else "Validación fallida.",
        }
        emit(data, args.json)
        return 0 if result["ok"] else 1
    except Exception as exc:
        emit({"ok": False, "input": args.input, "errors": [str(exc)], "warnings": [], "checks": {}, "message": str(exc)}, args.json)
        return 2


def command_remember(args: argparse.Namespace) -> int:
    summary = clean_inline(args.summary)
    if not summary:
        emit({"ok": False, "message": "La memoria requiere --summary no vacío.", "errors": ["summary vacío"]}, args.json)
        return 2
    ensure_runtime_dirs()
    title = summary[:60]
    filename = f"{now_date()}-{slugify(title)}.md"
    output = unique_path(ROOT / "memory" / "hot" / filename)
    content = "\n".join(
        [
            "---",
            f'title: {json.dumps(title, ensure_ascii=False)}',
            "type: memory",
            "status: active",
            f"created: {now_date()}",
            f"updated: {now_date()}",
            'tags: ["mi-memoria", "memory"]',
            "source: remember",
            "---",
            "",
            f"# {title}",
            "",
            "## Memoria",
            "",
            summary,
            "",
        ]
    )
    output.write_text(content, encoding="utf-8")
    log_operation("remember", "summary", str(output), "ok")
    emit({"ok": True, "output_path": str(output), "message": f"Memoria guardada: {output}"}, args.json)
    return 0


def command_apply(args: argparse.Namespace) -> int:
    try:
        source = Path(args.input).resolve()
        vault = resolve_vault_path(args.vault_path)
        preview_root = PREVIEW_DIR.resolve()
        vault_preview_root = (vault / VAULT_PREVIEW_DIR).resolve()
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mi-memoria", description="Runtime local de skills para Markdown/Obsidian.")
    sub = parser.add_subparsers(dest="command", required=True)

    ask = sub.add_parser("ask")
    ask.add_argument("text")
    ask.add_argument("--json", action="store_true")
    ask.set_defaults(func=command_ask)

    explain = sub.add_parser("explain")
    explain.add_argument("--json", action="store_true")
    explain.set_defaults(func=command_explain)

    context = sub.add_parser("context")
    context.add_argument("--json", action="store_true")
    context.set_defaults(func=command_context)

    capabilities = sub.add_parser("capabilities")
    capabilities.add_argument("--json", action="store_true")
    capabilities.set_defaults(func=command_capabilities)

    run = sub.add_parser("run")
    run.add_argument("skill")
    run.add_argument("--input")
    run.add_argument("--preview", action="store_true")
    run.add_argument("--write", action="store_true")
    run.add_argument("--vault-path")
    run.add_argument("--json", action="store_true")
    run.set_defaults(func=command_run)

    validate = sub.add_parser("validate")
    validate.add_argument("--input", required=True)
    validate.add_argument("--json", action="store_true")
    validate.set_defaults(func=command_validate)

    remember = sub.add_parser("remember")
    remember.add_argument("--summary", required=True)
    remember.add_argument("--json", action="store_true")
    remember.set_defaults(func=command_remember)

    apply = sub.add_parser("apply")
    apply.add_argument("--input", required=True)
    apply.add_argument("--vault-path")
    apply.add_argument("--json", action="store_true")
    apply.set_defaults(func=command_apply)

    return parser


def main(argv: list[str] | None = None) -> int:
    ensure_runtime_dirs()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
