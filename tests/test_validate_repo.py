from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.validate_repo import REQUIRED_FILES, run_validation, validate_markdown_links, validate_required_files


class ValidateRepoTests(unittest.TestCase):
    @staticmethod
    def _create_required_files(root: Path) -> None:
        for relative in REQUIRED_FILES:
            file_path = root / relative
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if file_path.exists():
                continue
            content = "# Placeholder\n" if file_path.suffix == ".md" else "placeholder\n"
            file_path.write_text(content, encoding="utf-8")

    def test_missing_required_file_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            errors = validate_required_files(root, required_files=["README.md"])
            self.assertIn("Missing required file: README.md", errors)

    def test_empty_required_file_list_is_respected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self.assertEqual(validate_required_files(root, required_files=[]), [])

    def test_broken_relative_markdown_link_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "doc.md").write_text("[Broken](missing.md)\n", encoding="utf-8")
            errors = validate_markdown_links(root)
            self.assertEqual(errors, ["Broken relative link in doc.md: missing.md"])

    def test_validation_passes_for_existing_required_files_and_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("[Docs](docs.md)\n", encoding="utf-8")
            (root / "docs.md").write_text("# Docs\n", encoding="utf-8")
            self._create_required_files(root)

            errors = run_validation(root)
            self.assertEqual(errors, [])

    def test_out_of_repository_markdown_link_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            outside_file = Path(tmp_dir).parent / "outside.md"
            outside_file.write_text("# Outside\n", encoding="utf-8")
            try:
                (root / "doc.md").write_text("[Outside](../outside.md)\n", encoding="utf-8")
                errors = validate_markdown_links(root)
                self.assertEqual(errors, ["Out-of-repository link in doc.md: ../outside.md"])
            finally:
                if outside_file.exists():
                    outside_file.unlink()

    def test_symlink_target_outside_repository_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            outside_file = Path(tmp_dir).parent / "outside-symlink.md"
            outside_file.write_text("# Outside\n", encoding="utf-8")

            try:
                link_path = root / "safe-link.md"
                try:
                    link_path.symlink_to(outside_file)
                except (NotImplementedError, OSError):
                    self.skipTest("Symlinks are not supported in this environment")

                (root / "doc.md").write_text("[Escaped](safe-link.md)\n", encoding="utf-8")
                errors = validate_markdown_links(root)
                self.assertEqual(errors, ["Out-of-repository link in doc.md: safe-link.md"])
            finally:
                if outside_file.exists():
                    outside_file.unlink()

    def test_directory_link_requires_readme_or_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "doc.md").write_text("[Dir](docs/)\n", encoding="utf-8")
            (root / "docs").mkdir()

            errors = validate_markdown_links(root)
            self.assertEqual(errors, ["Broken relative link in doc.md: docs/"])

            (root / "docs" / "README.md").write_text("# Docs\n", encoding="utf-8")
            self.assertEqual(validate_markdown_links(root), [])

    def test_relative_root_path_is_handled_correctly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "doc.md").write_text("[Docs](docs.md)\n", encoding="utf-8")
            (root / "docs.md").write_text("# Docs\n", encoding="utf-8")
            cwd = Path.cwd()
            try:
                os.chdir(root)
                self.assertEqual(validate_markdown_links(Path(".")), [])
            finally:
                os.chdir(cwd)

    def test_angle_bracket_markdown_link_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "doc.md").write_text("[Docs](<docs.md>)\n", encoding="utf-8")
            (root / "docs.md").write_text("# Docs\n", encoding="utf-8")
            self.assertEqual(validate_markdown_links(root), [])

    def test_cli_rejects_non_directory_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            file_path = root / "file.txt"
            file_path.write_text("data\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/validate_repo.py", "--root", str(file_path)],
                cwd=Path(__file__).resolve().parents[1],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("Invalid --root path", result.stderr)

    def test_protocol_relative_link_is_treated_as_external(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "doc.md").write_text("[External](//example.com/path)\n", encoding="utf-8")
            self.assertEqual(validate_markdown_links(root), [])

    def test_markdown_link_with_parentheses_in_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            target = root / "docs" / "file(1).md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# File\n", encoding="utf-8")
            (root / "doc.md").write_text("[Guide](docs/file(1).md)\n", encoding="utf-8")
            self.assertEqual(validate_markdown_links(root), [])

    def test_any_scheme_link_is_treated_as_external(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "doc.md").write_text("[Phone](tel:+10000000000)\n", encoding="utf-8")
            self.assertEqual(validate_markdown_links(root), [])

    def test_non_utf8_markdown_file_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "doc.md").write_bytes(b"\xff\xfe")
            errors = validate_markdown_links(root)
            self.assertEqual(errors, ["Unreadable markdown file (expected UTF-8): doc.md"])


if __name__ == "__main__":
    unittest.main()
