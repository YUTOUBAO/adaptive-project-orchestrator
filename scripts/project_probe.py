#!/usr/bin/env python3
"""Bounded, metadata-only project inventory for orchestration reconnaissance.

The probe never opens candidate files, invokes Git, follows symlinks, or writes to
its target. It reports directory names and small candidate-file metadata only;
phase inference is deliberately left to the orchestrator.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

DEFAULT_MAX_DEPTH = 3
DEFAULT_MAX_ENTRIES = 2_000
DEFAULT_MAX_CANDIDATES = 300
DEFAULT_MAX_PER_CATEGORY = 80
DEFAULT_MAX_CANDIDATE_BYTES = 2_000_000

HARD_MAX_DEPTH = 6
HARD_MAX_ENTRIES = 10_000
HARD_MAX_CANDIDATES = 1_000
HARD_MAX_PER_CATEGORY = 300
HARD_MAX_CANDIDATE_BYTES = 10_000_000

EXCLUDED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "bower_components",
    "vendor",
    "packages_cache",
    "dist",
    "build",
    "out",
    "target",
    ".next",
    ".nuxt",
    ".output",
    "coverage",
    "logs",
    "log",
    "tmp",
    "temp",
    "uploads",
    "upload",
    "user_uploads",
    "media_uploads",
    "storage",
    "backups",
    "backup",
    "database",
    "databases",
    "db",
    "data",
    ".ssh",
    ".gnupg",
    "secrets",
    ".secrets",
    "credentials",
    "keys",
}

SENSITIVE_FILE_NAMES = {
    ".env",
    ".npmrc",
    ".pypirc",
    ".netrc",
    "credentials",
    "credentials.json",
    "secrets.json",
    "secret.json",
    "id_rsa",
    "id_ed25519",
    "known_hosts",
}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".kdbx", ".jks"}
DATABASE_OR_ARCHIVE_SUFFIXES = {
    ".db",
    ".sqlite",
    ".sqlite3",
    ".mdb",
    ".sql",
    ".dump",
    ".bak",
    ".backup",
    ".zip",
    ".tar",
    ".gz",
    ".tgz",
    ".7z",
}
LOG_SUFFIXES = {".log", ".trace"}

RULE_FILES = {
    "agents.md",
    "claude.md",
    "contributing.md",
    "code_of_conduct.md",
    "codeowners",
    ".cursorrules",
    ".editorconfig",
    "governance.md",
    "project_rules.md",
}
STATUS_FILES = {
    "status.md",
    "project_status.md",
    "progress.md",
    "current_state.md",
    "checkpoint.json",
    "checkpoint.yaml",
    "checkpoint.yml",
    "handoff.md",
    "todo.md",
    "tasks.md",
    "backlog.md",
    "project_profile.yaml",
    "project_profile.yml",
    "project-profile.yaml",
    "project-profile.yml",
}
PLAN_FILES = {
    "plan.md",
    "project_plan.md",
    "roadmap.md",
    "requirements.md",
    "spec.md",
    "brief.md",
    "proposal.md",
    "architecture.md",
    "design.md",
}
DEPENDENCY_FILES = {
    "package.json",
    "package-lock.json",
    "npm-shrinkwrap.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lock",
    "bun.lockb",
    "deno.json",
    "deno.jsonc",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "poetry.lock",
    "pdm.lock",
    "uv.lock",
    "pipfile",
    "pipfile.lock",
    "cargo.toml",
    "cargo.lock",
    "go.mod",
    "go.sum",
    "composer.json",
    "composer.lock",
    "gemfile",
    "gemfile.lock",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
    "gradle.properties",
    "pubspec.yaml",
    "pubspec.lock",
    "mix.exs",
    "mix.lock",
    "makefile",
}
TEST_CONFIG_FILES = {
    "pytest.ini",
    "tox.ini",
    "noxfile.py",
    "jest.config.js",
    "jest.config.ts",
    "vitest.config.js",
    "vitest.config.ts",
    "playwright.config.js",
    "playwright.config.ts",
    "cypress.config.js",
    "cypress.config.ts",
    "phpunit.xml",
    "phpunit.xml.dist",
    "phpunit.xml.example",
    "karma.conf.js",
}
DEPLOYMENT_FILES = {
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "procfile",
    "vercel.json",
    "netlify.toml",
    "render.yaml",
    "fly.toml",
    "app.yaml",
    "serverless.yml",
    "serverless.yaml",
    "cloudbuild.yaml",
    "cloudbuild.yml",
    "skaffold.yaml",
    "helmfile.yaml",
    "terraform.tf",
}
TEXT_PLAN_SUFFIXES = {".md", ".txt", ".rst", ".adoc", ".yaml", ".yml", ".json", ".toml"}
TEST_SOURCE_SUFFIXES = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".php",
    ".rb",
    ".cs",
    ".swift",
}
DEPLOYMENT_PATH_PARTS = {
    ".github",
    "workflows",
    ".gitlab",
    "ci",
    "cd",
    "deploy",
    "deployment",
    "infra",
    "infrastructure",
    "helm",
    "k8s",
    "kubernetes",
    "terraform",
}
TEST_PATH_PARTS = {"test", "tests", "spec", "specs", "e2e", "integration"}


def bounded_int(value: str, *, minimum: int, maximum: int, label: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{label} must be an integer") from exc
    if not minimum <= parsed <= maximum:
        raise argparse.ArgumentTypeError(f"{label} must be between {minimum} and {maximum}")
    return parsed


def is_sensitive_name(name: str) -> bool:
    lower = name.lower()
    if lower in SENSITIVE_FILE_NAMES or lower.startswith(".env."):
        return True
    if Path(lower).suffix in SENSITIVE_SUFFIXES:
        return True
    stem = Path(lower).stem
    return stem in {"secret", "secrets", "credential", "credentials", "passwords", "tokens"}


def is_sensitive_directory_name(name: str) -> bool:
    lower = name.lower()
    normalized = lower
    for separator in (".", "_", "-"):
        normalized = normalized.replace(separator, " ")
    tokens = set(normalized.split())
    return bool(tokens.intersection({"secret", "secrets", "credential", "credentials", "password", "passwords", "token", "tokens"}))


def excluded_file_reason(name: str) -> str | None:
    lower = name.lower()
    suffix = Path(lower).suffix
    if is_sensitive_name(lower):
        return "sensitive_file"
    if suffix in DATABASE_OR_ARCHIVE_SUFFIXES:
        return "database_or_archive"
    if suffix in LOG_SUFFIXES or lower.endswith(".log.json"):
        return "log_file"
    return None


def classify_candidate(relative_path: Path) -> tuple[str, str] | None:
    name = relative_path.name.lower()
    suffix = relative_path.suffix.lower()
    parts = {part.lower() for part in relative_path.parts[:-1]}

    if name in RULE_FILES or (
        name in {"copilot-instructions.md", "instructions.md"}
        and ".github" in parts
    ):
        return "rules", "project or agent instruction candidate"

    if name in STATUS_FILES or (
        suffix in TEXT_PLAN_SUFFIXES
        and any(token in name for token in ("status", "progress", "checkpoint", "handoff"))
    ):
        return "status", "current status, checkpoint, or handoff candidate"

    if name in PLAN_FILES or (
        suffix in TEXT_PLAN_SUFFIXES
        and any(token in name for token in ("roadmap", "plan", "requirement", "proposal", "brief", "specification"))
    ):
        return "plan", "plan, scope, requirement, or decision candidate"

    if name in DEPENDENCY_FILES:
        return "dependency", "dependency or build manifest candidate"

    if name in TEST_CONFIG_FILES:
        return "test", "test configuration candidate"

    test_name = (
        name.startswith("test_")
        or "_test." in name
        or ".test." in name
        or ".spec." in name
    )
    if suffix in TEST_SOURCE_SUFFIXES and (test_name or parts.intersection(TEST_PATH_PARTS)):
        return "test", "test source candidate"

    if name in DEPLOYMENT_FILES:
        return "deployment", "deployment or runtime configuration candidate"

    if parts.intersection(DEPLOYMENT_PATH_PARTS) and suffix in {
        ".yml",
        ".yaml",
        ".json",
        ".toml",
        ".tf",
        ".hcl",
        ".sh",
    }:
        return "deployment", "CI/CD or infrastructure candidate"

    return None


def iso_mtime(stat_result: os.stat_result) -> str:
    return datetime.fromtimestamp(stat_result.st_mtime, tz=timezone.utc).isoformat()


def relative_posix(path: Path, root: Path) -> str:
    relative = path.relative_to(root)
    return "." if not relative.parts else relative.as_posix()


def scan_directory_entries(path: Path, remaining: int) -> tuple[list[os.DirEntry[str]], bool]:
    """Return at most remaining entries without exhausting a huge directory."""
    captured: list[os.DirEntry[str]] = []
    truncated = False
    try:
        with os.scandir(path) as iterator:
            for entry in iterator:
                if len(captured) >= remaining:
                    truncated = True
                    break
                captured.append(entry)
    except OSError:
        raise
    captured.sort(key=lambda item: item.name.casefold())
    return captured, truncated


def probe(
    root: Path,
    *,
    max_depth: int,
    max_entries: int,
    max_candidates: int,
    max_per_category: int,
    max_candidate_bytes: int,
) -> dict[str, Any]:
    directories: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    skipped: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    queue: deque[tuple[Path, int]] = deque([(root, 0)])
    entries_seen = 0
    truncated = False

    while queue and entries_seen < max_entries:
        current, depth = queue.popleft()
        remaining = max_entries - entries_seen
        try:
            entries, local_truncated = scan_directory_entries(current, remaining)
        except OSError as exc:
            errors.append(
                {
                    "path": relative_posix(current, root),
                    "error": exc.__class__.__name__,
                }
            )
            continue

        if local_truncated:
            truncated = True

        for entry in entries:
            entries_seen += 1
            name_lower = entry.name.lower()
            entry_path = Path(entry.path)

            try:
                if entry.is_symlink():
                    skipped["symlink"] += 1
                    continue

                if entry.is_dir(follow_symlinks=False):
                    if name_lower in EXCLUDED_DIR_NAMES or is_sensitive_directory_name(name_lower):
                        skipped["excluded_directory"] += 1
                        continue
                    relative = Path(relative_posix(entry_path, root))
                    child_depth = depth + 1
                    directories.append({"path": relative.as_posix(), "depth": child_depth})
                    if child_depth < max_depth:
                        queue.append((entry_path, child_depth))
                    else:
                        skipped["depth_limit_directory"] += 1
                    continue

                if not entry.is_file(follow_symlinks=False):
                    skipped["special_file"] += 1
                    continue

                exclusion = excluded_file_reason(entry.name)
                if exclusion:
                    skipped[exclusion] += 1
                    continue

                relative = Path(relative_posix(entry_path, root))
                classification = classify_candidate(relative)
                if classification is None:
                    skipped["non_candidate_file"] += 1
                    continue

                category, reason = classification
                if len(candidates) >= max_candidates:
                    skipped["candidate_limit"] += 1
                    truncated = True
                    continue
                if category_counts[category] >= max_per_category:
                    skipped[f"{category}_category_limit"] += 1
                    truncated = True
                    continue

                stat_result = entry.stat(follow_symlinks=False)
                if stat_result.st_size > max_candidate_bytes:
                    skipped["oversize_candidate"] += 1
                    continue

                candidates.append(
                    {
                        "path": relative.as_posix(),
                        "category": category,
                        "reason": reason,
                        "size_bytes": stat_result.st_size,
                        "modified_at": iso_mtime(stat_result),
                    }
                )
                category_counts[category] += 1
            except OSError as exc:
                errors.append(
                    {
                        "path": relative_posix(entry_path, root),
                        "error": exc.__class__.__name__,
                    }
                )

    if queue:
        truncated = True

    candidates.sort(key=lambda item: (item["category"], item["path"].casefold()))
    directories.sort(key=lambda item: item["path"].casefold())
    errors.sort(key=lambda item: item["path"].casefold())

    return {
        "schema_version": 1,
        "probe_mode": "metadata_only_read_only",
        "stage_inference_performed": False,
        "root": str(root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "limits": {
            "max_depth": max_depth,
            "max_entries": max_entries,
            "max_candidates": max_candidates,
            "max_per_category": max_per_category,
            "max_candidate_bytes": max_candidate_bytes,
        },
        "summary": {
            "entries_seen": entries_seen,
            "directories_reported": len(directories),
            "candidates_reported": len(candidates),
            "candidate_categories": dict(sorted(category_counts.items())),
            "skipped": dict(sorted(skipped.items())),
            "errors": len(errors),
            "truncated": truncated,
        },
        "directories": directories,
        "candidates": candidates,
        "errors": errors,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Emit a bounded JSON inventory of project directories and candidate evidence files without reading file contents."
    )
    parser.add_argument("root", nargs="?", default=".", help="project root to inspect")
    parser.add_argument(
        "--max-depth",
        type=lambda value: bounded_int(value, minimum=1, maximum=HARD_MAX_DEPTH, label="max-depth"),
        default=DEFAULT_MAX_DEPTH,
    )
    parser.add_argument(
        "--max-entries",
        type=lambda value: bounded_int(value, minimum=1, maximum=HARD_MAX_ENTRIES, label="max-entries"),
        default=DEFAULT_MAX_ENTRIES,
    )
    parser.add_argument(
        "--max-candidates",
        type=lambda value: bounded_int(value, minimum=1, maximum=HARD_MAX_CANDIDATES, label="max-candidates"),
        default=DEFAULT_MAX_CANDIDATES,
    )
    parser.add_argument(
        "--max-per-category",
        type=lambda value: bounded_int(value, minimum=1, maximum=HARD_MAX_PER_CATEGORY, label="max-per-category"),
        default=DEFAULT_MAX_PER_CATEGORY,
    )
    parser.add_argument(
        "--max-candidate-bytes",
        type=lambda value: bounded_int(
            value,
            minimum=1,
            maximum=HARD_MAX_CANDIDATE_BYTES,
            label="max-candidate-bytes",
        ),
        default=DEFAULT_MAX_CANDIDATE_BYTES,
    )
    parser.add_argument("--pretty", action="store_true", help="pretty-print JSON")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(json.dumps({"error": "root_is_not_a_directory", "root": str(root)}), file=sys.stderr)
        return 2

    result = probe(
        root,
        max_depth=args.max_depth,
        max_entries=args.max_entries,
        max_candidates=args.max_candidates,
        max_per_category=args.max_per_category,
        max_candidate_bytes=args.max_candidate_bytes,
    )
    json.dump(
        result,
        sys.stdout,
        indent=2 if args.pretty else None,
        ensure_ascii=False,
        sort_keys=False,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
