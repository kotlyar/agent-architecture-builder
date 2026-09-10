#!/usr/bin/env python3
"""Проверяет и упаковывает комплект реализации агентной системы."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path


REQUIRED_FILES = (
    "AGENTS.md",
    "START-HERE.md",
    "IMPLEMENTATION.md",
    "manifest.json",
    "requirements/goal.md",
    "requirements/work-map.md",
    "requirements/constraints.md",
    "architecture/system.md",
    "architecture/decisions.md",
    "architecture/authority.md",
    "architecture/interface-and-storage.md",
    "acceptance/criteria.md",
    "acceptance/scenarios.md",
    "blueprint/AGENTS.md",
    "blueprint/project-tree.md",
    "evidence/sources.md",
    "unresolved.md",
)

FORBIDDEN_NAMES = {
    ".env",
    "auth.json",
    "state.db",
    "id_rsa",
    "id_ed25519",
}

FORBIDDEN_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}


class PackageError(ValueError):
    """Комплект нельзя безопасно упаковать."""


def load_manifest(root: Path) -> dict:
    try:
        data = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PackageError("Отсутствует manifest.json") from exc
    except json.JSONDecodeError as exc:
        raise PackageError(f"Некорректный manifest.json: {exc}") from exc

    required = {
        "schema_version",
        "system_slug",
        "status",
        "target_agents",
        "entrypoint",
        "implementation_instruction",
        "critical_unknowns",
        "profiles",
        "expected_results",
    }
    missing = sorted(required - data.keys())
    if missing:
        raise PackageError("В manifest.json отсутствуют поля: " + ", ".join(missing))
    if data["schema_version"] != 1:
        raise PackageError("Поддерживается только schema_version = 1")
    if data["status"] not in {"готов_к_реализации", "реализован"}:
        raise PackageError("Архив создаётся только для готового комплекта")
    if data["critical_unknowns"]:
        raise PackageError("Список critical_unknowns должен быть пуст")
    if not isinstance(data["target_agents"], list) or not data["target_agents"]:
        raise PackageError("target_agents должен быть непустым списком")
    if not set(data["target_agents"]).issubset({"codex", "hermes"}):
        raise PackageError("target_agents допускает только codex и hermes")
    profiles = data["profiles"]
    if not isinstance(profiles, list) or not profiles:
        raise PackageError("profiles должен быть непустым списком")
    for number, profile in enumerate(profiles, start=1):
        if not isinstance(profile, dict):
            raise PackageError(f"profiles[{number}] должен быть объектом")
        fields = {"slug", "kind", "specification", "distribution"}
        absent = sorted(fields - profile.keys())
        if absent:
            raise PackageError(
                f"В profiles[{number}] отсутствуют поля: " + ", ".join(absent)
            )
    return data


def validate_profiles(root: Path, manifest: dict) -> None:
    distribution_files = (
        "distribution.yaml",
        "SOUL.md",
        "config.yaml",
        "mcp.json",
        ".env.EXAMPLE",
        ".gitignore",
    )
    for profile in manifest["profiles"]:
        specification = root / profile["specification"]
        distribution = root / profile["distribution"]
        if not specification.is_file():
            raise PackageError(f"Нет спецификации профиля: {profile['specification']}")
        missing = [
            name for name in distribution_files if not (distribution / name).is_file()
        ]
        if missing:
            raise PackageError(
                f"Неполный дистрибутив профиля {profile['slug']}: "
                + ", ".join(missing)
            )


def collect_files(root: Path, manifest: dict) -> list[Path]:
    missing = [item for item in REQUIRED_FILES if not (root / item).is_file()]
    if missing:
        raise PackageError("Отсутствуют обязательные файлы: " + ", ".join(missing))
    validate_profiles(root, manifest)

    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise PackageError(f"Символические ссылки запрещены: {path.relative_to(root)}")
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        is_private_env = path.name.startswith(".env.") and path.name != ".env.EXAMPLE"
        is_state_db = path.name.startswith("state.db")
        if (
            path.name in FORBIDDEN_NAMES
            or path.suffix.lower() in FORBIDDEN_SUFFIXES
            or is_private_env
            or is_state_db
        ):
            raise PackageError(f"Обнаружен возможный секрет: {relative}")
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
        raise PackageError(f"Каталог не найден: {root}")
    manifest = load_manifest(root)
    files = collect_files(root, manifest)
    system_slug = str(manifest["system_slug"]).strip()
    if not system_slug or any(char not in "abcdefghijklmnopqrstuvwxyz0123456789-" for char in system_slug):
        raise PackageError("system_slug должен содержать строчные латинские буквы, цифры и дефисы")

    destination = (output or root.with_name(f"{system_slug}-agent-kit.zip")).resolve()
    if destination.is_dir():
        destination = destination / f"{system_slug}-agent-kit.zip"
    if destination.is_relative_to(root):
        raise PackageError("Архив нельзя создавать внутри упаковываемого каталога")
    destination.parent.mkdir(parents=True, exist_ok=True)

    checksum_lines = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        checksum_lines.append(f"{digest(path)}  {relative}")

    prefix = f"{system_slug}-agent-kit"
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            relative = path.relative_to(root).as_posix()
            archive.write(path, f"{prefix}/{relative}")
        archive.writestr(
            f"{prefix}/CHECKSUMS.sha256",
            "\n".join(checksum_lines) + "\n",
        )
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Каталог готового комплекта")
    parser.add_argument("--output", type=Path, help="Путь итогового архива")
    args = parser.parse_args()
    try:
        result = package(args.source, args.output)
    except PackageError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 2
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
