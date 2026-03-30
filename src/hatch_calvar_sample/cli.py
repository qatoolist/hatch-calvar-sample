"""CLI tool for CalVer version management."""

import argparse
import json
import subprocess
import sys
from importlib.metadata import version as _version_func
from typing import Optional, Union

from hatch_calvar_sample.calver import (
    calculate_next_version,
    check_pep440_compliance,
    get_git_tags,
    parse_calver_tag,
    validate_version_format,
)


def get_package_version_from_metadata() -> Optional[str]:
    """Get version from installed package metadata.

    Returns
    -------
    str or None
        Version string or None if not available.
    """
    try:
        return _version_func("hatch-calvar-sample")
    except Exception:
        return None


def version_calc(args: argparse.Namespace) -> int:
    """Calculate next version.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.

    Returns
    -------
    int
        Exit code (0 for success, 1 for error).
    """
    try:
        version = calculate_next_version()
    except Exception as e:
        print(f"Error calculating version: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({"version": version}))
    else:
        print(version)

    return 0


def version_check(args: argparse.Namespace) -> int:
    """Check current version from different sources.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.

    Returns
    -------
    int
        Exit code (0 for success, 1 for error).
    """
    versions = {}

    pkg_version = get_package_version_from_metadata()
    if pkg_version:
        versions["package"] = pkg_version

    git_tags = get_git_tags()
    calver_tags = [tag for tag in git_tags if parse_calver_tag(tag)]
    if calver_tags:
        parsed_tags = [(tag, parse_calver_tag(tag)) for tag in calver_tags]
        parsed_tags.sort(key=lambda x: x[1] or (0, 0, 0, 0), reverse=True)
        latest_tag = parsed_tags[0][0]
        if latest_tag.startswith("v"):
            versions["git_tag"] = latest_tag[1:]
        else:
            versions["git_tag"] = latest_tag

    if args.json:
        print(json.dumps({"versions": versions}, indent=2))
    else:
        if versions:
            print("Current versions:")
            for source, ver in versions.items():
                print(f"  {source}: {ver}")
        else:
            print("No version information found", file=sys.stderr)
            return 1

    return 0


def version_validate(args: argparse.Namespace) -> int:
    """Validate version format.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.

    Returns
    -------
    int
        Exit code (0 for valid, 1 for invalid).
    """
    if not args.version:
        print("Error: version argument required", file=sys.stderr)
        return 1

    version = args.version
    is_valid_format = validate_version_format(version)
    is_pep440 = False
    if is_valid_format:
        is_pep440 = check_pep440_compliance(version)

    if args.json:
        output = {
            "version": version,
            "valid_format": is_valid_format,
            "pep440_compliant": is_pep440,
        }
        print(json.dumps(output))
        return 0 if (is_valid_format and is_pep440) else 1
    else:
        if not is_valid_format:
            print(f"Invalid CalVer format: {version}", file=sys.stderr)
            return 1
        if not is_pep440:
            print(f"Version not PEP 440 compliant: {version}", file=sys.stderr)
            return 1
        print(f"Version '{version}' is valid and PEP 440 compliant")
        return 0


def version_compare(args: argparse.Namespace) -> int:
    """Compare two versions.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.

    Returns
    -------
    int
        Exit code (0 for success, 1 for error).
    """
    if len(args.versions) != 2:
        print("Error: exactly two versions required for comparison", file=sys.stderr)
        return 1

    v1_str, v2_str = args.versions
    v1 = parse_calver_tag(v1_str)
    v2 = parse_calver_tag(v2_str)

    if not v1:
        print(f"Error: invalid version format: {v1_str}", file=sys.stderr)
        return 1
    if not v2:
        print(f"Error: invalid version format: {v2_str}", file=sys.stderr)
        return 1

    if v1 < v2:
        result = "<"
    elif v1 > v2:
        result = ">"
    else:
        result = "=="

    if args.json:
        output = {
            "version1": v1_str,
            "version2": v2_str,
            "comparison": result,
        }
        print(json.dumps(output))
    else:
        print(f"{v1_str} {result} {v2_str}")

    return 0


def version_info(args: argparse.Namespace) -> int:
    """Show version information.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.

    Returns
    -------
    int
        Exit code (0 for success, 1 for error).
    """
    info: dict[str, Union[str, int]] = {}

    try:
        next_version = calculate_next_version()
        parsed = parse_calver_tag(next_version)
        if parsed:
            year, month, day, micro = parsed
            info["next_version"] = next_version
            info["date"] = f"{year:04d}-{month:02d}-{day:02d}"
            info["micro"] = micro
    except Exception as e:
        info["next_version_error"] = str(e)

    pkg_version = get_package_version_from_metadata()
    if pkg_version:
        info["current_package_version"] = pkg_version

    if args.json:
        print(json.dumps(info, indent=2))
    else:
        print("Version Information:")
        for key, value in info.items():
            print(f"  {key}: {value}")

    return 0


def version_tag(args: argparse.Namespace) -> int:
    """Create a git tag for the next CalVer version.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.

    Returns
    -------
    int
        Exit code (0 for success, 1 for error).
    """
    try:
        version = calculate_next_version()
    except Exception as e:
        print(f"Error calculating version: {e}", file=sys.stderr)
        return 1

    tag_name = f"v{version}"

    if args.dry_run:
        if args.json:
            print(json.dumps({"tag": tag_name, "version": version, "dry_run": True}))
        else:
            print(f"Would create tag: {tag_name}")
        return 0

    try:
        subprocess.run(
            ["git", "tag", tag_name],
            capture_output=True,
            text=True,
            check=True,
        )
        if args.json:
            print(json.dumps({"tag": tag_name, "version": version, "created": True}))
        else:
            print(f"Created tag: {tag_name}")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error creating tag: {e.stderr.strip()}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print("Error: git is not available", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CalVer version management CLI",
        prog="calver-check",
        epilog=(
            "Examples:\n"
            "  calver-check calc                              "
            "Calculate next version\n"
            "  calver-check validate 2024.01.18.1             "
            "Validate a version string\n"
            "  calver-check compare 2024.01.18.1 2024.02.01.1 "
            "Compare two versions\n"
            "  calver-check tag --dry-run                     "
            "Preview the next git tag\n"
            "  calver-check tag                               "
            "Create a git tag for next version"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_package_version_from_metadata() or 'unknown'}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # calc command
    calc_parser = subparsers.add_parser("calc", help="Calculate next CalVer version")
    calc_parser.set_defaults(func=version_calc)

    # check command
    check_parser = subparsers.add_parser(
        "check", help="Check current version from different sources"
    )
    check_parser.set_defaults(func=version_check)

    # validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate version format and PEP 440 compliance"
    )
    validate_parser.add_argument("version", help="Version string to validate")
    validate_parser.set_defaults(func=version_validate)

    # compare command
    compare_parser = subparsers.add_parser("compare", help="Compare two versions")
    compare_parser.add_argument("versions", nargs=2, help="Two versions to compare")
    compare_parser.set_defaults(func=version_compare)

    # info command
    info_parser = subparsers.add_parser("info", help="Show version information")
    info_parser.set_defaults(func=version_info)

    # tag command
    tag_parser = subparsers.add_parser(
        "tag", help="Create a git tag for the next CalVer version"
    )
    tag_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what tag would be created without creating it",
    )
    tag_parser.set_defaults(func=version_tag)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    result: int = args.func(args)
    return result


if __name__ == "__main__":
    sys.exit(main())
