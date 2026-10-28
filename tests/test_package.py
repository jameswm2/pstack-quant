import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PackageChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "relocated-plugin"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__"))

    def check(self, expected=0):
        result = subprocess.run([sys.executable, str(self.root / "tools/check_package.py")], capture_output=True, text=True, cwd=self.temp.name)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_relocated_plugin_without_git_passes_and_example_runs(self):
        self.check()
        result = subprocess.run([sys.executable, str(self.root / "examples/synthetic/run.py"), "demo", str(Path(self.temp.name) / "research")], capture_output=True, text=True, cwd=self.temp.name)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("independent review BLOCKED", result.stdout)

    def test_manifest_identity_mismatch_is_rejected(self):
        path = self.root / ".codex-plugin/plugin.json"
        value = json.loads(path.read_text())
        value["version"] = "0.2.0"
        path.write_text(json.dumps(value))
        self.assertIn("manifest mismatch", self.check(1).stderr)

    def test_escaping_marketplace_source_is_rejected(self):
        path = self.root / ".agents/plugins/marketplace.json"
        value = json.loads(path.read_text())
        value["plugins"][0]["source"]["path"] = "./.."
        path.write_text(json.dumps(value))
        self.assertIn("escaping path", self.check(1).stderr)

    def test_missing_link_and_provenance_are_rejected(self):
        path = self.root / "docs/architecture.md"
        path.write_text(path.read_text() + "\n[missing](missing.md)\n")
        self.assertIn("broken or escaping link", self.check(1).stderr)
        path.write_text("# Architecture\n")
        (self.root / "licenses/pstack-MIT.txt").write_text("MIT")
        self.assertIn("missing MIT notice", self.check(1).stderr)


if __name__ == "__main__":
    unittest.main()
