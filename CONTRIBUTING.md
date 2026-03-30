# Contributing to hatch-calvar-sample

Thank you for considering a contribution. This document covers the development setup, coding standards, and pull request process.

## Development Setup

### Prerequisites

- Python 3.9 or later
- Git
- [pre-commit](https://pre-commit.com/)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/QAToolist/hatch-calvar-sample.git
cd hatch-calvar-sample

# Install in development mode with all dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

Alternatively, use the Makefile:

```bash
make install          # Install in dev mode (generates a dev version)
```

## Running Tests

```bash
# Run all tests
make test

# Run tests with coverage (mirrors CI)
make test-ci

# Run a specific test file
pytest tests/test_version_calc.py -v

# Run a specific test by name
pytest tests/ -k "test_calculate_next_version" -v
```

Coverage must meet the 80% threshold configured in `pyproject.toml`. The CI pipeline enforces this.

## Code Style

This project uses automated formatters and linters enforced through pre-commit hooks.

### Formatters

- **Black** -- code formatting (line length 88)
- **isort** -- import sorting (black-compatible profile)
- **Ruff** -- fast linter covering pycodestyle, pyflakes, bugbear, and more

### Type Checking

- **mypy** with `disallow_untyped_defs = true` for the source package
- The `py.typed` marker is included for PEP 561 compliance

### Running Linters Manually

```bash
# Run all pre-commit hooks on every file
make lint

# Run type checking
make type-check

# Run code complexity analysis
make complexity
```

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`. The configured hooks include:

| Hook | Purpose |
|------|---------|
| trailing-whitespace | Remove trailing whitespace |
| end-of-file-fixer | Ensure files end with a newline |
| check-yaml / check-toml / check-json | Validate config file syntax |
| check-added-large-files | Block files larger than 500 KB |
| detect-private-key | Prevent committing private keys |
| black | Format Python code |
| isort | Sort imports |
| ruff | Lint Python code |
| mypy | Static type checking |
| bandit | Security scanning |

To run hooks manually against all files:

```bash
pre-commit run --all-files
```

To update hook versions:

```bash
pre-commit autoupdate
```

## Pull Request Conventions

1. **Branch from `main`.** Create a feature branch with a descriptive name (e.g., `fix/tag-parsing`, `feat/new-command`).
2. **Keep PRs focused.** One logical change per pull request.
3. **Write tests.** New features and bug fixes should include tests. Aim for the coverage threshold.
4. **Pass CI.** All checks (tests, lint, type-check, security) must pass before merge.
5. **Update CHANGELOG.md.** Add your changes under the `[Unreleased]` section following the existing format.
6. **Use clear commit messages.** Describe the "why" in the first line. Keep it under 72 characters.

### PR Title Format

Use a short, descriptive title. Examples:

- `fix: handle empty tag list in version calculation`
- `feat: add --format flag to calc command`
- `docs: update migration guide for Python 3.13`

## Security

If you discover a security vulnerability, please report it responsibly. See [SECURITY.md](SECURITY.md) for details.

## Project Layout

- `src/hatch_calvar_sample/calver.py` -- core CalVer logic (parsing, validation, calculation)
- `src/hatch_calvar_sample/cli.py` -- CLI entry point and subcommands
- `scripts/calc_version.py` -- standalone script used by CI workflows
- `tests/` -- unit and integration tests
- `docs/` -- extended documentation and guides

## Questions?

Open an issue on [GitHub](https://github.com/QAToolist/hatch-calvar-sample/issues) if you have questions or need help getting started.
