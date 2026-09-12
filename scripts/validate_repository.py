#!/usr/bin/env python3
"""Validate the universal bilingual skill, plugins, and packaging contract."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_VERSION = "2.3.0"
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
    "references/agent-building-resources.md",
    "references/skill-discovery-and-reuse.md",
    "references/startup-readiness.md",
    "references/component-contracts.md",
    "references/web-interface-stack.md",
    "references/platforms/codex.md",
    "references/platforms/claude-code.md",
    "references/platforms/hermes.md",
    "assets/IMPLEMENTER-RULES.template.md",
    "assets/IMPLEMENTATION.template.md",
    "assets/manifest.template.json",
    "assets/component-contract.template.json",
    "assets/skill-reuse.template.json",
    "assets/startup-readiness.template.json",
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
PARITY_REFERENCES = {
    "references/skill-discovery-and-reuse.md": {
        "reuse.need",
        "reuse.sources",
        "reuse.compare",
        "reuse.record",
    },
    "references/component-contracts.md": {
        "contract.common",
        "contract.by-kind",
        "contract.adapter",
    },
    "references/discovery-interview.md": {
        "progress.stage-map",
    },
    "references/control-interface-and-storage.md": {
        "control.interface.conversation",
        "control.interface.command-line",
        "control.interface.browser",
        "control.interface.api",
        "control.interface.notifications",
        "control.interface.combination",
        "control.storage.files",
        "control.storage.sqlite",
        "control.storage.postgresql",
        "control.storage.vector-search",
        "control.storage.no-new-database",
        "control.persistent-state",
        "control.external-action-record",
        "control.unknown-result",
        "control.decision-record",
    },
    "references/web-interface-stack.md": {
        "web.default-stack",
        "web.optional-libraries",
        "web.prototype",
        "web.cost",
        "web.required-views",
        "web.required-states",
        "web.safety",
        "web.boundary",
        "web.do-not-build",
        "web.readiness",
    },
    "references/startup-readiness.md": {
        "startup.two-states",
        "startup.contract",
        "startup.gate",
        "startup.persistent",
        "startup.acceptance",
    },
}
PARITY_MARKER = re.compile(r"<!--\s*parity:([a-z0-9.-]+)\s*-->")
CRITICAL_CONTRACT_TERMS = {
    "references/discovery-interview.md": {
        "English": (
            "gate `d1` passes",
            "gate `d2` passes",
            "gate `d3` passes",
            "gates `d1–d4` all pass",
            "gates `r3–r5`",
            "gates `r6–r10`",
            "load `architecture-decisions.md`",
            "then `delivery-package.md`",
        ),
        "Russian": (
            "условие `d1`",
            "условие `d2`",
            "условие `d3`",
            "условия `d1–d4`",
            "условия `r3–r5`",
            "условия `r6–r10`",
            "загрузить `architecture-decisions.md`",
            "затем `delivery-package.md`",
        ),
    },
    "references/control-interface-and-storage.md": {
        "English": (
            "at least one of these requirements is confirmed",
            "no separate database",
            "exact target and account",
            "idempotency key",
            "result_unknown",
            "never retry an action with an unknown result until state has been checked",
            "one authoritative source",
        ),
        "Russian": (
            "хотя бы одно обязательное условие",
            "новая база данных не требуется",
            "точную цель и учётную запись",
            "ключ идемпотентности",
            "result_unknown",
            "не повторяй действие с неизвестным результатом, пока состояние не проверено",
            "единственный источник истины",
        ),
    },
    "references/web-interface-stack.md": {
        "English": (
            "current stable releases",
            "no paid component library or mandatory commercial cloud service",
            "approved for exact parameters",
            "result unknown",
            "cancelled or expired",
            "exact target, account, action",
            "editing an approved proposal invalidates that approval",
            "server-side authorization must enforce permissions",
            "secrets must never appear",
            "make stale status visible",
            "approval, cancellation, failure, unknown result, and recovery are tested separately",
        ),
        "Russian": (
            "актуальные стабильные версии",
            "без платной библиотеки компонентов и обязательной коммерческой облачной службы",
            "подтверждено для точных параметров",
            "результат неизвестен",
            "отменено или срок подтверждения истёк",
            "точную цель, учётную запись, действие",
            "изменение подтверждённой версии отменяет прежнее подтверждение",
            "проверяются права на сервере",
            "секреты и ключи доступа не передаются",
            "явно обозначать устаревшее состояние",
            "подтверждение, отмена, ошибка, неизвестный результат и восстановление проверены отдельно",
        ),
    },
    "references/startup-readiness.md": {
        "English": (
            "remains `blocked` until its runtime dependencies pass their checks",
            "never ask a person to paste a secret value into chat",
            "permits only setup guidance and safe diagnostics",
            "for codex this is a section in `agents.md`",
            "not because the agent claims it is ready",
        ),
        "Russian": (
            "остаётся в состоянии `blocked`",
            "не проси человека вставлять значение секрета в чат",
            "разрешает только объяснение настройки и безопасную диагностику",
            "для codex это раздел в `agents.md`",
            "не по тому, что агент сообщил о готовности словами",
        ),
    },
}


def fail(message: str) -> None:
    raise RuntimeError(message)


def frontmatter_value(text: str, key: str) -> str | None:
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    frontmatter = parts[1]
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*(.+?)\s*$", frontmatter)
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
    if frontmatter_value(skill_text, "version") != RELEASE_VERSION:
        fail(f"{directory}: SKILL.md must use version {RELEASE_VERSION}")
    if DOMAIN_TERMS.search(description) or "Hermes" in description:
        fail(f"{directory}: description must stay domain- and platform-neutral")

    manifest = json.loads(
        (root / "assets/manifest.template.json").read_text(encoding="utf-8")
    )
    if manifest.get("schema_version") != 4:
        fail(f"{directory}: manifest template must use schema_version 4")
    expected_status = "черновик" if directory.endswith("-ru") else "draft"
    if manifest.get("status") != expected_status:
        fail(f"{directory}: unexpected manifest template status")
    if not isinstance(manifest.get("target_platforms"), list):
        fail(f"{directory}: target_platforms must be a list")
    if not isinstance(manifest.get("components"), list):
        fail(f"{directory}: components must be a list")
    if manifest.get("skill_reuse") != "reuse/skills.json":
        fail(f"{directory}: manifest template must reference reuse/skills.json")
    if manifest.get("startup_readiness") != "requirements/startup-readiness.json":
        fail(
            f"{directory}: manifest template must reference "
            "requirements/startup-readiness.json"
        )
    for component in manifest["components"]:
        if not component.get("contract"):
            fail(f"{directory}: every manifest component needs a contract")

    required_sections = (
        "## Select a route" if not directory.endswith("-ru") else "## Выбор маршрута",
        "## Work map" if not directory.endswith("-ru") else "## Карта работы",
    )
    for section in required_sections:
        if section not in skill_text:
            fail(f"{directory}: structured skill section is missing: {section}")

    openai_text = (root / "agents/openai.yaml").read_text(encoding="utf-8")
    for field in ("display_name", "short_description", "default_prompt"):
        if not re.search(rf"(?m)^\s*{field}:\s*\".+\"\s*$", openai_text):
            fail(f"{directory}: agents/openai.yaml must define {field}")
    if f"${expected_name}" not in openai_text:
        fail(f"{directory}: agents/openai.yaml must mention ${expected_name}")
    if not re.search(r"(?m)^\s*allow_implicit_invocation:\s*true\s*$", openai_text):
        fail(f"{directory}: implicit invocation must be enabled")

    if not re.search(r'(?m)^argument-hint:\s*".+"\s*$', skill_text):
        fail(f"{directory}: Claude Code argument-hint must be defined")

    resource_text = (root / "references/agent-building-resources.md").read_text(
        encoding="utf-8"
    )
    agent_resources = (
        "https://www.anthropic.com/engineering/building-effective-agents",
        "https://www.anthropic.com/research/multiagent-systems",
        "https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills",
        "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents",
        "https://www.anthropic.com/engineering/writing-tools-for-agents",
        "https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents",
        "https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents",
        "https://github.com/karpathy/autoresearch",
        "https://ouroboros-agent.ai/paper/",
    )
    for resource in agent_resources:
        if resource not in resource_text:
            fail(f"{directory}: missing agent-building resource: {resource}")

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


def validate_critical_contracts() -> None:
    english = ROOT / "skills" / "agent-architecture-builder"
    russian = ROOT / "skills" / "agent-architecture-builder-ru"
    for relative, expected in PARITY_REFERENCES.items():
        texts = {
            "English": (english / relative).read_text(encoding="utf-8"),
            "Russian": (russian / relative).read_text(encoding="utf-8"),
        }
        for label, content in texts.items():
            actual = set(PARITY_MARKER.findall(content))
            if actual != expected:
                missing = sorted(expected - actual)
                unexpected = sorted(actual - expected)
                fail(
                    f"{label} {relative}: structural parity markers differ; "
                    f"missing={missing}, unexpected={unexpected}"
                )

    roots = {"English": english, "Russian": russian}
    for relative, editions in CRITICAL_CONTRACT_TERMS.items():
        for label, required_terms in editions.items():
            path = roots[label] / relative
            content = " ".join(path.read_text(encoding="utf-8").lower().split())
            missing = [term for term in required_terms if term not in content]
            if missing:
                fail(
                    f"{label} {relative}: critical contract terms are missing: "
                    f"{missing}"
                )

    logical_criteria = {
        "English": (
            english / "references/control-interface-and-storage.md",
            "these conditions hold together",
        ),
        "Russian": (
            russian / "references/control-interface-and-storage.md",
            "одновременно выполняются условия",
        ),
    }
    for label, (path, phrase) in logical_criteria.items():
        content = " ".join(path.read_text(encoding="utf-8").lower().split())
        if content.count(phrase) < 4:
            fail(f"{label} control criteria must state four all-condition choices")


def validate_plugin_manifests() -> None:
    codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    marketplace = json.loads(
        (ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
    )
    for label, manifest in (("Codex", codex), ("Claude", claude)):
        if manifest.get("name") != "agent-architecture-builder":
            fail(f"{label} plugin has an unexpected name")
        if manifest.get("version") != RELEASE_VERSION:
            fail(f"{label} plugin must use version {RELEASE_VERSION}")
    if claude.get("displayName") != "Agent Architecture Builder":
        fail("Claude plugin must define its human-readable displayName")
    if marketplace.get("version") != RELEASE_VERSION:
        fail(f"Claude marketplace must use version {RELEASE_VERSION}")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        fail("Claude marketplace must contain exactly one plugin")
    if plugins[0].get("name") != "agent-architecture-builder":
        fail("Claude marketplace plugin has an unexpected name")
    if plugins[0].get("source") != "./":
        fail("Claude marketplace plugin source must be ./")
    if plugins[0].get("version") != RELEASE_VERSION:
        fail(f"Claude marketplace plugin must use version {RELEASE_VERSION}")
    if plugins[0].get("displayName") != "Agent Architecture Builder":
        fail("Claude marketplace plugin must define its displayName")


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
        validate_critical_contracts()
        validate_plugin_manifests()
        validate_trigger_cases()
    except (RuntimeError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1
    print("Repository validation passed for both universal editions and plugin manifests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
