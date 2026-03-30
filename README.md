# hatch-calvar-sample

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-calvar-sample.svg)](https://pypi.org/project/hatch-calvar-sample)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-calvar-sample.svg)](https://pypi.org/project/hatch-calvar-sample)

Sample hatch-based Python project demonstrating **Calendar Versioning (CalVer)** with format `YYYY.MM.DD.MICRO` and automated PyPI release workflows.

## Overview

This project serves as a proof-of-concept and reusable template for implementing CalVer versioning with the hatch build system. It demonstrates:

- **Calendar Versioning (YYYY.MM.DD.MICRO)** calculated from git tags
- **Dynamic versioning** with hatch build system
- **Version checking CLI tool** with multiple commands
- **Automated PyPI release** via GitHub Actions
- **Complete release workflow** automation
- **Strict type checking** with mypy and `py.typed` marker
- **Python 3.9 -- 3.13** support

### Version Format

The project uses CalVer format: `YYYY.MM.DD.MICRO`

- `YYYY` -- 4-digit year (e.g., 2025)
- `MM` -- 2-digit month (01-12)
- `DD` -- 2-digit day (01-31)
- `MICRO` -- Sequential number for releases on the same day (1, 2, 3, ...)

Examples: `2025.01.18.1`, `2025.01.18.2`, `2025.03.15.1`

## Installation

```console
pip install hatch-calvar-sample
```

## Release Workflow

The following diagram shows the fully automated release pipeline:

```mermaid
flowchart LR
    A[PR Merged to main] --> B[auto-tag.yml]
    B -->|Calculates CalVer\nCreates git tag| C[Tag pushed: vYYYY.MM.DD.MICRO]
    C --> D[release.yml]
    D -->|Builds & validates\npackage| E[Publish to PyPI]

    style A fill:#4a90d9,color:#fff
    style B fill:#f5a623,color:#fff
    style C fill:#7b68ee,color:#fff
    style D fill:#f5a623,color:#fff
    style E fill:#50c878,color:#fff
```

**How it works:**

1. You merge a pull request into `main`.
2. `auto-tag.yml` runs, calculates the next CalVer version, and creates a `vYYYY.MM.DD.MICRO` git tag.
3. The tag push triggers `release.yml`, which builds the package, validates it with twine, and publishes to PyPI via Trusted Publishing.
4. CI checks (`ci.yml`) run on every push and PR to ensure tests, linting, security, and type checking pass.

## CLI Tool

The `calver-check` CLI provides commands for version management:

```bash
# Show CLI version
calver-check --version

# Calculate next version
calver-check calc

# Check current version from different sources
calver-check check

# Validate version format
calver-check validate 2025.01.18.1

# Compare two versions
calver-check compare 2025.01.18.1 2025.01.18.2

# Show version information
calver-check info

# Create a git tag for the next version
calver-check tag

# Preview the tag without creating it
calver-check tag --dry-run
```

All commands support `--json` for machine-readable output:

```bash
calver-check calc --json
calver-check tag --dry-run --json
```

## Usage Examples

### Calculating Next Version

```bash
# Using the CLI tool
calver-check calc

# Using the script directly
python scripts/calc_version.py

# With validation
python scripts/calc_version.py --validate --pep440
```

### Creating a Release Tag

```bash
# Preview what tag would be created
calver-check tag --dry-run

# Create the tag locally
calver-check tag

# Push the tag to trigger a release
git push origin v2025.01.18.1
```

### Validating Version Format

```bash
# Valid version
calver-check validate 2025.01.18.1

# Invalid version (exits with error)
calver-check validate 2025.1.18.1
```

### Comparing Versions

```bash
calver-check compare 2025.01.18.1 2025.01.18.2
# Output: 2025.01.18.1 < 2025.01.18.2
```

## Release Process

### Fully Automated (Recommended)

1. Open a pull request with your changes.
2. Merge the pull request to `main`.
3. GitHub Actions automatically:
   - Calculates next CalVer version (e.g., `2025.01.18.1`)
   - Creates tag `v2025.01.18.1`
   - Builds and validates the package
   - Publishes to PyPI

No manual tagging required.

### Manual Release (Hotfixes)

```bash
# Calculate and preview the next tag
calver-check tag --dry-run

# Create and push the tag
calver-check tag
git push origin v2025.01.18.1
```

### Using Makefile

```bash
make version-calc           # Calculate next version
make version-check          # Check current version
make version-validate VERSION=2025.01.18.1
make release-tag            # Create and push release tag (interactive)
make build-test             # Build package for testing
```

## Project Structure

```
hatch-calvar-sample/
├── pyproject.toml              # Hatch configuration with dynamic versioning
├── README.md                   # This file
├── CHANGELOG.md                # Changelog with CalVer format
├── CONTRIBUTING.md             # Contribution guidelines
├── SECURITY.md                 # Security policy
├── LICENSE.txt                 # MIT license
├── Makefile                    # Convenient make targets
├── .pre-commit-config.yaml     # Pre-commit hook configuration
├── .github/
│   └── workflows/
│       ├── ci.yml              # Unified CI (test, lint, type-check, security)
│       ├── auto-tag.yml        # Auto-create tag on PR merge
│       └── release.yml         # Build and publish to PyPI
├── docs/
│   ├── CALVER_MIGRATION_GUIDE.md   # Migrating an existing project to CalVer
│   ├── CALVER_QUICK_START.md       # Quick-start guide for CalVer
│   ├── PYPROJECT_TOML_MIGRATION.md # pyproject.toml migration reference
│   └── PLANNING.md                 # Project planning notes
├── scripts/
│   └── calc_version.py         # Standalone version calculation script
├── src/
│   └── hatch_calvar_sample/
│       ├── __init__.py         # Package with __version__
│       ├── __about__.py        # Version metadata
│       ├── calver.py           # Core CalVer logic (parse, validate, calculate)
│       ├── cli.py              # CLI implementation (calver-check)
│       ├── py.typed            # PEP 561 type marker
│       └── VERSION             # Version file (generated during build)
└── tests/
    ├── test_version_calc.py    # Unit tests for version calculation
    ├── test_version_cli.py     # Unit tests for CLI tool
    └── test_integration.py     # Integration tests
```

## Configuration

### Dynamic Versioning

The project uses hatch's dynamic versioning feature configured in `pyproject.toml`:

```toml
[tool.hatch.version]
path = "src/hatch_calvar_sample/VERSION"
```

The VERSION file is created during the release workflow with the version extracted from the git tag.

### Version Metadata in Code

The package reads version from `importlib.metadata` when installed, with fallbacks:

1. Package metadata (when installed)
2. VERSION file (for development builds)
3. Environment variable `HATCH_CALVER_VERSION`

Access version programmatically:

```python
from hatch_calvar_sample import __version__

print(__version__)  # Output: 2025.01.18.1
```

## Version Calculation Logic

The core logic lives in `src/hatch_calvar_sample/calver.py`:

1. Gets current UTC date (using `datetime.now(timezone.utc)`)
2. Fetches all git tags
3. Parses tags matching the strict CalVer regex (`YYYY.MM.DD.MICRO` with validated month/day ranges)
4. Filters tags with the same date
5. Calculates next MICRO = `max(existing) + 1` or `1` if none exist
6. Returns: `YYYY.MM.DD.MICRO`

### Edge Cases Handled

- No tags -- returns `YYYY.MM.DD.1`
- Multiple tags same date -- increments MICRO correctly
- Date boundary crossing -- resets MICRO to 1 for new date
- Invalid tag formats -- skipped gracefully
- Timezone handling -- uses UTC for consistency

## How to Adapt This Template

This repository is designed as a starting point. Here is what to change when using it for your own project.

### What to Rename

1. **Package name:** Replace `hatch-calvar-sample` and `hatch_calvar_sample` everywhere:
   - `pyproject.toml` -- `[project] name`, `[tool.hatch.version] path`, source paths
   - `src/hatch_calvar_sample/` -- rename the directory
   - `tests/` -- update imports
   - `Makefile` -- update `SRC_DIR`
2. **CLI entry point:** In `pyproject.toml` under `[project.scripts]`, rename `calver-check` to your desired command name.
3. **Author/URL info:** Update `[project] authors` and `[project.urls]` in `pyproject.toml`.

### What to Delete

- `docs/PLANNING.md` -- project-specific planning notes
- `SUGGESTIONS.md` -- internal notes (if present)
- `docs/CALVER_MIGRATION_GUIDE.md` -- only needed if migrating from SemVer
- Sample test data specific to this demo

### What to Configure

- **Python version range:** Adjust `requires-python` and classifier list in `pyproject.toml`.
- **Coverage threshold:** Change `fail_under` in `[tool.coverage.report]` (currently 80%).
- **Linting rules:** Adjust `[tool.ruff]` select/ignore lists as needed.
- **Pre-commit hooks:** Review `.pre-commit-config.yaml` and enable/disable hooks.
- **PyPI Trusted Publishing:** Configure your PyPI project to trust your GitHub repository.

### First Release Checklist

1. Rename the package (see above).
2. Replace this README content with your own.
3. Clear `CHANGELOG.md` entries (keep the format).
4. Push to GitHub and configure PyPI Trusted Publishing.
5. Open and merge your first PR -- the release will happen automatically.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for full development setup and guidelines.

Quick start:

```bash
git clone https://github.com/QAToolist/hatch-calvar-sample.git
cd hatch-calvar-sample
pip install -e ".[dev]"
pre-commit install
make test
```

## Documentation

Detailed guides are in the `docs/` directory:

- [CalVer Quick Start](docs/CALVER_QUICK_START.md) -- get started with CalVer in minutes
- [CalVer Migration Guide](docs/CALVER_MIGRATION_GUIDE.md) -- migrate an existing project from SemVer
- [pyproject.toml Migration](docs/PYPROJECT_TOML_MIGRATION.md) -- reference for pyproject.toml settings

## PEP 440 Compliance

CalVer format `YYYY.MM.DD.MICRO` is PEP 440 compliant as a release segment:

```bash
calver-check validate 2025.01.18.1
```

## Troubleshooting

### Version Not Found

1. Ensure package is installed: `pip install -e .`
2. Check VERSION file exists: `ls src/hatch_calvar_sample/VERSION`
3. Verify git tags: `git tag`

### Build Errors

1. Verify VERSION file exists with valid format
2. Check `pyproject.toml` dynamic version configuration
3. Ensure hatch is installed: `pip install hatchling`

### CLI Not Found

1. Reinstall package: `pip install -e .`
2. Check entry point in `pyproject.toml`
3. Verify PATH includes Python scripts directory

## License

`hatch-calvar-sample` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## References

- [Hatch Documentation](https://hatch.pypa.io/)
- [Calendar Versioning (CalVer)](https://calver.org/)
- [PEP 440 -- Version Identification](https://peps.python.org/pep-0440/)
- [PEP 561 -- Distributing and Packaging Type Information](https://peps.python.org/pep-0561/)
- [GitHub Actions](https://docs.github.com/en/actions)
