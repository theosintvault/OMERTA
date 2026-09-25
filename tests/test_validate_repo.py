from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_repo import run_validation, validate_markdown_links, validate_required_files


class ValidateRepoTests(unittest.TestCase):
    def test_missing_required_file_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            errors = validate_required_files(root, required_files=["README.md"])
            self.assertIn("Missing required file: README.md", errors)

    def test_broken_relative_markdown_link_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "doc.md").write_text("[Broken](missing.md)\n", encoding="utf-8")
            errors = validate_markdown_links(root)
            self.assertEqual(errors, ["Broken relative link in doc.md: missing.md"])

    def test_validation_passes_for_existing_required_files_and_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            required = ["README.md"]
            (root / "README.md").write_text("[Docs](docs.md)\n", encoding="utf-8")
            (root / "docs.md").write_text("# Docs\n", encoding="utf-8")

            errors = run_validation(root)
            self.assertNotEqual(errors, [])

            required_errors = validate_required_files(root, required_files=required)
            link_errors = validate_markdown_links(root)
            self.assertEqual(required_errors, [])
            self.assertEqual(link_errors, [])


if __name__ == "__main__":
    unittest.main()
