from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


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

    def test_remember(self) -> None:
        result = self.run_cli("remember", "--summary", "Convención aprobada: usar previews antes de apply.", "--json")
        data = json.loads(result.stdout)
        self.assertTrue(data["ok"])
        output = Path(data["output_path"])
        self.addCleanup(lambda path=output: path.exists() and path.unlink())
        self.assertTrue(output.exists())

    def test_setup_vault_and_apply(self) -> None:
        with runtime_temp_dir() as tmp:
            vault = tmp / "vault"
            setup = subprocess.run(
                ["bash", str(ROOT / "scripts" / "skill_setup.sh"), str(vault)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(setup.returncode, 0, setup.stderr)
            self.assertTrue((vault / "00-inbox").is_dir())
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

    def test_preview_to_vault_workspace_and_apply(self) -> None:
        with runtime_temp_dir() as tmp:
            vault = tmp / "vault"
            setup = subprocess.run(
                ["bash", str(ROOT / "scripts" / "skill_setup.sh"), str(vault)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(setup.returncode, 0, setup.stderr)
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
            vault = tmp / "vault"
            setup = subprocess.run(
                ["bash", str(ROOT / "scripts" / "skill_setup.sh"), str(vault)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(setup.returncode, 0, setup.stderr)
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
            vault = tmp / "vault"
            setup = subprocess.run(
                ["bash", str(ROOT / "scripts" / "skill_setup.sh"), str(vault)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(setup.returncode, 0, setup.stderr)

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


if __name__ == "__main__":
    unittest.main()
