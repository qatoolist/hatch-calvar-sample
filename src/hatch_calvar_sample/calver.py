"""Core CalVer (YYYY.MM.DD.MICRO) version calculation and validation logic."""

import re
import subprocess
from datetime import datetime, timezone
from typing import Optional

CALVER_PATTERN = re.compile(
    r"^v?(?P<year>\d{4})\."
    r"(?P<month>0[1-9]|1[0-2])\."
    r"(?P<day>0[1-9]|[12]\d|3[01])\."
    r"(?P<micro>\d+)$"
)


def parse_calver_tag(tag: str) -> Optional[tuple[int, int, int, int]]:
    """Parse a CalVer tag string into (year, month, day, micro).

    Supports both 'vYYYY.MM.DD.MICRO' and 'YYYY.MM.DD.MICRO' formats.

    Parameters
    ----------
    tag : str
        Git tag string to parse.

    Returns
    -------
    tuple of (int, int, int, int) or None
        Tuple of (year, month, day, micro) or None if invalid.
    """
    match = CALVER_PATTERN.match(tag.strip())
    if not match:
        return None

    try:
        year = int(match.group("year"))
        month = int(match.group("month"))
        day = int(match.group("day"))
        micro = int(match.group("micro"))

        if micro < 1:
            return None

        return (year, month, day, micro)
    except (ValueError, AttributeError):
        return None


def get_git_tags() -> list[str]:
    """Fetch and return all git tags.

    Returns
    -------
    list of str
        List of tag strings from the git repository.
    """
    try:
        subprocess.run(
            ["git", "fetch", "--tags"],
            capture_output=True,
            check=False,
        )
        result = subprocess.run(
            ["git", "tag"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [tag.strip() for tag in result.stdout.splitlines() if tag.strip()]
    except subprocess.CalledProcessError:
        return []
    except FileNotFoundError:
        return []


def get_current_date() -> tuple[int, int, int]:
    """Get current UTC date as (year, month, day).

    Returns
    -------
    tuple of (int, int, int)
        Tuple of (year, month, day) in UTC.
    """
    now = datetime.now(timezone.utc)
    return (now.year, now.month, now.day)


def calculate_next_version() -> str:
    """Calculate next CalVer version based on git tags and current date.

    Returns
    -------
    str
        Version string in format 'YYYY.MM.DD.MICRO'.
    """
    current_date = get_current_date()
    year, month, day = current_date
    date_prefix = f"{year:04d}.{month:02d}.{day:02d}"

    tags = get_git_tags()
    calver_tags = []

    for tag in tags:
        parsed = parse_calver_tag(tag)
        if parsed:
            calver_tags.append(parsed)

    same_date_tags = [
        (y, m, d, micro) for y, m, d, micro in calver_tags if (y, m, d) == current_date
    ]

    if same_date_tags:
        max_micro = max(micro for _, _, _, micro in same_date_tags)
        next_micro = max_micro + 1
    else:
        next_micro = 1

    return f"{date_prefix}.{next_micro}"


def validate_version_format(version: str) -> bool:
    """Validate CalVer version format.

    Parameters
    ----------
    version : str
        Version string to validate.

    Returns
    -------
    bool
        True if valid CalVer format, False otherwise.
    """
    return parse_calver_tag(version) is not None


def check_pep440_compliance(version: str) -> bool:
    """Check if version is PEP 440 compliant.

    CalVer format YYYY.MM.DD.MICRO is PEP 440 compliant as a release segment.

    Parameters
    ----------
    version : str
        Version string to check.

    Returns
    -------
    bool
        True if PEP 440 compliant, False otherwise.
    """
    if not validate_version_format(version):
        return False

    try:
        from packaging.version import Version

        Version(version)
        return True
    except ImportError:
        return validate_version_format(version)
    except Exception:
        return False
