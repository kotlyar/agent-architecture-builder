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
    "architecture/platform-neutral.md",
    "architecture/system.md",
    "architecture/decisions.md",
    "architecture/authority.md",
    "architecture/interface-and-storage.md",
    "acceptance/criteria.md",
    "acceptance/scenarios.md",
    "blueprint/project-tree.md",
    "evidence/sources.md",
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
        "critical_unknowns",
        "components",
        "expected_results",
    }
    missing = sorted(required - data.keys())
    if missing:
        raise PackageError("manifest.json is missing fields: " + ", ".join(missing))
    if data["schema_version"] != 2:
        raise PackageError("only schema_version = 2 is supported")
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
    for number, component in enumerate(components, start=1):
        if not isinstance(component, dict):
            raise PackageError(f"components[{number}] must be an object")
        missing_fields = {"slug", "kind", "specification"} - component.keys()
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
        relative_file(root, component["specification"], f"specification for {slug}")

    relative_file(root, data["entrypoint"], "entrypoint")
    relative_file(root, data["implementation_instruction"], "implementation_instruction")
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
