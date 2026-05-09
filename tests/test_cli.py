from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "mi-memoria"


class MiMemoriaCliTests(unittest.TestCase):
    def run_cli(
        self, *args: str, check: bool = True, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        process_env = os.environ.copy()
        process_env.pop("MI_MEMORIA_VAULT_PATH", None)
        if env:
            process_env.update(env)
        result = subprocess.run(
            ["python3", str(BIN), *args],
            cwd=ROOT,
            env=process_env,
            text=True,
            capture_output=True,
            check=False,
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

    def test_normalize_preview_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            note = Path(tmp) / "note.md"
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
        with tempfile.TemporaryDirectory() as tmp:
            note = Path(tmp) / "note.md"
            note.write_text("# Nota\n\nContenido.", encoding="utf-8")
            result = self.run_cli("run", "normalize", "--input", str(note), "--write", "--json", check=False)
            self.assertNotEqual(result.returncode, 0)
            data = json.loads(result.stdout)
            self.assertFalse(data["ok"])

    def test_validate_invalid_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            invalid = Path(tmp) / "invalid.md"
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
        with tempfile.TemporaryDirectory() as tmp:
            vault = self.setup_vault(tmp)
            self.assertTrue((vault / "00-inbox").is_dir())
            memory_template = vault / "templates" / "memory.md"
            self.assertTrue(memory_template.is_file())
            self.assertIn("type: memory", memory_template.read_text(encoding="utf-8"))
            note = Path(tmp) / "note.md"
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
        with tempfile.TemporaryDirectory() as tmp:
            vault = self.setup_vault(tmp)
            (vault / "templates" / "note.md").unlink()
            note = Path(tmp) / "note.md"
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
        with tempfile.TemporaryDirectory() as tmp:
            vault = self.setup_vault(tmp)
            (vault / "templates" / "note.md").write_text(
                "---\ntitle:\ntype: note\nstatus: draft\ncreated:\nupdated:\ntags: []\naliases: []\nsource:\n---\n\n# Título\n\n## Resumen\n\n## Desarrollo\n\n## Relaciones\n\n## Pendientes\n\n## Contexto local\n",
                encoding="utf-8",
            )
            note = Path(tmp) / "note.md"
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


if __name__ == "__main__":
    unittest.main()
