from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from argparse import Namespace
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from unittest.mock import patch

from cli import main as cli_main


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "mi-memoria"
TEST_TMP = ROOT / "tmp" / "tests"


@contextmanager
def runtime_temp_dir() -> Iterator[Path]:
    TEST_TMP.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=TEST_TMP) as tmp:
        yield Path(tmp)


class MiMemoriaCliTests(unittest.TestCase):
    def run_cli(
        self,
        *args: str,
        check: bool = True,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        subprocess_env = os.environ.copy()
        subprocess_env.pop("MI_MEMORIA_VAULT_PATH", None)
        if env:
            subprocess_env.update(env)
        result = subprocess.run(
            ["python3", str(BIN), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            env=subprocess_env,
        )
        if check and result.returncode != 0:
            self.fail(f"command failed: {result.args}\nstdout={result.stdout}\nstderr={result.stderr}")
        return result

    def test_capabilities_json(self) -> None:
        result = self.run_cli("capabilities", "--json")
        data = json.loads(result.stdout)
        self.assertTrue(data["ok"])
        self.assertIn("normalize", data["skills"])
        self.assertIn("memory", data["types"])
        self.assertIn("template", data["commands"])
        self.assertIn("upgrade", data["commands"])

    def test_upgrade_invokes_scoped_git_pull(self) -> None:
        calls: list[list[str]] = []

        def fake_git(args: list[str]) -> subprocess.CompletedProcess[str]:
            calls.append(args)
            return subprocess.CompletedProcess(args, 0, "ok\n", "")

        with patch.object(cli_main, "run_git_command", side_effect=fake_git), patch("builtins.print") as printed:
            code = cli_main.command_upgrade(Namespace(json=True))

        self.assertEqual(code, 0)
        self.assertEqual(calls[0], ["git", "-C", str(cli_main.ROOT), "rev-parse", "--git-dir"])
        self.assertEqual(calls[1], ["git", "-C", str(cli_main.ROOT), "remote", "get-url", "origin"])
        self.assertEqual(calls[2], ["git", "-C", str(cli_main.ROOT), "pull", "--ff-only"])
        data = json.loads(printed.call_args.args[0])
        self.assertTrue(data["ok"])
        self.assertEqual(data["command"], "upgrade")

    def test_upgrade_reports_git_pull_error(self) -> None:
        def fake_git(args: list[str]) -> subprocess.CompletedProcess[str]:
            if args[-1] == "--git-dir":
                return subprocess.CompletedProcess(args, 0, ".git\n", "")
            if args[-2:] == ["get-url", "origin"]:
                return subprocess.CompletedProcess(args, 0, "git@example.com:repo.git\n", "")
            return subprocess.CompletedProcess(args, 1, "", "fatal: Not possible to fast-forward\n")

        with patch.object(cli_main, "run_git_command", side_effect=fake_git), patch("builtins.print") as printed:
            code = cli_main.command_upgrade(Namespace(json=True))

        self.assertEqual(code, 1)
        data = json.loads(printed.call_args.args[0])
        self.assertFalse(data["ok"])
        self.assertEqual(data["returncode"], 1)
        self.assertIn("fast-forward", data["stderr"])

    def test_upgrade_reports_missing_origin_remote(self) -> None:
        def fake_git(args: list[str]) -> subprocess.CompletedProcess[str]:
            if args[-1] == "--git-dir":
                return subprocess.CompletedProcess(args, 0, ".git\n", "")
            return subprocess.CompletedProcess(args, 2, "", "error: No such remote 'origin'\n")

        with patch.object(cli_main, "run_git_command", side_effect=fake_git), patch("builtins.print") as printed:
            code = cli_main.command_upgrade(Namespace(json=True))

        self.assertEqual(code, 2)
        data = json.loads(printed.call_args.args[0])
        self.assertFalse(data["ok"])
        self.assertIn("remoto origin", data["message"])

    def test_upgrade_reports_non_git_runtime(self) -> None:
        result = subprocess.CompletedProcess(["git"], 128, "", "fatal: not a git repository\n")
        with patch.object(cli_main, "run_git_command", return_value=result), patch("builtins.print") as printed:
            code = cli_main.command_upgrade(Namespace(json=True))

        self.assertEqual(code, 2)
        data = json.loads(printed.call_args.args[0])
        self.assertFalse(data["ok"])
        self.assertIn("repositorio Git", data["message"])

    def test_normalize_preview_and_validate(self) -> None:
        with runtime_temp_dir() as tmp:
            note = tmp / "note.md"
            note.write_text("# Decisión de arquitectura\n\nSe adopta Python estándar.", encoding="utf-8")
            result = self.run_cli("run", "normalize", "--input", str(note), "--preview", "--json")
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            output = Path(data["output_path"])
            self.addCleanup(lambda path=output: path.exists() and path.unlink())
            self.assertTrue(output.exists())
            self.assertEqual(data["mode"], "preview")

            validation = self.run_cli("validate", "--input", str(output), "--json")
            validation_data = json.loads(validation.stdout)
            self.assertTrue(validation_data["ok"])

    def test_write_requires_vault(self) -> None:
        with runtime_temp_dir() as tmp:
            note = tmp / "note.md"
            note.write_text("# Nota\n\nContenido.", encoding="utf-8")
            result = self.run_cli("run", "normalize", "--input", str(note), "--write", "--json", check=False)
            self.assertNotEqual(result.returncode, 0)
            data = json.loads(result.stdout)
            self.assertFalse(data["ok"])

    def test_validate_invalid_markdown(self) -> None:
        with runtime_temp_dir() as tmp:
            invalid = tmp / "invalid.md"
            invalid.write_text("# Sin frontmatter\n", encoding="utf-8")
            result = self.run_cli("validate", "--input", str(invalid), "--json", check=False)
            self.assertEqual(result.returncode, 1)
            data = json.loads(result.stdout)
            self.assertFalse(data["ok"])
            self.assertTrue(data["errors"])

    def setup_vault(self, tmp: str) -> Path:
        vault = Path(tmp) / "vault"
        setup = subprocess.run(
            ["bash", str(ROOT / "scripts" / "skill_setup.sh"), str(vault)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(setup.returncode, 0, setup.stderr)
        return vault.resolve()

    def test_remember_defaults_to_vault(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = self.setup_vault(tmp)
            result = self.run_cli(
                "remember",
                "--summary",
                "Convención aprobada: usar previews antes de apply.",
                "--vault-path",
                str(vault),
                "--json",
            )
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertEqual(data["scope"], "vault")
            output = Path(data["output_path"])
            self.assertTrue(output.exists())
            self.assertEqual(output.parent, vault / "memory")

            validation = self.run_cli("validate", "--input", str(output), "--json")
            validation_data = json.loads(validation.stdout)
            self.assertTrue(validation_data["ok"])

    def test_remember_uses_env_vault(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = self.setup_vault(tmp)
            result = self.run_cli(
                "remember",
                "--summary",
                "Decisión persistente: guardar memoria del proyecto en el vault.",
                "--json",
                env={"MI_MEMORIA_VAULT_PATH": str(vault)},
            )
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertEqual(data["scope"], "vault")
            self.assertEqual(Path(data["output_path"]).parent, vault / "memory")

    def test_remember_uses_core_template_when_vault_template_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = self.setup_vault(tmp)
            (vault / "templates" / "memory.md").unlink()
            result = self.run_cli(
                "remember",
                "--summary",
                "Memoria persistente aun sin plantilla en el vault.",
                "--vault-path",
                str(vault),
                "--json",
            )
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertEqual(data["template"]["source"], "core")
            self.assertTrue(data["warnings"])
            self.assertIn("plantilla CORE", data["warnings"][0])

    def test_remember_prefers_vault_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = self.setup_vault(tmp)
            (vault / "templates" / "memory.md").write_text(
                "---\ntitle:\ntype: memory\nstatus: active\ncreated:\nupdated:\ntags: []\naliases: []\nsource:\n---\n\n# Título\n\n## Memoria\n\n## Contexto local\n",
                encoding="utf-8",
            )
            result = self.run_cli(
                "remember",
                "--summary",
                "Memoria desde plantilla personalizada.",
                "--vault-path",
                str(vault),
                "--json",
            )
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertEqual(data["template"]["source"], "vault")
            output = Path(data["output_path"])
            self.assertIn("## Contexto local", output.read_text(encoding="utf-8"))

    def test_template_list_shows_core_templates(self) -> None:
        result = self.run_cli("template", "list", "--json")
        data = json.loads(result.stdout)
        self.assertTrue(data["ok"])
        core_names = {template["name"] for template in data["core"]}
        self.assertTrue({"note", "memory", "log"}.issubset(core_names))

    def test_template_show_prefers_vault_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = self.setup_vault(tmp)
            (vault / "templates" / "log.md").write_text(
                "---\ntitle:\ntype: note\nstatus: active\ncreated:\nupdated:\ntags: []\naliases: []\nsource:\n---\n\n# Log local\n\n## Registro\n",
                encoding="utf-8",
            )
            result = self.run_cli("template", "show", "--name", "log", "--vault-path", str(vault), "--json")
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertEqual(data["template"]["source"], "vault")
            self.assertIn("# Log local", data["content"])

    def test_template_generate_description_preview(self) -> None:
        result = self.run_cli(
            "template",
            "generate",
            "--name",
            "log-diario",
            "--type",
            "note",
            "--description",
            "Registro diario de eventos",
            "--preview",
            "--json",
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["ok"])
        self.assertEqual(data["command"], "template generate")
        self.assertEqual(data["mode"], "preview")
        output = Path(data["output_path"])
        self.addCleanup(lambda path=output: path.exists() and path.unlink())
        self.assertTrue(output.exists())
        self.assertIn("## Registro", output.read_text(encoding="utf-8"))

    def test_template_generate_input_context_preview(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            context = Path(tmp) / "context.yaml"
            context.write_text(
                "title: Cliente CRM\ntype: note\nstatus: draft\ntags: [crm, cliente]\nsections:\n  - Perfil\n  - Oportunidades\n  - Pendientes\n",
                encoding="utf-8",
            )
            result = self.run_cli(
                "template",
                "generate",
                "--name",
                "cliente-crm",
                "--type",
                "note",
                "--input",
                str(context),
                "--description",
                "Contexto comercial",
                "--preview",
                "--json",
            )
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            output = Path(data["output_path"])
            self.addCleanup(lambda path=output: path.exists() and path.unlink())
            content = output.read_text(encoding="utf-8")
            self.assertIn("# Cliente CRM", content)
            self.assertIn("## Perfil", content)
            self.assertIn("## Contexto", content)

    def test_template_validate_rejects_invalid_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            invalid = Path(tmp) / "invalid.md"
            invalid.write_text("# Sin frontmatter\n", encoding="utf-8")
            result = self.run_cli("template", "validate", "--input", str(invalid), "--json", check=False)
            data = json.loads(result.stdout)
            self.assertFalse(data["ok"])
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(data["errors"])

    def test_template_apply_writes_preview_to_vault(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = self.setup_vault(tmp)
            generated = self.run_cli(
                "template",
                "generate",
                "--name",
                "cliente-crm",
                "--type",
                "note",
                "--description",
                "Cliente CRM",
                "--preview",
                "--json",
            )
            generated_data = json.loads(generated.stdout)
            preview = Path(generated_data["output_path"])
            self.addCleanup(lambda path=preview: path.exists() and path.unlink())
            applied = self.run_cli(
                "template",
                "apply",
                "--input",
                str(preview),
                "--vault-path",
                str(vault),
                "--json",
            )
            applied_data = json.loads(applied.stdout)
            self.assertTrue(applied_data["ok"])
            self.assertTrue((vault / "templates" / preview.name).exists())

    def test_template_apply_does_not_overwrite_existing_template(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = self.setup_vault(tmp)
            generated = self.run_cli(
                "template",
                "generate",
                "--name",
                "log",
                "--type",
                "note",
                "--description",
                "Registro",
                "--preview",
                "--json",
            )
            preview = Path(json.loads(generated.stdout)["output_path"])
            self.addCleanup(lambda path=preview: path.exists() and path.unlink())
            result = self.run_cli(
                "template",
                "apply",
                "--input",
                str(preview),
                "--vault-path",
                str(vault),
                "--json",
                check=False,
            )
            data = json.loads(result.stdout)
            self.assertFalse(data["ok"])
            self.assertIn("ya existe", data["message"])

    def test_remember_runtime_scope(self) -> None:
        result = self.run_cli(
            "remember",
            "--summary",
            "Convención del skill: runtime solo con scope explícito.",
            "--scope",
            "runtime",
            "--json",
        )
        data = json.loads(result.stdout)
        self.assertTrue(data["ok"])
        self.assertEqual(data["scope"], "runtime")
        output = Path(data["output_path"])
        self.addCleanup(lambda path=output: path.exists() and path.unlink())
        self.assertTrue(output.exists())
        self.assertEqual(output.parent, ROOT / "memory" / "hot")

    def test_remember_requires_vault_by_default(self) -> None:
        result = self.run_cli(
            "remember",
            "--summary",
            "Memoria del proyecto requiere vault.",
            "--json",
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertFalse(data["ok"])
        self.assertEqual(data["scope"], "vault")
        self.assertIn("Falta vault", data["message"])

    def test_setup_vault_and_apply(self) -> None:
        with runtime_temp_dir() as tmp:
            vault = self.setup_vault(str(tmp))
            self.assertTrue((vault / "00-inbox").is_dir())
            memory_template = vault / "templates" / "memory.md"
            self.assertTrue(memory_template.is_file())
            self.assertIn("type: memory", memory_template.read_text(encoding="utf-8"))
            log_template = vault / "templates" / "log.md"
            self.assertTrue(log_template.is_file())
            for workspace_dir in ["inbox", "processing", "preview", "exports"]:
                self.assertTrue((vault / "workspace" / workspace_dir).is_dir())
                self.assertTrue((vault / "workspace" / workspace_dir / ".gitkeep").exists())
            self.assertTrue((vault / "workspace" / "README.md").exists())
            note = tmp / "note.md"
            note.write_text("# Proyecto Memoria\n\nProyecto para normalizar notas.", encoding="utf-8")
            preview = self.run_cli("run", "normalize", "--input", str(note), "--preview", "--json")
            preview_data = json.loads(preview.stdout)
            preview_output = Path(preview_data["output_path"])
            self.addCleanup(lambda path=preview_output: path.exists() and path.unlink())
            applied = self.run_cli(
                "apply",
                "--input",
                preview_data["output_path"],
                "--vault-path",
                str(vault),
                "--json",
            )
            applied_data = json.loads(applied.stdout)
            self.assertTrue(applied_data["ok"])
            self.assertTrue(Path(applied_data["output_path"]).exists())

    def test_normalize_write_uses_core_note_template_when_vault_template_is_missing(self) -> None:
        with runtime_temp_dir() as tmp:
            vault = self.setup_vault(str(tmp))
            (vault / "templates" / "note.md").unlink()
            note = tmp / "note.md"
            note.write_text("# Nota simple\n\nContenido.", encoding="utf-8")
            result = self.run_cli(
                "run",
                "normalize",
                "--input",
                str(note),
                "--write",
                "--vault-path",
                str(vault),
                "--json",
            )
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertEqual(data["template"]["source"], "core")
            self.assertTrue(data["warnings"])
            self.assertIn("vault/templates/note.md", data["warnings"][0])

    def test_normalize_write_prefers_vault_note_template(self) -> None:
        with runtime_temp_dir() as tmp:
            vault = self.setup_vault(str(tmp))
            (vault / "templates" / "note.md").write_text(
                "---\ntitle:\ntype: note\nstatus: draft\ncreated:\nupdated:\ntags: []\naliases: []\nsource:\n---\n\n# Título\n\n## Resumen\n\n## Desarrollo\n\n## Relaciones\n\n## Pendientes\n\n## Contexto local\n",
                encoding="utf-8",
            )
            note = tmp / "note.md"
            note.write_text("# Nota con template\n\nContenido.", encoding="utf-8")
            result = self.run_cli(
                "run",
                "normalize",
                "--input",
                str(note),
                "--write",
                "--vault-path",
                str(vault),
                "--json",
            )
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertEqual(data["template"]["source"], "vault")
            output = Path(data["output_path"])
            self.assertIn("## Contexto local", output.read_text(encoding="utf-8"))

    def test_preview_to_vault_workspace_and_apply(self) -> None:
        with runtime_temp_dir() as tmp:
            vault = self.setup_vault(str(tmp))
            note = tmp / "note.md"
            note.write_text("# Decisión visible\n\nSe adopta staging visible en Obsidian.", encoding="utf-8")

            preview = self.run_cli(
                "run",
                "normalize",
                "--input",
                str(note),
                "--preview",
                "--vault-path",
                str(vault),
                "--json",
            )
            preview_data = json.loads(preview.stdout)
            preview_output = Path(preview_data["output_path"])
            self.assertTrue(preview_output.exists())
            self.assertEqual(preview_output.parent.resolve(), (vault / "workspace" / "preview").resolve())

            applied = self.run_cli(
                "apply",
                "--input",
                str(preview_output),
                "--vault-path",
                str(vault),
                "--json",
            )
            applied_data = json.loads(applied.stdout)
            self.assertTrue(applied_data["ok"])
            applied_output = Path(applied_data["output_path"])
            self.assertTrue(applied_output.exists())
            self.assertEqual(applied_output.parent.resolve(), (vault / "30-resources").resolve())

    def test_preview_uses_env_vault_workspace(self) -> None:
        with runtime_temp_dir() as tmp:
            vault = self.setup_vault(str(tmp))
            note = tmp / "note.md"
            note.write_text("# Nota visible\n\nContenido para preview visible.", encoding="utf-8")

            preview = self.run_cli(
                "run",
                "normalize",
                "--input",
                str(note),
                "--preview",
                "--json",
                env={"MI_MEMORIA_VAULT_PATH": str(vault)},
            )
            preview_data = json.loads(preview.stdout)
            preview_output = Path(preview_data["output_path"])
            self.assertTrue(preview_output.exists())
            self.assertEqual(preview_output.parent.resolve(), (vault / "workspace" / "preview").resolve())

    def test_ask_uses_env_vault_workspace(self) -> None:
        with runtime_temp_dir() as tmp:
            vault = self.setup_vault(str(tmp))

            result = self.run_cli(
                "ask",
                "Normaliza esta nota sobre arquitectura",
                "--json",
                env={"MI_MEMORIA_VAULT_PATH": str(vault)},
            )
            data = json.loads(result.stdout)
            output = Path(data["output_path"])
            self.assertTrue(output.exists())
            self.assertEqual(output.parent.resolve(), (vault / "workspace" / "preview").resolve())

    def test_capture_creates_note_in_runtime_workspace_inbox(self) -> None:
        result = self.run_cli("capture", "--text", "Idea rapida para proyecto", "--json")
        data = json.loads(result.stdout)
        self.assertTrue(data["ok"])
        output = Path(data["output_path"])
        self.addCleanup(lambda path=output: path.exists() and path.unlink())
        self.assertTrue(output.exists())
        self.assertEqual(output.parent.resolve(), (ROOT / "workspace" / "inbox").resolve())

    def test_classify_returns_destination_without_moving(self) -> None:
        with runtime_temp_dir() as tmp:
            note = tmp / "2026-01-01-mi-nota.md"
            note.write_text("# Proyecto X\n\nRoadmap y tareas.", encoding="utf-8")
            result = self.run_cli("classify", "--input", str(note), "--json")
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertIn(data["proposed_destination"], cli_main.VALID_DESTINATIONS)
            self.assertTrue(note.exists())

    def test_review_generates_reports(self) -> None:
        with runtime_temp_dir() as tmp:
            note = tmp / "2026-01-01-nota.md"
            note.write_text("# Sin frontmatter\n", encoding="utf-8")
            result = self.run_cli("review", "--input", str(note), "--json", check=False)
            data = json.loads(result.stdout)
            self.assertIn("report_paths", data)
            self.assertTrue(Path(data["report_paths"]["md"]).exists())
            self.assertTrue(Path(data["report_paths"]["json"]).exists())

    def test_link_returns_suggestions_without_modifying_source(self) -> None:
        with runtime_temp_dir() as tmp:
            note = tmp / "note.md"
            content = "# Nota Principal\n\n## Arquitectura Local\n"
            note.write_text(content, encoding="utf-8")
            result = self.run_cli("link", "--input", str(note), "--preview", "--json")
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertIn("suggested_links", data)
            self.assertEqual(note.read_text(encoding="utf-8"), content)

    def test_summarize_generates_traceable_summary(self) -> None:
        with runtime_temp_dir() as tmp:
            note = tmp / "note.md"
            note.write_text("# Nota\n\nContenido con una decision.", encoding="utf-8")
            result = self.run_cli("summarize", "--input", str(note), "--json")
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertTrue(Path(data["output_path"]).exists())
            self.assertEqual(len(data["sources"]), 1)

    def test_index_generates_report_without_mutation(self) -> None:
        with runtime_temp_dir() as tmp:
            note = tmp / "2026-01-01-a.md"
            note.write_text("# Nota A\n\nContenido.", encoding="utf-8")
            result = self.run_cli("index", "--path", str(tmp), "--json")
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertTrue(Path(data["output_path"]).exists())
            self.assertTrue(note.exists())

    def test_timeline_generates_events(self) -> None:
        with runtime_temp_dir() as tmp:
            note = tmp / "2026-01-01-evento.md"
            note.write_text("# Evento\n\nContenido.", encoding="utf-8")
            result = self.run_cli("timeline", "--path", str(tmp), "--json")
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertTrue(data["events"])

    def test_drift_detection_generates_md_and_json(self) -> None:
        with runtime_temp_dir() as tmp:
            note = tmp / "2026-01-01-drift.md"
            note.write_text("# Drift\n\n[[Inexistente]]", encoding="utf-8")
            result = self.run_cli("drift-detection", "--path", str(tmp), "--json")
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertTrue(Path(data["report_paths"]["md"]).exists())
            self.assertTrue(Path(data["report_paths"]["json"]).exists())

    def test_remember_plus_accepts_type_and_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = self.setup_vault(tmp)
            source = Path(tmp) / "source.md"
            source.write_text("# Decision\n\nSe adopta proceso.", encoding="utf-8")
            result = self.run_cli("remember", "--input", str(source), "--type", "decision", "--vault-path", str(vault), "--json")
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])
            self.assertEqual(data["memory_type"], "decision")

    def test_archive_preview_and_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = self.setup_vault(tmp)
            source = vault / "30-resources" / "2026-01-01-note.md"
            source.write_text("# Nota\n\nContenido.", encoding="utf-8")
            preview = self.run_cli("archive", "--input", str(source), "--preview", "--vault-path", str(vault), "--json")
            preview_data = json.loads(preview.stdout)
            self.assertTrue(preview_data["ok"])
            self.assertTrue(source.exists())
            applied = self.run_cli("archive", "--input", str(source), "--apply", "--vault-path", str(vault), "--json")
            applied_data = json.loads(applied.stdout)
            self.assertTrue(applied_data["ok"])
            self.assertFalse(source.exists())
            self.assertTrue((vault / "40-archive" / "2026-01-01-note.md").exists())


if __name__ == "__main__":
    unittest.main()
