from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

from cli import main as cli_main


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "mi-memoria"


class MiMemoriaCliTests(unittest.TestCase):
    def run_cli(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["python3", str(BIN), *args],
            cwd=ROOT,
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

    def test_remember(self) -> None:
        result = self.run_cli("remember", "--summary", "Convención aprobada: usar previews antes de apply.", "--json")
        data = json.loads(result.stdout)
        self.assertTrue(data["ok"])
        output = Path(data["output_path"])
        self.addCleanup(lambda path=output: path.exists() and path.unlink())
        self.assertTrue(output.exists())

    def test_setup_vault_and_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "vault"
            setup = subprocess.run(
                ["bash", str(ROOT / "scripts" / "skill_setup.sh"), str(vault)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(setup.returncode, 0, setup.stderr)
            self.assertTrue((vault / "00-inbox").is_dir())
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


if __name__ == "__main__":
    unittest.main()
