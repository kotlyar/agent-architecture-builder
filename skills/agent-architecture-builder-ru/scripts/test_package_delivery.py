from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("package_delivery.py")
SPEC = importlib.util.spec_from_file_location("package_delivery", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PackageDeliveryTest(unittest.TestCase):
    def make_kit(self, root: Path, *, status: str = "ready_for_implementation") -> Path:
        kit = root / "source"
        for name in MODULE.REQUIRED_FILES:
            path = kit / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("test\n", encoding="utf-8")
        manifest = {
            "schema_version": 2,
            "system_slug": "test-agent-system",
            "status": status,
            "target_platforms": [
                {"slug": "custom-runtime", "adapter": "platforms/custom-runtime/README.md"}
            ],
            "entrypoint": "START-HERE.md",
            "implementation_instruction": "IMPLEMENTATION.md",
            "critical_unknowns": [],
            "components": [
                {
                    "slug": "test-worker",
                    "kind": "persistent-agent",
                    "specification": "blueprint/components/test-worker.md",
                }
            ],
            "expected_results": [
                "implementation/",
                "implementation/IMPLEMENTATION-RESULT.md",
            ],
        }
        (kit / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        adapter = kit / "platforms/custom-runtime/README.md"
        adapter.parent.mkdir(parents=True, exist_ok=True)
        adapter.write_text("adapter\n", encoding="utf-8")
        component = kit / "blueprint/components/test-worker.md"
        component.parent.mkdir(parents=True, exist_ok=True)
        component.write_text("component\n", encoding="utf-8")
        return kit

    def test_ready_custom_platform_kit_is_packaged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = MODULE.package(self.make_kit(root), root / "result.zip")
            self.assertTrue(result.is_file())

    def test_draft_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            kit = self.make_kit(root, status="draft")
            with self.assertRaises(MODULE.PackageError):
                MODULE.package(kit, root / "result.zip")

    def test_missing_platform_adapter_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            kit = self.make_kit(root)
            (kit / "platforms/custom-runtime/README.md").unlink()
            with self.assertRaises(MODULE.PackageError):
                MODULE.package(kit, root / "result.zip")

    def test_unsupported_component_kind_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            kit = self.make_kit(root)
            manifest_path = kit / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["components"][0]["kind"] = "job-title"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(MODULE.PackageError):
                MODULE.package(kit, root / "result.zip")

    def test_secret_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            kit = self.make_kit(root)
            (kit / ".env").write_text("SECRET=value\n", encoding="utf-8")
            with self.assertRaises(MODULE.PackageError):
                MODULE.package(kit, root / "result.zip")


if __name__ == "__main__":
    unittest.main()
