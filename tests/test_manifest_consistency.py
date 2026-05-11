from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "mi-memoria"
MANIFEST = ROOT / "docs" / "skill-manifest.json"


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
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        metadata = manifest.get("command_metadata", {})
        missing = [command for command in capabilities["commands"] if command not in metadata]
        self.assertEqual(missing, [], f"Missing metadata for commands: {missing}")


if __name__ == "__main__":
    unittest.main()
