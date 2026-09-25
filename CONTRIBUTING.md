# Contributing to OMERTA

Thank you for your interest in improving OMERTA.

## Ground Rules

- Keep contributions lawful, ethical, and aligned with project scope.
- Keep pull requests focused and small enough to review effectively.
- Do not include credentials, private data, or sensitive investigative material.

## Branch and Commit Expectations

- Branch from `main`.
- Use clear branch names (example: `docs/update-security-guidance`).
- Write concise, descriptive commits.
- Keep unrelated changes in separate commits/PRs.

## Pull Request Expectations

Each PR should include:

- A clear summary of what changed and why
- Any follow-up work that remains intentionally unimplemented
- Validation/test evidence (commands and outcomes)
- Linked issues when applicable

## Code Quality Standards

- Prefer simple, maintainable implementations.
- Avoid speculative features and unsupported claims.
- Update documentation alongside behavior or interface changes.
- Preserve backward compatibility when introducing non-breaking changes is practical.

## Testing Expectations

Before opening a PR, run:

```bash
python scripts/validate_repo.py --root .
python -m unittest discover -s tests -p 'test_*.py'
```

Add or update tests when you change behavior.

## Issue Hygiene

When opening issues:

- Use the provided templates
- Include reproducible steps and expected behavior
- Keep one problem per issue where possible

## Responsible Disclosure

Security vulnerabilities must not be posted in public issues or discussions.

Please follow [`SECURITY.md`](SECURITY.md).
