from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "mi-memoria"
MANIFEST_ROOT = ROOT / "skill-manifest.json"
MANIFEST_DOCS = ROOT / "docs" / "skill-manifest.json"


class ManifestConsistencyTests(unittest.TestCase):
    def test_capabilities_commands_have_manifest_metadata(self) -> None:
        result = subprocess.run(
            ["python3", str(BIN), "capabilities", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        capabilities = json.loads(result.stdout)
        manifest = json.loads(MANIFEST_ROOT.read_text(encoding="utf-8"))
        metadata = manifest.get("command_metadata", {})
        missing = [command for command in capabilities["commands"] if command not in metadata]
        self.assertEqual(missing, [], f"Missing metadata for commands: {missing}")

    def test_root_and_docs_manifests_are_identical(self) -> None:
        root_payload = json.loads(MANIFEST_ROOT.read_text(encoding="utf-8"))
        docs_payload = json.loads(MANIFEST_DOCS.read_text(encoding="utf-8"))
        self.assertEqual(root_payload, docs_payload, "Root manifest and docs mirror differ")


if __name__ == "__main__":
    unittest.main()
