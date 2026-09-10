#!/usr/bin/env python3
"""Validate the universal bilingual skill, plugins, and packaging contract."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EDITIONS = {
    "agent-architecture-builder": "agent-architecture-builder",
    "agent-architecture-builder-ru": "agent-architecture-builder-ru",
}
REQUIRED = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/architecture-decisions.md",
    "references/control-interface-and-storage.md",
    "references/delivery-package.md",
    "references/discovery-interview.md",
    "references/question-hints.md",
    "references/web-interface-stack.md",
    "references/platforms/codex.md",
    "references/platforms/claude-code.md",
    "references/platforms/hermes.md",
    "assets/IMPLEMENTER-RULES.template.md",
    "assets/IMPLEMENTATION.template.md",
    "assets/manifest.template.json",
    "assets/START-HERE.template.md",
    "scripts/package_delivery.py",
    "scripts/test_package_delivery.py",
)
FORBIDDEN_NAMES = {".env", "auth.json", "state.db", "id_rsa", "id_ed25519"}
FORBIDDEN_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
DOMAIN_TERMS = re.compile(
    r"(?i)\bseo\b|yandex|google ads|яндекс|реклам|маркетолог|marketing"
)
LEGACY_DIRECTORIES = ("hermes-agent-builder", "hermes-agent-builder-en")


def fail(message: str) -> None:
    raise RuntimeError(message)


def frontmatter_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", text)
    if not match:
        return None
    return match.group(1).strip().strip('"\'')


def validate_edition(directory: str, expected_name: str) -> None:
    root = ROOT / "skills" / directory
    missing = [relative for relative in REQUIRED if not (root / relative).is_file()]
    if missing:
        fail(f"{directory}: missing files: {', '.join(missing)}")

    skill_text = (root / "SKILL.md").read_text(encoding="utf-8")
    if frontmatter_value(skill_text, "name") != expected_name:
        fail(f"{directory}: SKILL.md name does not match its directory")
    description = frontmatter_value(skill_text, "description")
    if not description:
        fail(f"{directory}: SKILL.md description is missing")
    if DOMAIN_TERMS.search(description) or "Hermes" in description:
        fail(f"{directory}: description must stay domain- and platform-neutral")

    manifest = json.loads(
        (root / "assets/manifest.template.json").read_text(encoding="utf-8")
    )
    if manifest.get("schema_version") != 2:
        fail(f"{directory}: manifest template must use schema_version 2")
    expected_status = "черновик" if directory.endswith("-ru") else "draft"
    if manifest.get("status") != expected_status:
        fail(f"{directory}: unexpected manifest template status")
    if not isinstance(manifest.get("target_platforms"), list):
        fail(f"{directory}: target_platforms must be a list")
    if not isinstance(manifest.get("components"), list):
        fail(f"{directory}: components must be a list")

    openai_text = (root / "agents/openai.yaml").read_text(encoding="utf-8")
    if f"${expected_name}" not in openai_text:
        fail(f"{directory}: agents/openai.yaml must mention ${expected_name}")
    if not re.search(r"(?m)^\s*allow_implicit_invocation:\s*true\s*$", openai_text):
        fail(f"{directory}: implicit invocation must be enabled")

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            fail(f"{directory}: possible secret file: {path.relative_to(root)}")

    if not directory.endswith("-ru"):
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".json", ".py", ".yaml"}:
                text = path.read_text(encoding="utf-8")
                if re.search(r"[А-Яа-яЁё]", text):
                    fail(f"{directory}: Cyrillic text found in {path.relative_to(root)}")

    subprocess.run(
        [sys.executable, str(root / "scripts/test_package_delivery.py"), "-v"],
        cwd=ROOT,
        check=True,
    )


def validate_plugin_manifests() -> None:
    codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    marketplace = json.loads(
        (ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
    )
    for label, manifest in (("Codex", codex), ("Claude", claude)):
        if manifest.get("name") != "agent-architecture-builder":
            fail(f"{label} plugin has an unexpected name")
        if manifest.get("version") != "2.0.0":
            fail(f"{label} plugin must use version 2.0.0")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        fail("Claude marketplace must contain exactly one plugin")
    if plugins[0].get("name") != "agent-architecture-builder":
        fail("Claude marketplace plugin has an unexpected name")
    if plugins[0].get("source") != "./":
        fail("Claude marketplace plugin source must be ./")


def validate_trigger_cases() -> None:
    cases = json.loads((ROOT / "tests/trigger-cases.json").read_text(encoding="utf-8"))
    if cases.get("schema_version") != 1:
        fail("trigger cases must use schema_version 1")
    for kind in ("positive", "negative"):
        prompts = cases.get(kind)
        if not isinstance(prompts, list) or len(prompts) < 5:
            fail(f"trigger cases need at least five {kind} prompts")
        if not all(isinstance(prompt, str) and prompt.strip() for prompt in prompts):
            fail(f"trigger cases contain an invalid {kind} prompt")


def main() -> int:
    try:
        for legacy in LEGACY_DIRECTORIES:
            if (ROOT / "skills" / legacy).exists():
                fail(f"legacy skill directory still exists: skills/{legacy}")
        for directory, expected_name in EDITIONS.items():
            validate_edition(directory, expected_name)
        validate_plugin_manifests()
        validate_trigger_cases()
    except (RuntimeError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1
    print("Repository validation passed for both universal editions and plugin manifests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
