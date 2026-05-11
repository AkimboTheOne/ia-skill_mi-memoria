from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

from cli.commands.capabilities_commands import handle_capabilities
from cli.commands.contextual_commands import (
    handle_context_build,
    handle_query,
    handle_session,
    session_file as contextual_session_file,
)
from cli.commands.normalize_commands import handle_run_normalize, handle_validate
from cli.commands.production_commands import handle_capture, handle_daily, handle_decision
from cli.commands.quality_commands import handle_classify, handle_link, handle_review, handle_summarize
from cli.commands.runtime_commands import handle_ask, handle_context, handle_explain
from cli.commands.upgrade_commands import handle_upgrade
from cli.commands.template_commands import (
    handle_template_apply,
    handle_template_generate,
    handle_template_list,
    handle_template_show,
    handle_template_sync,
    handle_template_validate,
)
from cli.infra.git_tools import run_git_command as infra_run_git_command
from cli.infra.telemetry import append_operation_logs
from cli.services.template_sync import sync_templates_safe


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "workspace"
PREVIEW_DIR = WORKSPACE / "preview"
TEMPLATE_PREVIEW_DIR = PREVIEW_DIR / "templates"
VAULT_WORKSPACE = Path("workspace")
VAULT_PREVIEW_DIR = VAULT_WORKSPACE / "preview"
LOG_FILE = ROOT / "logs" / "operations.log"
LOG_JSONL_FILE = ROOT / "logs" / "operations.jsonl"
CORE_TEMPLATE_DIR = ROOT / "skills" / "core" / "templates"

REQUIRED_FIELDS = ["title", "type", "status", "created", "updated", "tags"]
VALID_TYPES = ["note", "decision", "project", "resource", "area", "memory", "daily"]
VALID_STATUSES = ["draft", "review", "active", "archived"]
VALID_DECISION_STATUSES = ["proposed", "accepted", "superseded", "deprecated"]
VALID_CAPTURE_KINDS = ["idea", "reference", "note", "decision", "project", "resource", "area", "memory", "daily"]
VALID_DESTINATIONS = ["00-inbox", "10-areas", "20-projects", "30-resources", "40-archive"]
STANDARD_SECTIONS = ["Resumen", "Desarrollo", "Relaciones", "Pendientes"]
REMEMBER_TYPES = ["decision", "convention", "learning", "constraint", "taxonomy"]
SESSION_DIR = ROOT / "tmp" / "sessions"
SKILL_MANIFEST_PATH = ROOT / "docs" / "skill-manifest.json"


def core_template_warning(note_type: str) -> str:
    return (
        f"No existe vault/templates/{note_type}.md; se usó la plantilla CORE por defecto. "
        "Ejecuta scripts/skill_setup.sh para restaurar plantillas base o crea tu propia plantilla en el vault."
    )


def now_date() -> str:
    return datetime.now().date().isoformat()


def now_stamp() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def parse_iso_date(raw: str) -> str:
    parsed = datetime.strptime(raw, "%Y-%m-%d")
    return parsed.date().isoformat()


def capture_kind_to_type(raw_kind: str | None) -> tuple[str | None, str | None]:
    if not raw_kind:
        return None, None
    kind = clean_inline(raw_kind).lower()
    mapping = {"idea": "note", "reference": "resource"}
    if kind in mapping:
        return kind, mapping[kind]
    if kind in VALID_TYPES:
        return kind, kind
    raise ValueError(f"Tipo de captura inválido: {raw_kind}")


def ensure_runtime_dirs() -> None:
    for path in [
        WORKSPACE / "inbox",
        WORKSPACE / "processing",
        PREVIEW_DIR,
        TEMPLATE_PREVIEW_DIR,
        WORKSPACE / "exports",
        ROOT / "logs",
        ROOT / "tmp",
        ROOT / "memory" / "hot",
        ROOT / "memory" / "history",
        ROOT / "memory" / "conventions",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def resolve_template(note_type: str, vault: Path | None = None) -> dict[str, Any]:
    filename = f"{note_type}.md"
    if vault:
        vault_template = vault / "templates" / filename
        if vault_template.is_file():
            return {
                "source": "vault",
                "path": str(vault_template),
                "content": vault_template.read_text(encoding="utf-8"),
                "warnings": [],
            }
    core_template = CORE_TEMPLATE_DIR / filename
    if core_template.is_file():
        warnings = [core_template_warning(note_type)] if vault else []
        return {
            "source": "core",
            "path": str(core_template),
            "content": core_template.read_text(encoding="utf-8"),
            "warnings": warnings,
        }
    raise ValueError(f"Plantilla CORE no disponible para tipo: {note_type}")


def list_template_files(path: Path) -> list[dict[str, str]]:
    if not path.is_dir():
        return []
    templates: list[dict[str, str]] = []
    for template in sorted(path.glob("*.md")):
        templates.append({"name": template.stem, "path": str(template)})
    return templates


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
    append_operation_logs(
        text_log_path=LOG_FILE,
        jsonl_log_path=LOG_JSONL_FILE,
        timestamp=now_stamp(),
        action=action,
        source=source,
        destination=destination,
        result=result,
    )


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


def render_template(content: str, metadata: dict[str, Any], sections: dict[str, str]) -> str:
    body = strip_existing_frontmatter(content)
    frontmatter = build_frontmatter(metadata)
    title = metadata["title"]
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if re.match(r"^#\s+", line):
            lines[index] = f"# {title}"
            break
    else:
        lines.insert(0, f"# {title}")
    rendered_body = "\n".join(lines).strip()
    for section, value in sections.items():
        replacement = f"## {section}\n\n{value.strip()}"
        pattern = re.compile(rf"## {re.escape(section)}(?:\n.*?)(?=\n## |\Z)", re.DOTALL)
        if pattern.search(rendered_body):
            rendered_body = pattern.sub(replacement, rendered_body)
        else:
            rendered_body = f"{rendered_body}\n\n{replacement}".strip()
    return f"{frontmatter}\n\n{rendered_body}\n"


def normalize_markdown(text: str, source: str, vault: Path | None = None) -> dict[str, Any]:
    body = strip_existing_frontmatter(text)
    title = extract_title(body)
    note_type = infer_type(body, title)
    template = resolve_template(note_type if note_type in {"note", "memory"} else "note", vault)
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
    normalized = render_template(
        template["content"],
        metadata,
        {
            "Resumen": summarize(body),
            "Desarrollo": body or "Contenido pendiente.",
            "Relaciones": relation_lines,
            "Pendientes": "- Revisar y consolidar esta nota antes de moverla a estado activo.",
        },
    )
    validation = validate_text(normalized, filename)
    return {
        "content": normalized + "\n",
        "filename": filename,
        "classification": destination,
        "metadata": metadata,
        "wikilinks": links,
        "template": {
            "type": note_type if note_type in {"note", "memory"} else "note",
            "source": template["source"],
            "path": template["path"],
        },
        "warnings": template["warnings"],
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
    if note_type == "memory":
        if "## Memoria" not in text:
            errors.append("Falta sección requerida: Memoria")
    else:
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
            "sections": "## Memoria" in text
            if note_type == "memory"
            else all(f"## {section}" in text for section in STANDARD_SECTIONS),
            "filename": filename is None or not any("Nombre de archivo" in error for error in errors),
        },
    }


def parse_template_context(text: str, source_name: str = "") -> dict[str, Any]:
    data: dict[str, Any] = {
        "title": "",
        "type": "",
        "status": "",
        "tags": [],
        "sections": [],
    }
    if source_name.endswith((".yaml", ".yml")):
        current_list: str | None = None
        for raw_line in text.splitlines():
            line = raw_line.rstrip()
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("- ") and current_list:
                data[current_list].append(clean_inline(stripped[2:]))
                continue
            if ":" in stripped:
                key, value = stripped.split(":", 1)
                key = key.strip().lower()
                value = value.strip().strip("\"'")
                if key in {"title", "type", "status"}:
                    data[key] = value
                    current_list = None
                elif key in {"tags", "sections"}:
                    current_list = key
                    if value.startswith("[") and value.endswith("]"):
                        data[key] = [
                            clean_inline(item.strip().strip("\"'"))
                            for item in value[1:-1].split(",")
                            if clean_inline(item.strip().strip("\"'"))
                        ]
                        current_list = None
                    elif value:
                        data[key] = [clean_inline(value)]
        return data

    frontmatter = parse_frontmatter(text)
    data["title"] = frontmatter.get("title", "").strip('"')
    data["type"] = frontmatter.get("type", "")
    data["status"] = frontmatter.get("status", "")
    tags = frontmatter.get("tags", "")
    if tags.startswith("[") and tags.endswith("]"):
        data["tags"] = [
            clean_inline(item.strip().strip("\"'"))
            for item in tags[1:-1].split(",")
            if clean_inline(item.strip().strip("\"'"))
        ]
    sections = re.findall(r"^##\s+(.+)$", strip_existing_frontmatter(text), flags=re.MULTILINE)
    data["sections"] = [clean_inline(section) for section in sections if clean_inline(section)]
    if not data["title"]:
        data["title"] = extract_title(strip_existing_frontmatter(text))
    return data


def sections_from_description(description: str) -> list[str]:
    lowered = description.lower()
    if any(term in lowered for term in ["log", "registro", "cronolog", "evento"]):
        return ["Registro", "Observaciones"]
    if any(term in lowered for term in ["cliente", "crm", "venta", "comercial"]):
        return ["Resumen", "Datos clave", "Interacciones", "Pendientes"]
    if any(term in lowered for term in ["proyecto", "roadmap"]):
        return ["Resumen", "Objetivos", "Avance", "Riesgos", "Pendientes"]
    return ["Resumen", "Desarrollo", "Relaciones", "Pendientes"]


def build_template_content(
    name: str,
    note_type: str,
    input_text: str | None = None,
    input_name: str = "",
    description: str | None = None,
) -> dict[str, Any]:
    context = parse_template_context(input_text, input_name) if input_text is not None else {}
    title = clean_inline(str(context.get("title") or name.replace("-", " ").title()))
    resolved_type = clean_inline(str(context.get("type") or note_type))
    status = clean_inline(str(context.get("status") or ("active" if name == "log" else "draft")))
    tags = context.get("tags") or ["mi-memoria", slugify(name)]
    sections = context.get("sections") or sections_from_description(description or name)
    if description and input_text is not None and "Contexto" not in sections:
        sections = [*sections, "Contexto"]
    metadata = {
        "title": title,
        "type": resolved_type,
        "status": status,
        "created": "",
        "updated": "",
        "tags": tags,
        "aliases": [],
        "source": "template.generate",
    }
    body_lines = [f"# {title}", ""]
    for section in sections:
        body_lines.extend([f"## {section}", ""])
        if section == "Contexto" and description:
            body_lines.extend([description.strip(), ""])
    content = build_frontmatter(metadata) + "\n\n" + "\n".join(body_lines).rstrip() + "\n"
    validation = validate_template_text(content, f"{slugify(name)}.md")
    return {
        "content": content,
        "template": {"name": slugify(name), "type": resolved_type, "source": "generated"},
        "warnings": [],
        "validation": validation,
    }


def validate_template_text(text: str, filename: str | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    frontmatter = parse_frontmatter(text)
    for field in REQUIRED_FIELDS:
        if field not in frontmatter:
            errors.append(f"Falta frontmatter requerido: {field}")
    note_type = frontmatter.get("type", "")
    status = frontmatter.get("status", "")
    if note_type and note_type not in VALID_TYPES:
        errors.append(f"Tipo inválido: {note_type}")
    if status and status not in VALID_STATUSES:
        errors.append(f"Estado inválido: {status}")
    sections = re.findall(r"^##\s+.+$", strip_existing_frontmatter(text), flags=re.MULTILINE)
    if not sections:
        errors.append("Falta al menos una sección de template.")
    if filename and not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$", Path(filename).name):
        errors.append("Nombre de template no cumple slug.md")
    if "tags" in frontmatter and frontmatter["tags"] and not frontmatter["tags"].startswith("["):
        warnings.append("tags debería declararse como lista YAML inline.")
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "checks": {
            "frontmatter": bool(frontmatter),
            "required_fields": all(field in frontmatter for field in REQUIRED_FIELDS),
            "sections": bool(sections),
            "filename": filename is None or not any("Nombre de template" in error for error in errors),
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


def run_git_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    # Keep wrapper in main for backwards-compatible test patching.
    return infra_run_git_command(args)


def command_upgrade(args: argparse.Namespace) -> int:
    return handle_upgrade(
        args=args,
        runtime_root=ROOT,
        run_git_command=run_git_command,
        emit=emit,
    )


def collect_markdown_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"Ruta inválida: {path}")
    return sorted(file for file in path.rglob("*.md") if file.is_file())


def parse_list_field(value: str) -> list[str]:
    if value.startswith("[") and value.endswith("]"):
        return [clean_inline(item.strip().strip("\"'")) for item in value[1:-1].split(",") if clean_inline(item.strip().strip("\"'"))]
    return []


def resolve_existing_path(raw_path: str, vault: Path | None = None) -> Path:
    path = Path(raw_path)
    if path.exists():
        return path.resolve()
    if vault:
        candidate = (vault / raw_path).resolve()
        if candidate.exists():
            return candidate
    raise ValueError(f"Ruta inválida: {raw_path}")


def resolve_capture_target(target: str | None, vault: Path | None) -> Path:
    if not target:
        if vault:
            ensure_vault_workspace_dirs(vault)
            return (vault / VAULT_WORKSPACE / "inbox").resolve()
        return (WORKSPACE / "inbox").resolve()
    raw = Path(target)
    if raw.is_absolute():
        if vault:
            vault_workspace_root = (vault / VAULT_WORKSPACE).resolve()
            resolved = raw.resolve()
            if resolved == vault_workspace_root or vault_workspace_root in resolved.parents:
                return resolved
        workspace_root = WORKSPACE.resolve()
        resolved = raw.resolve()
        if resolved == workspace_root or workspace_root in resolved.parents:
            return resolved
        raise ValueError("capture --to solo permite rutas dentro de workspace/ o vault/workspace/.")
    if vault and target.startswith("workspace/"):
        destination = (vault / target).resolve()
        ensure_inside(vault, destination)
        return destination
    destination = (ROOT / target).resolve()
    workspace_root = WORKSPACE.resolve()
    if destination == workspace_root or workspace_root in destination.parents:
        return destination
    raise ValueError("capture --to solo permite rutas relativas dentro de workspace/.")


def remove_private_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---", 4)
    if end == -1:
        return text
    raw = text[4:end].strip()
    filtered: list[str] = []
    for line in raw.splitlines():
        key = line.split(":", 1)[0].strip().lower()
        if key in {"source", "aliases"}:
            continue
        filtered.append(line)
    body = text[end + 4 :].lstrip("\n")
    return "---\n" + "\n".join(filtered).strip() + "\n---\n\n" + body


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def score_query_match(text: str, query: str) -> int:
    lowered = text.lower()
    q = query.lower().strip()
    if not q:
        return 0
    if q == lowered:
        return 100
    if q in lowered:
        return 60
    score = 0
    for token in [item for item in re.split(r"\s+", q) if item]:
        if token in lowered:
            score += 10
    return score


def gather_markdown_scope(path: Path, vault: Path | None = None) -> tuple[Path, list[Path]]:
    target = resolve_existing_path(str(path), vault)
    files = collect_markdown_files(target)
    return target, files


def command_index(args: argparse.Namespace) -> int:
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
        output = Path(args.output) if args.output else unique_path(PREVIEW_DIR / f"{now_date()}-index.md")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
        emit({"ok": True, "command": "index", "input_path": str(target), "output_path": str(output), "totals": {"files": len(files), "by_type": by_type}, "duplicates": duplicates, "warnings": [], "errors": [], "message": f"Index generado: {output}"}, args.json)
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "index", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2


def command_timeline(args: argparse.Namespace) -> int:
    try:
        target_raw = args.path or args.from_path
        if not target_raw:
            raise ValueError("timeline requiere --path o --from.")
        target = resolve_existing_path(target_raw)
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
        output = Path(args.output) if args.output else unique_path(PREVIEW_DIR / f"{now_date()}-timeline.md")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
        emit({"ok": True, "command": "timeline", "input_path": str(target), "output_path": str(output), "events": events, "warnings": [], "errors": [], "message": f"Timeline generado: {output}"}, args.json)
        return 0
    except Exception as exc:
        emit({"ok": False, "command": "timeline", "warnings": [], "errors": [str(exc)], "message": str(exc)}, args.json)
        return 2


def command_drift_detection(args: argparse.Namespace) -> int:
    try:
        target = resolve_existing_path(args.path)
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
            title = fm.get("title", "").strip('"') or extract_title(text)
            title_index[title.lower()] = str(file)
        for file in files:
            text = file.read_text(encoding="utf-8")
            links = re.findall(r"\[\[([^\]]+)\]\]", text)
            if not links:
                issues["orphan_notes"].append({"file": str(file)})
            for link in links:
                if clean_inline(link).lower() not in title_index:
                    issues["broken_links"].append({"file": str(file), "link": link})
        output = Path(args.output) if args.output else unique_path(PREVIEW_DIR / f"{now_date()}-drift-report.md")
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


def command_capture(args: argparse.Namespace) -> int:
    return handle_capture(
        args=args,
        ensure_runtime_dirs=ensure_runtime_dirs,
        resolve_optional_vault_path=resolve_optional_vault_path,
        read_text_input=read_text_input,
        normalize_markdown=normalize_markdown,
        capture_kind_to_type=capture_kind_to_type,
        render_template=render_template,
        resolve_template=resolve_template,
        summarize=summarize,
        strip_existing_frontmatter=strip_existing_frontmatter,
        resolve_capture_target=resolve_capture_target,
        vault_workspace_name=str(VAULT_WORKSPACE),
        ensure_inside=ensure_inside,
        unique_path=unique_path,
        log_operation=log_operation,
        emit=emit,
    )


def command_daily(args: argparse.Namespace) -> int:
    return handle_daily(
        args=args,
        ensure_runtime_dirs=ensure_runtime_dirs,
        resolve_optional_vault_path=resolve_optional_vault_path,
        parse_iso_date=parse_iso_date,
        now_date=now_date,
        ensure_vault_workspace_dirs=ensure_vault_workspace_dirs,
        vault_workspace_name=str(VAULT_WORKSPACE),
        ensure_inside=ensure_inside,
        workspace=WORKSPACE,
        resolve_template=resolve_template,
        core_template_dir=CORE_TEMPLATE_DIR,
        render_template=render_template,
        strip_existing_frontmatter=strip_existing_frontmatter,
        summarize=summarize,
        emit=emit,
    )


def command_decision(args: argparse.Namespace) -> int:
    return handle_decision(
        args=args,
        resolve_optional_vault_path=resolve_optional_vault_path,
        ensure_runtime_dirs=ensure_runtime_dirs,
        ensure_vault_workspace_dirs=ensure_vault_workspace_dirs,
        vault_workspace_name=str(VAULT_WORKSPACE),
        ensure_inside=ensure_inside,
        workspace=WORKSPACE,
        clean_inline=clean_inline,
        now_date=now_date,
        slugify=slugify,
        unique_path=unique_path,
        valid_decision_statuses=VALID_DECISION_STATUSES,
        core_template_dir=CORE_TEMPLATE_DIR,
        resolve_template=resolve_template,
        render_template=render_template,
        session_file=session_file,
        parse_frontmatter=parse_frontmatter,
        safe_read_text=safe_read_text,
        emit=emit,
    )


def command_curate(args: argparse.Namespace) -> int:
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
        report_md = Path(args.report) if args.report else unique_path(PREVIEW_DIR / f"{now_date()}-curation-report.md")
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


def command_publish(args: argparse.Namespace) -> int:
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
        output_root = Path(args.output) if args.output else unique_path(WORKSPACE / "exports" / f"{now_date()}-publish-pack")
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


def command_classify(args: argparse.Namespace) -> int:
    return handle_classify(
        args=args,
        parse_frontmatter=parse_frontmatter,
        infer_type=infer_type,
        strip_existing_frontmatter=strip_existing_frontmatter,
        extract_title=extract_title,
        classify=classify,
        emit=emit,
    )


def command_review(args: argparse.Namespace) -> int:
    return handle_review(
        args=args,
        collect_markdown_files=collect_markdown_files,
        validate_text=validate_text,
        ensure_runtime_dirs=ensure_runtime_dirs,
        now_date=now_date,
        preview_dir=PREVIEW_DIR,
        unique_path=unique_path,
        emit=emit,
    )


def command_link(args: argparse.Namespace) -> int:
    return handle_link(
        args=args,
        extract_title=extract_title,
        suggest_wikilinks=suggest_wikilinks,
        strip_existing_frontmatter=strip_existing_frontmatter,
        emit=emit,
    )


def command_summarize(args: argparse.Namespace) -> int:
    return handle_summarize(
        args=args,
        collect_markdown_files=collect_markdown_files,
        summarize=summarize,
        strip_existing_frontmatter=strip_existing_frontmatter,
        now_date=now_date,
        preview_dir=PREVIEW_DIR,
        unique_path=unique_path,
        emit=emit,
    )


def command_query(args: argparse.Namespace) -> int:
    return handle_query(
        args=args,
        resolve_optional_vault_path=resolve_optional_vault_path,
        gather_markdown_scope=gather_markdown_scope,
        safe_read_text=safe_read_text,
        parse_frontmatter=parse_frontmatter,
        extract_title=extract_title,
        parse_list_field=parse_list_field,
        strip_existing_frontmatter=strip_existing_frontmatter,
        score_query_match=score_query_match,
        emit=emit,
    )


def command_context_build(args: argparse.Namespace) -> int:
    return handle_context_build(
        args=args,
        ensure_runtime_dirs=ensure_runtime_dirs,
        resolve_optional_vault_path=resolve_optional_vault_path,
        gather_markdown_scope=gather_markdown_scope,
        safe_read_text=safe_read_text,
        parse_frontmatter=parse_frontmatter,
        extract_title=extract_title,
        strip_existing_frontmatter=strip_existing_frontmatter,
        score_query_match=score_query_match,
        summarize=summarize,
        now_date=now_date,
        workspace=WORKSPACE,
        unique_path=unique_path,
        emit=emit,
    )


def session_file(name: str) -> Path:
    return contextual_session_file(session_dir=SESSION_DIR, slugify=slugify, name=name)


def command_session(args: argparse.Namespace) -> int:
    return handle_session(
        args=args,
        session_dir=SESSION_DIR,
        slugify=slugify,
        now_stamp=now_stamp,
        resolve_existing_path=lambda raw: resolve_existing_path(raw),
        safe_read_text=safe_read_text,
        strip_existing_frontmatter=strip_existing_frontmatter,
        summarize=summarize,
        emit=emit,
    )


def command_capabilities(args: argparse.Namespace) -> int:
    return handle_capabilities(
        args=args,
        manifest_path=SKILL_MANIFEST_PATH,
        maturity="p4-stable",
        valid_types=VALID_TYPES,
        valid_decision_statuses=VALID_DECISION_STATUSES,
        valid_capture_kinds=VALID_CAPTURE_KINDS,
        valid_statuses=VALID_STATUSES,
        valid_destinations=VALID_DESTINATIONS,
        emit=emit,
    )


def command_explain(args: argparse.Namespace) -> int:
    return handle_explain(args=args, emit=emit)


def command_context(args: argparse.Namespace) -> int:
    return handle_context(
        args=args,
        runtime_root=ROOT,
        workspace=WORKSPACE,
        vault_workspace_name=str(VAULT_WORKSPACE),
        resolve_vault_path=resolve_vault_path,
        env_get=os.environ.get,
        emit=emit,
    )


def command_ask(args: argparse.Namespace) -> int:
    return handle_ask(
        args=args,
        normalize_markdown=normalize_markdown,
        ensure_runtime_dirs=ensure_runtime_dirs,
        resolve_optional_vault_path=resolve_optional_vault_path,
        ensure_vault_workspace_dirs=ensure_vault_workspace_dirs,
        unique_path=unique_path,
        vault_preview_dir=VAULT_PREVIEW_DIR,
        runtime_preview_dir=PREVIEW_DIR,
        log_operation=log_operation,
        emit=emit,
    )


def command_run(args: argparse.Namespace) -> int:
    return handle_run_normalize(
        args=args,
        ensure_runtime_dirs=ensure_runtime_dirs,
        read_text_input=read_text_input,
        resolve_optional_vault_path=resolve_optional_vault_path,
        normalize_markdown=normalize_markdown,
        ensure_vault_workspace_dirs=ensure_vault_workspace_dirs,
        unique_path=unique_path,
        vault_preview_dir=VAULT_PREVIEW_DIR,
        runtime_preview_dir=PREVIEW_DIR,
        resolve_vault_path=resolve_vault_path,
        ensure_inside=ensure_inside,
        log_operation=log_operation,
        emit=emit,
    )


def command_validate(args: argparse.Namespace) -> int:
    return handle_validate(
        args=args,
        validate_text=validate_text,
        emit=emit,
    )


def command_template_list(args: argparse.Namespace) -> int:
    return handle_template_list(
        args=args,
        list_template_files=list_template_files,
        core_template_dir=CORE_TEMPLATE_DIR,
        resolve_vault_path=resolve_vault_path,
        emit=emit,
    )


def command_template_show(args: argparse.Namespace) -> int:
    return handle_template_show(
        args=args,
        resolve_template=resolve_template,
        resolve_vault_path=resolve_vault_path,
        emit=emit,
    )


def command_template_generate(args: argparse.Namespace) -> int:
    return handle_template_generate(
        args=args,
        build_template_content=build_template_content,
        ensure_runtime_dirs=ensure_runtime_dirs,
        template_preview_dir=TEMPLATE_PREVIEW_DIR,
        unique_path=unique_path,
        slugify=slugify,
        log_operation=log_operation,
        emit=emit,
    )


def command_template_validate(args: argparse.Namespace) -> int:
    return handle_template_validate(
        args=args,
        validate_template_text=validate_template_text,
        emit=emit,
    )


def command_template_apply(args: argparse.Namespace) -> int:
    return handle_template_apply(
        args=args,
        template_preview_dir=TEMPLATE_PREVIEW_DIR,
        validate_template_text=validate_template_text,
        resolve_vault_path=resolve_vault_path,
        ensure_inside=ensure_inside,
        log_operation=log_operation,
        emit=emit,
    )


def command_template_sync(args: argparse.Namespace) -> int:
    return handle_template_sync(
        args=args,
        resolve_vault_path=resolve_vault_path,
        ensure_inside=ensure_inside,
        preview_dir=PREVIEW_DIR,
        unique_path=unique_path,
        now_date=now_date,
        core_template_dir=CORE_TEMPLATE_DIR,
        sync_templates_safe=sync_templates_safe,
        emit=emit,
    )


def command_remember(args: argparse.Namespace) -> int:
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
            template = resolve_template("memory")
            output = unique_path(ROOT / "memory" / "hot" / filename)
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
        content = render_template(
            template["content"],
            metadata,
            {
                "Memoria": summary,
            },
        )
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


def command_archive(args: argparse.Namespace) -> int:
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

    upgrade = sub.add_parser("upgrade")
    upgrade.add_argument("--json", action="store_true")
    upgrade.set_defaults(func=command_upgrade)

    capture = sub.add_parser("capture")
    capture.add_argument("--text")
    capture.add_argument("--input")
    capture.add_argument("--type")
    capture.add_argument("--kind")
    capture.add_argument("--to")
    capture.add_argument("--vault-path")
    capture.add_argument("--json", action="store_true")
    capture.set_defaults(func=command_capture)

    daily = sub.add_parser("daily")
    daily.add_argument("--date")
    daily.add_argument("--append")
    daily.add_argument("--summary", action="store_true")
    daily.add_argument("--vault-path")
    daily.add_argument("--json", action="store_true")
    daily.set_defaults(func=command_daily)

    decision = sub.add_parser("decision")
    decision_sub = decision.add_subparsers(dest="decision_command", required=True)

    decision_new = decision_sub.add_parser("new")
    decision_new.add_argument("--title", required=True)
    decision_new.add_argument("--decision-status", choices=VALID_DECISION_STATUSES, default="proposed")
    decision_new.add_argument("--vault-path")
    decision_new.add_argument("--json", action="store_true")
    decision_new.set_defaults(func=command_decision)

    decision_from_session = decision_sub.add_parser("from-session")
    decision_from_session.add_argument("--session", required=True)
    decision_from_session.add_argument("--decision-status", choices=VALID_DECISION_STATUSES, default="proposed")
    decision_from_session.add_argument("--vault-path")
    decision_from_session.add_argument("--json", action="store_true")
    decision_from_session.set_defaults(func=command_decision)

    decision_list = decision_sub.add_parser("list")
    decision_list.add_argument("--vault-path")
    decision_list.add_argument("--json", action="store_true")
    decision_list.set_defaults(func=command_decision)

    classify_cmd = sub.add_parser("classify")
    classify_cmd.add_argument("--input", required=True)
    classify_cmd.add_argument("--json", action="store_true")
    classify_cmd.set_defaults(func=command_classify)

    review = sub.add_parser("review")
    review.add_argument("--input")
    review.add_argument("--path")
    review.add_argument("--json", action="store_true")
    review.set_defaults(func=command_review)

    link = sub.add_parser("link")
    link.add_argument("--input", required=True)
    link.add_argument("--preview", action="store_true")
    link.add_argument("--json", action="store_true")
    link.set_defaults(func=command_link)

    summarize_cmd = sub.add_parser("summarize")
    summarize_cmd.add_argument("--input")
    summarize_cmd.add_argument("--path")
    summarize_cmd.add_argument("--output")
    summarize_cmd.add_argument("--json", action="store_true")
    summarize_cmd.set_defaults(func=command_summarize)

    query_cmd = sub.add_parser("query")
    query_cmd.add_argument("query")
    query_cmd.add_argument("--path")
    query_cmd.add_argument("--vault-path")
    query_cmd.add_argument("--limit", type=int, default=10)
    query_cmd.add_argument("--json", action="store_true")
    query_cmd.set_defaults(func=command_query)

    context_build_cmd = sub.add_parser("context-build")
    context_build_cmd.add_argument("--topic")
    context_build_cmd.add_argument("--path")
    context_build_cmd.add_argument("--output")
    context_build_cmd.add_argument("--vault-path")
    context_build_cmd.add_argument("--max-files", type=int, default=10)
    context_build_cmd.add_argument("--json", action="store_true")
    context_build_cmd.set_defaults(func=command_context_build)

    session_cmd = sub.add_parser("session")
    session_sub = session_cmd.add_subparsers(dest="session_command", required=True)

    session_start = session_sub.add_parser("start")
    session_start.add_argument("--name", required=True)
    session_start.add_argument("--json", action="store_true")
    session_start.set_defaults(func=command_session)

    session_add = session_sub.add_parser("add")
    session_add.add_argument("--name", required=True)
    session_add.add_argument("--input", required=True)
    session_add.add_argument("--json", action="store_true")
    session_add.set_defaults(func=command_session)

    session_context = session_sub.add_parser("context")
    session_context.add_argument("--name", required=True)
    session_context.add_argument("--json", action="store_true")
    session_context.set_defaults(func=command_session)

    session_close = session_sub.add_parser("close")
    session_close.add_argument("--name", required=True)
    session_close.add_argument("--remember", action="store_true")
    session_close.add_argument("--json", action="store_true")
    session_close.set_defaults(func=command_session)

    index_cmd = sub.add_parser("index")
    index_cmd.add_argument("--path", required=True)
    index_cmd.add_argument("--output")
    index_cmd.add_argument("--vault-path")
    index_cmd.add_argument("--json", action="store_true")
    index_cmd.set_defaults(func=command_index)

    timeline_cmd = sub.add_parser("timeline")
    timeline_cmd.add_argument("--path")
    timeline_cmd.add_argument("--from", dest="from_path")
    timeline_cmd.add_argument("--output")
    timeline_cmd.add_argument("--json", action="store_true")
    timeline_cmd.set_defaults(func=command_timeline)

    drift_cmd = sub.add_parser("drift-detection")
    drift_cmd.add_argument("--path", required=True)
    drift_cmd.add_argument("--output")
    drift_cmd.add_argument("--json", action="store_true")
    drift_cmd.set_defaults(func=command_drift_detection)

    curate = sub.add_parser("curate")
    curate.add_argument("--path", required=True)
    curate.add_argument("--report")
    curate.add_argument("--vault-path")
    curate.add_argument("--json", action="store_true")
    curate.set_defaults(func=command_curate)

    publish = sub.add_parser("publish")
    publish.add_argument("--path")
    publish.add_argument("--context-pack")
    publish.add_argument("--format", default="markdown")
    publish.add_argument("--output")
    publish.add_argument("--strip-private", action="store_true")
    publish.add_argument("--vault-path")
    publish.add_argument("--json", action="store_true")
    publish.set_defaults(func=command_publish)

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

    template = sub.add_parser("template")
    template_sub = template.add_subparsers(dest="template_command", required=True)

    template_list = template_sub.add_parser("list")
    template_list.add_argument("--vault-path")
    template_list.add_argument("--json", action="store_true")
    template_list.set_defaults(func=command_template_list)

    template_show = template_sub.add_parser("show")
    template_show.add_argument("--name", required=True)
    template_show.add_argument("--vault-path")
    template_show.add_argument("--json", action="store_true")
    template_show.set_defaults(func=command_template_show)

    template_generate = template_sub.add_parser("generate")
    template_generate.add_argument("--name", required=True)
    template_generate.add_argument("--type", choices=VALID_TYPES, default="note")
    template_generate.add_argument("--input")
    template_generate.add_argument("--description")
    template_generate.add_argument("--preview", action="store_true")
    template_generate.add_argument("--json", action="store_true")
    template_generate.set_defaults(func=command_template_generate)

    template_validate = template_sub.add_parser("validate")
    template_validate.add_argument("--input", required=True)
    template_validate.add_argument("--json", action="store_true")
    template_validate.set_defaults(func=command_template_validate)

    template_apply = template_sub.add_parser("apply")
    template_apply.add_argument("--input", required=True)
    template_apply.add_argument("--vault-path")
    template_apply.add_argument("--json", action="store_true")
    template_apply.set_defaults(func=command_template_apply)

    template_sync = template_sub.add_parser("sync")
    template_sync.add_argument("--vault-path", required=True)
    template_sync.add_argument("--report")
    template_sync.add_argument("--json", action="store_true")
    template_sync.set_defaults(func=command_template_sync)

    remember = sub.add_parser("remember")
    remember.add_argument("--summary")
    remember.add_argument("--input")
    remember.add_argument("--type", choices=REMEMBER_TYPES, default="learning")
    remember.add_argument("--scope", choices=["vault", "runtime"], default="vault")
    remember.add_argument("--vault-path")
    remember.add_argument("--json", action="store_true")
    remember.set_defaults(func=command_remember)

    apply = sub.add_parser("apply")
    apply.add_argument("--input", required=True)
    apply.add_argument("--vault-path")
    apply.add_argument("--json", action="store_true")
    apply.set_defaults(func=command_apply)

    archive = sub.add_parser("archive")
    archive.add_argument("--input", required=True)
    archive_mode = archive.add_mutually_exclusive_group(required=True)
    archive_mode.add_argument("--preview", action="store_true")
    archive_mode.add_argument("--apply", action="store_true")
    archive.add_argument("--vault-path")
    archive.add_argument("--json", action="store_true")
    archive.set_defaults(func=command_archive)

    return parser


def main(argv: list[str] | None = None) -> int:
    ensure_runtime_dirs()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
