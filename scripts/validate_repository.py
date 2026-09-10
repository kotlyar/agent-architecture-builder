#!/usr/bin/env python3
"""Validate both skill editions and their deterministic packaging tests."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EDITIONS = {
    "hermes-agent-builder": "hermes-agent-builder",
    "hermes-agent-builder-en": "hermes-agent-builder-en",
}
REQUIRED = (
    "SKILL.md",
    "references/architecture-decisions.md",
    "references/control-interface-and-storage.md",
    "references/delivery-package.md",
    "references/discovery-interview.md",
    "references/question-hints.md",
    "references/web-interface-stack.md",
    "assets/AGENTS.template.md",
    "assets/IMPLEMENTATION.template.md",
    "assets/manifest.template.json",
    "assets/START-HERE.template.md",
    "scripts/package_delivery.py",
    "scripts/test_package_delivery.py",
)
FORBIDDEN_NAMES = {".env", "auth.json", "state.db", "id_rsa", "id_ed25519"}
FORBIDDEN_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}


def fail(message: str) -> None:
    raise RuntimeError(message)


def validate_edition(directory: str, expected_name: str) -> None:
    root = ROOT / "skills" / directory
    missing = [relative for relative in REQUIRED if not (root / relative).is_file()]
    if missing:
        fail(f"{directory}: missing files: {', '.join(missing)}")

    skill_text = (root / "SKILL.md").read_text(encoding="utf-8")
    name_match = re.search(r"(?m)^name:\s*([^\s]+)\s*$", skill_text)
    if not name_match or name_match.group(1) != expected_name:
        fail(f"{directory}: SKILL.md name does not match its edition")
    if not re.search(r"(?m)^description:\s*\S", skill_text):
        fail(f"{directory}: SKILL.md description is missing")

    manifest = json.loads(
        (root / "assets/manifest.template.json").read_text(encoding="utf-8")
    )
    expected_status = "draft" if directory.endswith("-en") else "черновик"
    if manifest.get("status") != expected_status:
        fail(f"{directory}: unexpected manifest template status")

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            fail(f"{directory}: possible secret file: {path.relative_to(root)}")

    if directory.endswith("-en"):
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".json", ".py"}:
                text = path.read_text(encoding="utf-8")
                if re.search(r"[А-Яа-яЁё]", text):
                    fail(f"{directory}: Cyrillic text found in {path.relative_to(root)}")

    subprocess.run(
        [sys.executable, str(root / "scripts/test_package_delivery.py"), "-v"],
        cwd=ROOT,
        check=True,
    )


def main() -> int:
    try:
        for directory, expected_name in EDITIONS.items():
            validate_edition(directory, expected_name)
    except (RuntimeError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1
    print("Repository validation passed for Russian and English editions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
