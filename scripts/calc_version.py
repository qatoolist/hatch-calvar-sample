#!/usr/bin/env python3
"""Calculate next CalVer version (YYYY.MM.DD.MICRO) from git tags.

This is a thin wrapper around hatch_calvar_sample.calver for use in CI/CD
scripts and GitHub Actions workflows that need standalone version calculation.
"""

import argparse
import sys
from pathlib import Path

# Allow importing from the package source when not installed
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hatch_calvar_sample.calver import (  # noqa: E402
    calculate_next_version,
    check_pep440_compliance,
    validate_version_format,
)

VERSION_FILE = Path(__file__).parent.parent / "src" / "hatch_calvar_sample" / "VERSION"


def write_version(version: str) -> None:
    """Write version to the VERSION file."""
    VERSION_FILE.write_text(f'__version__ = "{version}"\n')
    print(f"Wrote {version} to {VERSION_FILE}")


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Calculate next CalVer version (YYYY.MM.DD.MICRO)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate calculated version format",
    )
    parser.add_argument(
        "--pep440",
        action="store_true",
        help="Check PEP 440 compliance",
    )
    parser.add_argument(
        "--set",
        action="store_true",
        help="Write the calculated version to the VERSION file",
    )
    parser.add_argument(
        "--set-dev",
        action="store_true",
        help="Write CalVer dev version (YYYY.MM.DD.MICRO.dev1) to the VERSION file",
    )
    args = parser.parse_args()

    try:
        version = calculate_next_version()
    except Exception as e:
        print(f"Error calculating version: {e}", file=sys.stderr)
        return 1

    if args.validate:
        if not validate_version_format(version):
            print(f"Invalid version format: {version}", file=sys.stderr)
            return 1

    if args.pep440:
        if not check_pep440_compliance(version):
            print(f"Version not PEP 440 compliant: {version}", file=sys.stderr)
            return 1

    if args.set:
        write_version(version)
    elif args.set_dev:
        write_version(f"{version}.dev1")
    else:
        print(version)

    return 0


if __name__ == "__main__":
    sys.exit(main())
