#!/usr/bin/env python3
"""Validate and package a platform-neutral agent-system implementation kit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path


REQUIRED_FILES = (
    "START-HERE.md",
    "IMPLEMENTATION.md",
    "IMPLEMENTER-RULES.md",
    "manifest.json",
    "requirements/goal.md",
    "requirements/work-map.md",
    "requirements/constraints.md",
    "requirements/startup-readiness.json",
    "architecture/platform-neutral.md",
    "architecture/system.md",
    "architecture/decisions.md",
    "architecture/authority.md",
    "architecture/interface-and-storage.md",
    "acceptance/criteria.md",
    "acceptance/scenarios.md",
    "blueprint/project-tree.md",
    "evidence/sources.md",
    "reuse/skills.json",
    "unresolved.md",
)
COMPONENT_KINDS = {
    "deterministic-workflow",
    "tool",
    "skill",
    "subagent",
    "persistent-agent",
    "orchestrator",
    "storage",
    "interface",
}
FORBIDDEN_NAMES = {".env", "auth.json", "state.db", "id_rsa", "id_ed25519"}
FORBIDDEN_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
COMMON_CONTRACT_FIELDS = {
    "contract_schema_version",
    "slug",
    "kind",
    "purpose",
    "trigger",
    "inputs",
    "outputs",
    "state",
    "authority",
    "runtime_dependencies",
    "blocked_behavior",
    "failures",
    "acceptance",
    "kind_contract",
}
KIND_CONTRACT_FIELDS = {
    "deterministic-workflow": {"steps", "branch_rules", "stop_conditions"},
    "tool": {
        "operation",
        "effect",
        "input_schema",
        "output_schema",
        "retry_policy",
        "result_verification",
    },
    "skill": {
        "skill_name",
        "use_when",
        "do_not_use_when",
        "method_steps",
        "output_format",
        "tool_dependencies",
        "skill_dependencies",
        "reuse_decision",
        "reuse_candidate",
    },
    "subagent": {
        "delegated_task",
        "completion_boundary",
        "context_inputs",
        "returned_result",
        "allowed_tools",
    },
    "persistent-agent": {
        "owned_outcome",
        "lifecycle",
        "skills",
        "tools",
        "handoffs",
        "recovery",
    },
    "orchestrator": {
        "coordination_decision",
        "participants",
        "routing_inputs",
        "conflict_policy",
        "stop_condition",
    },
    "storage": {"records", "source_of_truth", "retention", "concurrency", "recovery"},
    "interface": {"users", "decisions", "views", "commands", "stale_state_behavior"},
}
REUSE_DECISIONS = {"reuse", "configure", "adapt", "fork", "reject", "create-new"}
READINESS_KINDS = {"integration", "credential", "data-source", "runtime", "human-decision"}
SAFE_REFERENCE = re.compile(r"^(?:env|config|secret-manager):[A-Za-z0-9._:/#-]+$")


class PackageError(ValueError):
    """The kit cannot be packaged safely."""


def relative_file(root: Path, value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise PackageError(f"{label} must be a non-empty relative path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise PackageError(f"{label} must stay inside the kit")
    target = root / path
    if not target.is_file():
        raise PackageError(f"{label} is missing: {value}")
    return target


def require_slug(value: object, label: str) -> str:
    if not isinstance(value, str) or not SLUG.fullmatch(value):
        raise PackageError(
            f"{label} may contain lowercase ASCII letters, digits, and single hyphens"
        )
    return value


def require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PackageError(f"{label} must be a non-empty string")
    return value


def require_list(value: object, label: str, *, non_empty: bool = False) -> list:
    if not isinstance(value, list) or (non_empty and not value):
        qualifier = "non-empty " if non_empty else ""
        raise PackageError(f"{label} must be a {qualifier}list")
    return value


def require_string_list(value: object, label: str, *, non_empty: bool = False) -> list[str]:
    items = require_list(value, label, non_empty=non_empty)
    if not all(isinstance(item, str) and item.strip() for item in items):
        raise PackageError(f"{label} must contain only non-empty strings")
    return items


def load_json_file(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PackageError(f"{label} is invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise PackageError(f"{label} must be an object")
    return value


def validate_component_contract(path: Path, slug: str, kind: str) -> tuple[str, str | None] | None:
    contract = load_json_file(path, f"contract for {slug}")
    missing = sorted(COMMON_CONTRACT_FIELDS - contract.keys())
    if missing:
        raise PackageError(f"contract for {slug} is missing fields: {', '.join(missing)}")
    if contract["contract_schema_version"] != 2:
        raise PackageError(f"contract for {slug} must use contract_schema_version = 2")
    if contract["slug"] != slug or contract["kind"] != kind:
        raise PackageError(f"contract identity does not match component {slug}")
    require_text(contract["purpose"], f"contract {slug}.purpose")
    require_text(contract["trigger"], f"contract {slug}.trigger")
    for field in ("inputs", "outputs"):
        records = require_list(contract[field], f"contract {slug}.{field}", non_empty=field == "outputs")
        for number, record in enumerate(records, start=1):
            if not isinstance(record, dict):
                raise PackageError(f"contract {slug}.{field}[{number}] must be an object")
            require_text(record.get("name"), f"contract {slug}.{field}[{number}].name")
            require_text(record.get("description"), f"contract {slug}.{field}[{number}].description")
            if field == "inputs" and not isinstance(record.get("required"), bool):
                raise PackageError(f"contract {slug}.inputs[{number}].required must be boolean")
    state = contract["state"]
    if not isinstance(state, dict) or not {"reads", "writes"}.issubset(state):
        raise PackageError(f"contract {slug}.state must define reads and writes")
    require_string_list(state["reads"], f"contract {slug}.state.reads")
    require_string_list(state["writes"], f"contract {slug}.state.writes")
    authority = contract["authority"]
    authority_fields = {"allowed", "forbidden", "approval_required"}
    if not isinstance(authority, dict) or not authority_fields.issubset(authority):
        raise PackageError(f"contract {slug}.authority is incomplete")
    for field in authority_fields:
        require_string_list(authority[field], f"contract {slug}.authority.{field}")
    dependencies = require_string_list(
        contract["runtime_dependencies"], f"contract {slug}.runtime_dependencies"
    )
    if len(dependencies) != len(set(dependencies)):
        raise PackageError(f"contract {slug}.runtime_dependencies contains duplicates")
    for dependency in dependencies:
        require_slug(dependency, f"contract {slug}.runtime dependency")
    require_text(contract["blocked_behavior"], f"contract {slug}.blocked_behavior")
    failures = require_list(contract["failures"], f"contract {slug}.failures", non_empty=True)
    for number, failure in enumerate(failures, start=1):
        if not isinstance(failure, dict):
            raise PackageError(f"contract {slug}.failures[{number}] must be an object")
        require_text(failure.get("condition"), f"contract {slug}.failures[{number}].condition")
        require_text(failure.get("response"), f"contract {slug}.failures[{number}].response")
    require_string_list(contract["acceptance"], f"contract {slug}.acceptance", non_empty=True)

    detail = contract["kind_contract"]
    if not isinstance(detail, dict):
        raise PackageError(f"contract {slug}.kind_contract must be an object")
    missing_detail = sorted(KIND_CONTRACT_FIELDS[kind] - detail.keys())
    if missing_detail:
        raise PackageError(
            f"contract {slug}.kind_contract is missing fields: {', '.join(missing_detail)}"
        )
    if kind == "deterministic-workflow":
        for field in ("steps", "branch_rules", "stop_conditions"):
            require_string_list(detail[field], f"contract {slug}.{field}", non_empty=True)
    elif kind == "tool":
        require_text(detail["operation"], f"contract {slug}.operation")
        if detail["effect"] not in {"read", "local-write", "external-write", "financial"}:
            raise PackageError(f"contract {slug}.effect is unsupported")
        for field in ("input_schema", "output_schema"):
            if not isinstance(detail[field], dict) or not detail[field]:
                raise PackageError(f"contract {slug}.{field} must be a non-empty object")
        require_text(detail["retry_policy"], f"contract {slug}.retry_policy")
        require_text(detail["result_verification"], f"contract {slug}.result_verification")
    elif kind == "skill":
        if detail["skill_name"] != slug:
            raise PackageError(f"contract {slug}.skill_name must equal its component slug")
        for field in ("use_when", "do_not_use_when", "method_steps"):
            require_string_list(detail[field], f"contract {slug}.{field}", non_empty=True)
        for field in ("tool_dependencies", "skill_dependencies"):
            require_string_list(detail[field], f"contract {slug}.{field}")
        require_text(detail["output_format"], f"contract {slug}.output_format")
        if detail["reuse_decision"] not in REUSE_DECISIONS - {"reject"}:
            raise PackageError(f"contract {slug}.reuse_decision is unsupported")
        candidate = detail["reuse_candidate"]
        if detail["reuse_decision"] == "create-new":
            if candidate is not None:
                raise PackageError(f"contract {slug}.reuse_candidate must be null for create-new")
        else:
            require_text(candidate, f"contract {slug}.reuse_candidate")
        return detail["reuse_decision"], candidate
    elif kind == "subagent":
        for field in ("delegated_task", "completion_boundary", "returned_result"):
            require_text(detail[field], f"contract {slug}.{field}")
        for field in ("context_inputs", "allowed_tools"):
            require_string_list(detail[field], f"contract {slug}.{field}")
    elif kind == "persistent-agent":
        for field in ("owned_outcome", "recovery"):
            require_text(detail[field], f"contract {slug}.{field}")
        lifecycle = detail["lifecycle"]
        if not isinstance(lifecycle, dict) or not {"start", "run", "stop"}.issubset(lifecycle):
            raise PackageError(f"contract {slug}.lifecycle is incomplete")
        for field in ("start", "run", "stop"):
            require_text(lifecycle[field], f"contract {slug}.lifecycle.{field}")
        for field in ("skills", "tools", "handoffs"):
            require_string_list(detail[field], f"contract {slug}.{field}")
    elif kind == "orchestrator":
        for field in ("coordination_decision", "conflict_policy", "stop_condition"):
            require_text(detail[field], f"contract {slug}.{field}")
        require_string_list(detail["participants"], f"contract {slug}.participants", non_empty=True)
        if len(detail["participants"]) < 2:
            raise PackageError(f"contract {slug}.participants requires at least two entries")
        require_string_list(detail["routing_inputs"], f"contract {slug}.routing_inputs", non_empty=True)
    elif kind == "storage":
        require_string_list(detail["records"], f"contract {slug}.records", non_empty=True)
        for field in ("source_of_truth", "retention", "concurrency", "recovery"):
            require_text(detail[field], f"contract {slug}.{field}")
    elif kind == "interface":
        for field in ("users", "decisions", "views", "commands"):
            require_string_list(detail[field], f"contract {slug}.{field}", non_empty=True)
        require_text(detail["stale_state_behavior"], f"contract {slug}.stale_state_behavior")
    return None


def contract_runtime_dependencies(path: Path, slug: str) -> set[str]:
    contract = load_json_file(path, f"contract for {slug}")
    return set(
        require_string_list(
            contract.get("runtime_dependencies"),
            f"contract {slug}.runtime_dependencies",
        )
    )


def validate_startup_readiness(
    path: Path,
    component_dependencies: dict[str, set[str]],
) -> None:
    record = load_json_file(path, "startup readiness contract")
    required = {
        "readiness_schema_version",
        "default_state",
        "check_command",
        "ready_condition",
        "allowed_while_blocked",
        "dependencies",
    }
    missing = sorted(required - record.keys())
    if missing:
        raise PackageError(
            "startup readiness contract is missing fields: " + ", ".join(missing)
        )
    if record["readiness_schema_version"] != 1:
        raise PackageError("startup readiness contract must use readiness_schema_version = 1")
    require_text(record["check_command"], "startup readiness check_command")
    require_text(record["ready_condition"], "startup readiness ready_condition")
    require_string_list(
        record["allowed_while_blocked"],
        "startup readiness allowed_while_blocked",
        non_empty=True,
    )

    dependencies = require_list(record["dependencies"], "startup readiness dependencies")
    if record["default_state"] != ("blocked" if dependencies else "ready"):
        raise PackageError(
            "startup readiness default_state must be blocked when dependencies exist "
            "and ready otherwise"
        )

    declared: dict[str, set[str]] = {}
    component_slugs = set(component_dependencies)
    for number, dependency in enumerate(dependencies, start=1):
        if not isinstance(dependency, dict):
            raise PackageError(f"startup dependency {number} must be an object")
        required_fields = {
            "slug",
            "kind",
            "required_for",
            "purpose",
            "configuration_refs",
            "secret_refs",
            "minimum_permissions",
            "setup_owner",
            "setup_instruction",
            "readiness_check",
            "failure_behavior",
        }
        missing_fields = sorted(required_fields - dependency.keys())
        if missing_fields:
            raise PackageError(
                f"startup dependency {number} is missing fields: "
                + ", ".join(missing_fields)
            )
        slug = require_slug(dependency["slug"], f"startup dependency {number}.slug")
        if slug in declared:
            raise PackageError(f"duplicate startup dependency: {slug}")
        if dependency["kind"] not in READINESS_KINDS:
            raise PackageError(f"startup dependency {slug}.kind is unsupported")
        required_for = set(
            require_string_list(
                dependency["required_for"],
                f"startup dependency {slug}.required_for",
                non_empty=True,
            )
        )
        if not required_for <= component_slugs:
            raise PackageError(f"startup dependency {slug} references unknown components")
        declared[slug] = required_for
        for field in ("purpose", "setup_owner", "setup_instruction", "readiness_check"):
            require_text(dependency[field], f"startup dependency {slug}.{field}")
        for field in ("configuration_refs", "secret_refs"):
            references = require_string_list(
                dependency[field], f"startup dependency {slug}.{field}"
            )
            if any(not SAFE_REFERENCE.fullmatch(reference) for reference in references):
                raise PackageError(
                    f"startup dependency {slug}.{field} must contain only safe references"
                )
        require_string_list(
            dependency["minimum_permissions"],
            f"startup dependency {slug}.minimum_permissions",
            non_empty=True,
        )
        if dependency["failure_behavior"] != "block-dependent-work":
            raise PackageError(
                f"startup dependency {slug}.failure_behavior must be block-dependent-work"
            )

    expected: dict[str, set[str]] = {}
    for component, dependency_slugs in component_dependencies.items():
        for dependency_slug in dependency_slugs:
            expected.setdefault(dependency_slug, set()).add(component)
    if declared != expected:
        raise PackageError(
            "startup dependency records must exactly match component runtime_dependencies"
        )


def validate_skill_reuse(
    path: Path,
    skill_slugs: set[str],
    contract_decisions: dict[str, tuple[str, str | None]],
) -> None:
    record = load_json_file(path, "skill reuse record")
    required = {"schema_version", "search_status", "sources_checked", "queries", "candidates", "decisions"}
    missing = sorted(required - record.keys())
    if missing:
        raise PackageError("skill reuse record is missing fields: " + ", ".join(missing))
    if record["schema_version"] != 1:
        raise PackageError("skill reuse record must use schema_version = 1")
    if record["search_status"] not in {"completed", "not-required"}:
        raise PackageError("skill reuse search_status must be completed or not-required")
    if skill_slugs and record["search_status"] != "completed":
        raise PackageError("skill reuse search must be completed when skill components exist")
    sources = require_list(record["sources_checked"], "skill reuse sources_checked", non_empty=bool(skill_slugs))
    source_kinds: set[str] = set()
    for number, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            raise PackageError(f"skill reuse source {number} must be an object")
        kind = source.get("kind")
        if kind not in {"installed", "platform", "public-catalog", "repository"}:
            raise PackageError(f"skill reuse source {number} has unsupported kind")
        source_kinds.add(kind)
        require_text(source.get("location"), f"skill reuse source {number}.location")
        if source.get("status") not in {"checked", "unavailable"}:
            raise PackageError(f"skill reuse source {number}.status is unsupported")
    if skill_slugs and source_kinds != {"installed", "platform", "public-catalog", "repository"}:
        raise PackageError("skill reuse must record all four source kinds")
    queries = require_string_list(record["queries"], "skill reuse queries")
    if skill_slugs and len(queries) < 2:
        raise PackageError("skill reuse requires at least two search queries")

    candidates = require_list(record["candidates"], "skill reuse candidates")
    candidate_ids: set[str] = set()
    candidate_targets: dict[str, str] = {}
    for number, candidate in enumerate(candidates, start=1):
        if not isinstance(candidate, dict):
            raise PackageError(f"skill reuse candidate {number} must be an object")
        required_candidate = {"id", "name", "source", "revision", "license", "target_component", "coverage", "gaps", "dependencies", "risks", "decision"}
        missing_candidate = sorted(required_candidate - candidate.keys())
        if missing_candidate:
            raise PackageError(f"skill reuse candidate {number} is missing fields: {', '.join(missing_candidate)}")
        candidate_id = require_text(candidate["id"], f"skill reuse candidate {number}.id")
        if candidate_id in candidate_ids:
            raise PackageError(f"duplicate skill reuse candidate: {candidate_id}")
        candidate_ids.add(candidate_id)
        require_text(candidate["name"], f"skill reuse candidate {number}.name")
        require_text(candidate["source"], f"skill reuse candidate {number}.source")
        require_text(candidate["revision"], f"skill reuse candidate {number}.revision")
        require_text(candidate["license"], f"skill reuse candidate {number}.license")
        target = require_slug(candidate["target_component"], f"skill reuse candidate {number}.target_component")
        candidate_targets[candidate_id] = target
        for field in ("coverage", "gaps", "dependencies", "risks"):
            require_string_list(candidate[field], f"skill reuse candidate {number}.{field}", non_empty=field == "coverage")
        if candidate["decision"] not in REUSE_DECISIONS:
            raise PackageError(f"skill reuse candidate {number}.decision is unsupported")

    decisions = require_list(record["decisions"], "skill reuse decisions", non_empty=bool(skill_slugs))
    seen: set[str] = set()
    for number, decision in enumerate(decisions, start=1):
        if not isinstance(decision, dict):
            raise PackageError(f"skill reuse decision {number} must be an object")
        slug = require_slug(decision.get("component_slug"), f"skill reuse decision {number}.component_slug")
        if slug in seen:
            raise PackageError(f"duplicate skill reuse decision for {slug}")
        seen.add(slug)
        choice = decision.get("decision")
        if choice not in REUSE_DECISIONS - {"reject"}:
            raise PackageError(f"skill reuse decision {number}.decision is unsupported")
        require_text(decision.get("rationale"), f"skill reuse decision {number}.rationale")
        candidate_id = decision.get("candidate_id")
        if choice == "create-new":
            if candidate_id is not None:
                raise PackageError(f"skill reuse decision for {slug} must not select a candidate")
        elif candidate_id not in candidate_ids or candidate_targets[candidate_id] != slug:
            raise PackageError(f"skill reuse decision for {slug} has no matching candidate")
        if contract_decisions.get(slug) != (choice, candidate_id):
            raise PackageError(f"skill reuse decision for {slug} conflicts with its component contract")
    if seen != skill_slugs:
        raise PackageError("skill reuse decisions must match manifest skill components exactly")


def load_manifest(root: Path) -> dict:
    try:
        data = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PackageError("manifest.json is missing") from exc
    except json.JSONDecodeError as exc:
        raise PackageError(f"manifest.json is invalid: {exc}") from exc

    required = {
        "schema_version",
        "system_slug",
        "status",
        "target_platforms",
        "entrypoint",
        "implementation_instruction",
        "skill_reuse",
        "startup_readiness",
        "critical_unknowns",
        "components",
        "expected_results",
    }
    missing = sorted(required - data.keys())
    if missing:
        raise PackageError("manifest.json is missing fields: " + ", ".join(missing))
    if data["schema_version"] != 4:
        raise PackageError("only schema_version = 4 is supported")
    if data["status"] not in {"ready_for_implementation", "implemented"}:
        raise PackageError("only a ready kit can be archived")
    if data["critical_unknowns"]:
        raise PackageError("critical_unknowns must be empty")
    require_slug(data["system_slug"], "system_slug")

    platforms = data["target_platforms"]
    if not isinstance(platforms, list) or not platforms:
        raise PackageError("target_platforms must be a non-empty list")
    platform_slugs: set[str] = set()
    for number, platform in enumerate(platforms, start=1):
        if not isinstance(platform, dict):
            raise PackageError(f"target_platforms[{number}] must be an object")
        missing_fields = {"slug", "adapter"} - platform.keys()
        if missing_fields:
            raise PackageError(
                f"target_platforms[{number}] is missing fields: "
                + ", ".join(sorted(missing_fields))
            )
        slug = require_slug(platform["slug"], f"target_platforms[{number}].slug")
        if slug in platform_slugs:
            raise PackageError(f"duplicate target platform: {slug}")
        platform_slugs.add(slug)
        relative_file(root, platform["adapter"], f"adapter for {slug}")

    components = data["components"]
    if not isinstance(components, list) or not components:
        raise PackageError("components must be a non-empty list")
    component_slugs: set[str] = set()
    skill_slugs: set[str] = set()
    skill_contract_decisions: dict[str, tuple[str, str | None]] = {}
    component_dependencies: dict[str, set[str]] = {}
    for number, component in enumerate(components, start=1):
        if not isinstance(component, dict):
            raise PackageError(f"components[{number}] must be an object")
        missing_fields = {"slug", "kind", "specification", "contract"} - component.keys()
        if missing_fields:
            raise PackageError(
                f"components[{number}] is missing fields: "
                + ", ".join(sorted(missing_fields))
            )
        slug = require_slug(component["slug"], f"components[{number}].slug")
        if slug in component_slugs:
            raise PackageError(f"duplicate component: {slug}")
        component_slugs.add(slug)
        if component["kind"] not in COMPONENT_KINDS:
            raise PackageError(f"unsupported component kind: {component['kind']}")
        expected_specification = f"blueprint/components/{slug}.md"
        expected_contract = f"blueprint/contracts/{slug}.json"
        if component["specification"] != expected_specification:
            raise PackageError(f"specification for {slug} must be {expected_specification}")
        if component["contract"] != expected_contract:
            raise PackageError(f"contract for {slug} must be {expected_contract}")
        relative_file(root, component["specification"], f"specification for {slug}")
        contract_path = relative_file(root, component["contract"], f"contract for {slug}")
        contract_decision = validate_component_contract(contract_path, slug, component["kind"])
        component_dependencies[slug] = contract_runtime_dependencies(contract_path, slug)
        if component["kind"] == "skill":
            skill_slugs.add(slug)
            assert contract_decision is not None
            skill_contract_decisions[slug] = contract_decision

    relative_file(root, data["entrypoint"], "entrypoint")
    relative_file(root, data["implementation_instruction"], "implementation_instruction")
    reuse_path = relative_file(root, data["skill_reuse"], "skill_reuse")
    validate_skill_reuse(reuse_path, skill_slugs, skill_contract_decisions)
    readiness_path = relative_file(
        root, data["startup_readiness"], "startup_readiness"
    )
    validate_startup_readiness(readiness_path, component_dependencies)
    return data


def collect_files(root: Path) -> list[Path]:
    missing = [item for item in REQUIRED_FILES if not (root / item).is_file()]
    if missing:
        raise PackageError("required files are missing: " + ", ".join(missing))

    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise PackageError(f"symbolic links are forbidden: {path.relative_to(root)}")
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        private_env = path.name.startswith(".env.") and path.name != ".env.EXAMPLE"
        state_db = path.name.startswith("state.db")
        if (
            path.name in FORBIDDEN_NAMES
            or path.suffix.lower() in FORBIDDEN_SUFFIXES
            or private_env
            or state_db
        ):
            raise PackageError(f"possible secret detected: {relative}")
        if "__pycache__" in relative.parts or path.name == ".DS_Store":
            continue
        files.append(path)
    return files


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def package(root: Path, output: Path | None = None) -> Path:
    root = root.resolve()
    if not root.is_dir():
        raise PackageError(f"directory not found: {root}")
    manifest = load_manifest(root)
    files = collect_files(root)
    system_slug = manifest["system_slug"]

    destination = (output or root.with_name(f"{system_slug}-agent-kit.zip")).resolve()
    if destination.is_dir():
        destination = destination / f"{system_slug}-agent-kit.zip"
    if destination.is_relative_to(root):
        raise PackageError("the archive cannot be created inside the source kit")
    destination.parent.mkdir(parents=True, exist_ok=True)

    checksum_lines = [
        f"{digest(path)}  {path.relative_to(root).as_posix()}" for path in files
    ]
    prefix = f"{system_slug}-agent-kit"
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, f"{prefix}/{path.relative_to(root).as_posix()}")
        archive.writestr(
            f"{prefix}/CHECKSUMS.sha256", "\n".join(checksum_lines) + "\n"
        )
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="ready implementation-kit directory")
    parser.add_argument("--output", type=Path, help="output archive path")
    args = parser.parse_args()
    try:
        result = package(args.source, args.output)
    except PackageError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
