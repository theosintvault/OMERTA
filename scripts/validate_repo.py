#!/usr/bin/env python3
"""Repository validation checks for OMERTA."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable, List

REQUIRED_FILES = [
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "SUPPORT.md",
    "CHANGELOG.md",
    "LICENSE-CHOICE.md",
    ".editorconfig",
    ".gitignore",
    ".github/workflows/ci.yml",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/feature_request.md",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
]

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def collect_markdown_files(root: Path) -> List[Path]:
    return sorted(path for path in root.rglob("*.md") if ".git" not in path.parts)


def validate_required_files(root: Path, required_files: Iterable[str] = REQUIRED_FILES) -> List[str]:
    errors: List[str] = []
    for relative_path in required_files:
        if not (root / relative_path).exists():
            errors.append(f"Missing required file: {relative_path}")
    return errors


def iter_relative_markdown_links(markdown_file: Path) -> Iterable[str]:
    content = markdown_file.read_text(encoding="utf-8")
    for match in MARKDOWN_LINK_RE.finditer(content):
        raw_link = match.group(1).strip()
        link = raw_link.split("#", 1)[0].split("?", 1)[0].strip()
        if not link:
            continue
        if link.startswith(("http://", "https://", "mailto:", "#")):
            continue
        yield link


def validate_markdown_links(root: Path) -> List[str]:
    errors: List[str] = []
    for markdown_file in collect_markdown_files(root):
        for link in iter_relative_markdown_links(markdown_file):
            target = (markdown_file.parent / link).resolve()
            if not target.exists():
                relative_source = markdown_file.relative_to(root)
                errors.append(
                    f"Broken relative link in {relative_source}: {link}"
                )
    return errors


def run_validation(root: Path) -> List[str]:
    errors: List[str] = []
    errors.extend(validate_required_files(root))
    errors.extend(validate_markdown_links(root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate repository foundation files and links.")
    parser.add_argument("--root", default=".", help="Repository root path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors = run_validation(root)

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
