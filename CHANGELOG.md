# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Calendar Versioning (CalVer)](https://calver.org/) with format `YYYY.MM.DD.MICRO`.

## [Unreleased]

### Added
- Core `calver.py` module in `src/hatch_calvar_sample/` with all version calculation and validation logic (replaces `sys.path` hacking of `scripts/calc_version.py`)
- Python 3.13 support
- CLI `--version` flag to display installed package version
- CLI `tag` subcommand to create git tags locally, with `--dry-run` option
- CLI help text now includes usage examples via `--help`
- `py.typed` marker file for PEP 561 type information distribution
- Stricter mypy configuration with `disallow_untyped_defs = true`
- Integration tests (`tests/test_integration.py`)
- `CONTRIBUTING.md` with development setup, testing, and PR conventions
- `SECURITY.md` with vulnerability reporting policy
- Stricter CalVer regex validation (month 01-12, day 01-31 enforced in pattern)
- Coverage target raised to 80% (`fail_under = 80` in pyproject.toml)

### Changed
- Dropped Python 3.8 support; minimum is now Python 3.9
- Refactored architecture: core version logic moved from `scripts/calc_version.py` into `src/hatch_calvar_sample/calver.py`; CLI imports from the new module
- CI/CD consolidated into unified `ci.yml` workflow (`auto-tag.yml` and `release.yml` remain separate)
- Documentation reorganized into `docs/` directory (`CALVER_MIGRATION_GUIDE.md`, `CALVER_QUICK_START.md`, `PYPROJECT_TOML_MIGRATION.md`, `PLANNING.md`)
- README updated with Mermaid release workflow diagram, "How to Adapt This Template" section, and revised project structure

### Fixed
- Replaced deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)`

### Removed
- Python 3.8 classifier and support
- Build artifacts and empty files from repository
- Direct `sys.path` manipulation for importing `calc_version` in CLI

## [2024.01.18.1] - 2024-01-18

### Added
- Initial implementation of CalVer versioning system
- Version calculation script (`scripts/calc_version.py`)
  - Calculates next CalVer version from git tags
  - Supports both `vYYYY.MM.DD.MICRO` and `YYYY.MM.DD.MICRO` tag formats
  - Validates version format and PEP 440 compliance
- Version checking CLI tool (`calver-check`)
  - `calc` command: Calculate next version
  - `check` command: Check version from multiple sources
  - `validate` command: Validate version format
  - `compare` command: Compare two versions
  - `info` command: Show version information
  - JSON output support for all commands
- Dynamic versioning with hatch
  - VERSION file-based versioning
  - Version reading from `importlib.metadata` with fallbacks
- GitHub Actions release workflow
  - Automated PyPI publishing on tag push
  - Version format validation
  - Package building and validation with twine
- Unit tests for version calculation and CLI
- Comprehensive documentation in README.md
- Makefile with convenient targets for common tasks

### Configuration
- Hatch build system with dynamic versioning
- Python 3.8+ support
- MIT license

[Unreleased]: https://github.com/QAToolist/hatch-calvar-sample/compare/v2024.01.18.1...HEAD
[2024.01.18.1]: https://github.com/QAToolist/hatch-calvar-sample/releases/tag/v2024.01.18.1
