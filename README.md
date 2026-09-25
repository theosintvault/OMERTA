# OMERTA

OMERTA is an investigative intelligence project built by **The OSINT Vault**.

This repository currently provides a production-ready open-source project foundation: governance, security, contribution standards, CI hygiene checks, and validation tooling for future implementation.

## Project Status

**Status: Foundation stage (no operational intelligence features implemented yet).**

OMERTA is being prepared for public development with a focus on quality, safety, and maintainability. Core investigative workflows, connectors, and analysis modules are intentionally not implemented in this initial baseline.

## Purpose

OMERTA is intended to evolve into a structured platform for investigative intelligence workflows that can be audited, tested, and operated responsibly.

## Ethical and Legal Use Boundary

OMERTA must be used only for lawful, authorized, and ethical purposes.

- No unauthorized access, surveillance, or targeting.
- No use that violates privacy, data-protection, or computer-misuse laws.
- No deployment for harassment, discrimination, or abuse.

Users and contributors are responsible for compliance with all applicable laws and regulations in their jurisdiction.

## High-Level Capability Direction (Planned)

The following capability areas are direction-only placeholders and are **not yet implemented**:

- Case and evidence data modeling
- Source connector framework (provider-specific adapters)
- Analyst workflow orchestration
- Reporting and audit trails
- Access controls and role-aware operations

## Architecture Direction

The repository is structured to support incremental implementation:

- `src/` for application code
- `tests/` for automated tests
- `docs/` for project documentation
- `scripts/` for repository maintenance and validation
- `.github/` for templates and CI workflows

## Quick Start

### Prerequisites

- Git
- Python 3.10+

### Validate Repository Foundation

```bash
python scripts/validate_repo.py --root .
python -m unittest discover -s tests -p 'test_*.py'
```

## Configuration

No runtime application configuration is required yet.

Repository-level validation currently supports:

- `--root <path>`: set the repository root for checks

## Usage

At this stage, OMERTA supports repository validation only:

```bash
python scripts/validate_repo.py --root .
```

Output reports missing required files and broken internal relative Markdown links.

## Development Workflow

1. Create a branch from `main`
2. Make focused, testable changes
3. Run local validation and tests
4. Open a pull request with clear scope and rationale

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for full standards.

## Testing

Current automated checks:

- Unit tests in `tests/`
- Repository validation checks via `scripts/validate_repo.py`
- CI workflow in `.github/workflows/ci.yml`

## Security Reporting

Do **not** report vulnerabilities in public issues.

See [`SECURITY.md`](SECURITY.md) for responsible disclosure instructions.

## Contributing

Contributions are welcome once aligned with project standards.

Please read:

- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
- [`SUPPORT.md`](SUPPORT.md)

## License Status

A final open-source license has not been selected yet.

See [`LICENSE-CHOICE.md`](LICENSE-CHOICE.md) before distributing, forking, or reusing this project.

## Roadmap

- [x] Foundation repository hygiene and governance baseline
- [ ] Initial technical design documents for core modules
- [ ] First implementation milestones for source/tested application code
- [ ] Security hardening and release process definition

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md).
