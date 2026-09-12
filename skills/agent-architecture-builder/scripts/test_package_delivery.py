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
    def contract(self, slug: str, kind: str) -> dict:
        details = {
            "persistent-agent": {
                "owned_outcome": "A durable result",
                "lifecycle": {"start": "On request", "run": "Process one item", "stop": "When complete"},
                "skills": [],
                "tools": [],
                "handoffs": [],
                "recovery": "Resume from stored status",
            },
            "skill": {
                "skill_name": slug,
                "use_when": ["The repeatable method is needed"],
                "do_not_use_when": ["A deterministic operation is enough"],
                "method_steps": ["Inspect input", "Produce result"],
                "output_format": "A structured report",
                "tool_dependencies": [],
                "skill_dependencies": [],
                "reuse_decision": "create-new",
                "reuse_candidate": None,
            },
            "tool": {
                "operation": "Read one record",
                "effect": "read",
                "input_schema": {"type": "object"},
                "output_schema": {"type": "object"},
                "retry_policy": "Retry safe reads twice",
                "result_verification": "Compare the returned identifier",
            },
        }
        return {
            "contract_schema_version": 2,
            "slug": slug,
            "kind": kind,
            "purpose": "Produce one observable result",
            "trigger": "A request arrives",
            "inputs": [{"name": "request", "required": True, "description": "Requested work"}],
            "outputs": [{"name": "result", "description": "Completed work"}],
            "state": {"reads": [], "writes": []},
            "authority": {"allowed": [], "forbidden": [], "approval_required": []},
            "runtime_dependencies": ["test-integration"],
            "blocked_behavior": "Stop dependent work and enter setup mode",
            "failures": [{"condition": "Input is invalid", "response": "Stop with an error"}],
            "acceptance": ["The result matches the request"],
            "kind_contract": details[kind],
        }

    def make_kit(self, root: Path, *, status: str = "ready_for_implementation") -> Path:
        kit = root / "source"
        for name in MODULE.REQUIRED_FILES:
            path = kit / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("test\n", encoding="utf-8")
        manifest = {
            "schema_version": 4,
            "system_slug": "test-agent-system",
            "status": status,
            "target_platforms": [
                {"slug": "custom-runtime", "adapter": "platforms/custom-runtime/README.md"}
            ],
            "entrypoint": "START-HERE.md",
            "implementation_instruction": "IMPLEMENTATION.md",
            "skill_reuse": "reuse/skills.json",
            "startup_readiness": "requirements/startup-readiness.json",
            "critical_unknowns": [],
            "components": [
                {
                    "slug": "test-worker",
                    "kind": "persistent-agent",
                    "specification": "blueprint/components/test-worker.md",
                    "contract": "blueprint/contracts/test-worker.json",
                }
            ],
            "expected_results": [
                "implementation/",
                "implementation/IMPLEMENTATION-RESULT.md",
            ],
        }
        (kit / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        readiness = {
            "readiness_schema_version": 1,
            "default_state": "blocked",
            "check_command": "bin/check-readiness --json",
            "ready_condition": "Every required dependency passes its readiness check",
            "allowed_while_blocked": ["Explain setup", "Run safe diagnostics"],
            "dependencies": [
                {
                    "slug": "test-integration",
                    "kind": "integration",
                    "required_for": ["test-worker"],
                    "purpose": "Provide required source data",
                    "configuration_refs": ["config:service.account_id"],
                    "secret_refs": ["env:TEST_API_TOKEN"],
                    "minimum_permissions": ["read"],
                    "setup_owner": "operator",
                    "setup_instruction": "Store the token in the runtime environment",
                    "readiness_check": "Read and compare the connected account identifier",
                    "failure_behavior": "block-dependent-work",
                }
            ],
        }
        (kit / "requirements/startup-readiness.json").write_text(
            json.dumps(readiness), encoding="utf-8"
        )
        adapter = kit / "platforms/custom-runtime/README.md"
        adapter.parent.mkdir(parents=True, exist_ok=True)
        adapter.write_text("adapter\n", encoding="utf-8")
        component = kit / "blueprint/components/test-worker.md"
        component.parent.mkdir(parents=True, exist_ok=True)
        component.write_text("component\n", encoding="utf-8")
        contract = kit / "blueprint/contracts/test-worker.json"
        contract.parent.mkdir(parents=True, exist_ok=True)
        contract.write_text(json.dumps(self.contract("test-worker", "persistent-agent")), encoding="utf-8")
        reuse = kit / "reuse/skills.json"
        reuse.parent.mkdir(parents=True, exist_ok=True)
        reuse.write_text(
            json.dumps({
                "schema_version": 1,
                "search_status": "not-required",
                "sources_checked": [],
                "queries": [],
                "candidates": [],
                "decisions": [],
            }),
            encoding="utf-8",
        )
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

    def test_missing_component_contract_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            kit = self.make_kit(root)
            path = kit / "blueprint/contracts/test-worker.json"
            contract = json.loads(path.read_text(encoding="utf-8"))
            del contract["kind_contract"]["lifecycle"]
            path.write_text(json.dumps(contract), encoding="utf-8")
            with self.assertRaises(MODULE.PackageError):
                MODULE.package(kit, root / "result.zip")

    def test_missing_startup_readiness_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            kit = self.make_kit(root)
            (kit / "requirements/startup-readiness.json").unlink()
            with self.assertRaises(MODULE.PackageError):
                MODULE.package(kit, root / "result.zip")

    def test_startup_dependency_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            kit = self.make_kit(root)
            path = kit / "requirements/startup-readiness.json"
            readiness = json.loads(path.read_text(encoding="utf-8"))
            readiness["dependencies"][0]["slug"] = "different-integration"
            path.write_text(json.dumps(readiness), encoding="utf-8")
            with self.assertRaises(MODULE.PackageError):
                MODULE.package(kit, root / "result.zip")

    def test_unsafe_secret_reference_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            kit = self.make_kit(root)
            path = kit / "requirements/startup-readiness.json"
            readiness = json.loads(path.read_text(encoding="utf-8"))
            readiness["dependencies"][0]["secret_refs"] = ["actual-token-value"]
            path.write_text(json.dumps(readiness), encoding="utf-8")
            with self.assertRaises(MODULE.PackageError):
                MODULE.package(kit, root / "result.zip")

    def test_component_without_runtime_dependencies_can_start_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            kit = self.make_kit(root)
            contract_path = kit / "blueprint/contracts/test-worker.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["runtime_dependencies"] = []
            contract_path.write_text(json.dumps(contract), encoding="utf-8")
            readiness_path = kit / "requirements/startup-readiness.json"
            readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
            readiness["default_state"] = "ready"
            readiness["dependencies"] = []
            readiness_path.write_text(json.dumps(readiness), encoding="utf-8")
            result = MODULE.package(kit, root / "result.zip")
            self.assertTrue(result.is_file())

    def test_skill_without_reuse_decision_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            kit = self.make_kit(root)
            manifest_path = kit / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["components"][0]["kind"] = "skill"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            contract_path = kit / "blueprint/contracts/test-worker.json"
            contract_path.write_text(json.dumps(self.contract("test-worker", "skill")), encoding="utf-8")
            with self.assertRaises(MODULE.PackageError):
                MODULE.package(kit, root / "result.zip")

    def test_skill_with_create_new_decision_is_packaged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            kit = self.make_kit(root)
            manifest_path = kit / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["components"][0]["kind"] = "skill"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            (kit / "blueprint/contracts/test-worker.json").write_text(
                json.dumps(self.contract("test-worker", "skill")), encoding="utf-8"
            )
            (kit / "reuse/skills.json").write_text(
                json.dumps({
                    "schema_version": 1,
                    "search_status": "completed",
                    "sources_checked": [
                        {"kind": "installed", "location": "local", "status": "checked"},
                        {"kind": "platform", "location": "custom", "status": "unavailable"},
                        {"kind": "public-catalog", "location": "catalog", "status": "checked"},
                        {"kind": "repository", "location": "repository", "status": "checked"},
                    ],
                    "queries": ["worker method", "process worker"],
                    "candidates": [],
                    "decisions": [{
                        "component_slug": "test-worker",
                        "decision": "create-new",
                        "candidate_id": None,
                        "rationale": "No candidate covers the required method",
                    }],
                }),
                encoding="utf-8",
            )
            result = MODULE.package(kit, root / "result.zip")
            self.assertTrue(result.is_file())

    def test_tool_operation_must_be_singular_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            kit = self.make_kit(root)
            manifest_path = kit / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["components"][0]["kind"] = "tool"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            contract = self.contract("test-worker", "tool")
            contract["kind_contract"]["operation"] = ["create", "update", "delete"]
            (kit / "blueprint/contracts/test-worker.json").write_text(json.dumps(contract), encoding="utf-8")
            with self.assertRaises(MODULE.PackageError):
                MODULE.package(kit, root / "result.zip")

    def test_reuse_record_must_match_skill_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            kit = self.make_kit(root)
            manifest_path = kit / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["components"][0]["kind"] = "skill"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            contract = self.contract("test-worker", "skill")
            contract["kind_contract"]["reuse_decision"] = "adapt"
            contract["kind_contract"]["reuse_candidate"] = "candidate-1"
            (kit / "blueprint/contracts/test-worker.json").write_text(json.dumps(contract), encoding="utf-8")
            (kit / "reuse/skills.json").write_text(
                json.dumps({
                    "schema_version": 1,
                    "search_status": "completed",
                    "sources_checked": [
                        {"kind": "installed", "location": "local", "status": "checked"},
                        {"kind": "platform", "location": "custom", "status": "unavailable"},
                        {"kind": "public-catalog", "location": "catalog", "status": "checked"},
                        {"kind": "repository", "location": "repository", "status": "checked"},
                    ],
                    "queries": ["worker method", "process worker"],
                    "candidates": [{
                        "id": "candidate-1",
                        "name": "existing-worker",
                        "source": "https://example.invalid/repository",
                        "revision": "0123456789abcdef",
                        "license": "MIT",
                        "target_component": "test-worker",
                        "coverage": ["Core method"],
                        "gaps": ["Output adapter"],
                        "dependencies": [],
                        "risks": [],
                        "decision": "adapt",
                    }],
                    "decisions": [{
                        "component_slug": "test-worker",
                        "decision": "adapt",
                        "candidate_id": "candidate-1",
                        "rationale": "Candidate covers the method",
                    }],
                }),
                encoding="utf-8",
            )
            result = MODULE.package(kit, root / "result.zip")
            self.assertTrue(result.is_file())
            reuse_path = kit / "reuse/skills.json"
            reuse = json.loads(reuse_path.read_text(encoding="utf-8"))
            reuse["decisions"][0]["decision"] = "reuse"
            reuse_path.write_text(json.dumps(reuse), encoding="utf-8")
            with self.assertRaises(MODULE.PackageError):
                MODULE.package(kit, root / "mismatch.zip")


if __name__ == "__main__":
    unittest.main()
