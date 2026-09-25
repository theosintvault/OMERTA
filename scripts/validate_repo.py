#!/usr/bin/env python3
"""Repository validation checks for OMERTA."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Iterable, List
from urllib.parse import urlsplit

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


class MarkdownReadError(Exception):
    """Raised when a markdown file cannot be read safely."""


def collect_markdown_files(root: Path) -> List[Path]:
    return sorted(path for path in root.rglob("*.md") if ".git" not in path.parts)


def validate_required_files(root: Path, required_files: Iterable[str] | None = None) -> List[str]:
    required = REQUIRED_FILES if required_files is None else required_files
    errors: List[str] = []
    for relative_path in required:
        if not (root / relative_path).exists():
            errors.append(f"Missing required file: {relative_path}")
    return errors


def iter_relative_markdown_links(markdown_file: Path) -> Iterable[str]:
    try:
        content = markdown_file.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as error:
        raise MarkdownReadError(str(markdown_file)) from error

    cursor = 0
    while True:
        link_open = content.find("](", cursor)
        if link_open == -1:
            break
        index = link_open + 2
        raw_link = ""

        if index < len(content) and content[index] == "<":
            close_angle = content.find(">", index + 1)
            if close_angle == -1:
                cursor = index
                continue
            raw_link = content[index + 1 : close_angle].strip()
            close_paren = content.find(")", close_angle + 1)
            if close_paren == -1:
                cursor = close_angle + 1
                continue
            cursor = close_paren + 1
        else:
            depth = 1
            start = index
            while index < len(content):
                char = content[index]
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                    if depth == 0:
                        break
                index += 1
            if depth != 0:
                cursor = start
                continue
            raw_link = content[start:index].strip()
            cursor = index + 1

        link = raw_link.split("#", 1)[0].split("?", 1)[0].strip()
        if not link:
            continue
        parsed_link = urlsplit(link)
        if parsed_link.scheme or link.startswith("//"):
            continue
        yield link


def is_within_root(root: Path, target: Path) -> bool:
    root_text = os.path.normcase(str(root))
    target_text = os.path.normcase(str(target))
    try:
        return os.path.commonpath([root_text, target_text]) == root_text
    except ValueError:
        return False


def normalize_lexical_path(path: Path) -> Path:
    return Path(os.path.normpath(str(path)))


def validate_markdown_links(root: Path) -> List[str]:
    root = root.resolve()
    errors: List[str] = []
    for markdown_file in collect_markdown_files(root):
        try:
            links = list(iter_relative_markdown_links(markdown_file))
        except MarkdownReadError:
            relative_source = markdown_file.relative_to(root)
            errors.append(
                f"Unreadable markdown file (expected UTF-8): {relative_source}"
            )
            continue

        for link in links:
            lexical_target = normalize_lexical_path(markdown_file.parent / link)
            resolved_target = lexical_target.resolve()
            if not is_within_root(root, resolved_target):
                relative_source = markdown_file.relative_to(root)
                errors.append(
                    f"Out-of-repository link in {relative_source}: {link}"
                )
                continue
            target = resolved_target
            if target.is_dir():
                readme_target = target / "README.md"
                index_target = target / "index.md"
                if readme_target.exists():
                    target = readme_target
                elif index_target.exists():
                    target = index_target
                else:
                    target = target / "README.md"
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
    if not root.exists() or not root.is_dir():
        print(
            f"Invalid --root path (must be an existing directory): {args.root} -> {root}",
            file=sys.stderr,
        )
        return 2

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
