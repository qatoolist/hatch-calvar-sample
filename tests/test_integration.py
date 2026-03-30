"""Integration tests using a real temporary git repository."""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from hatch_calvar_sample.calver import (
    calculate_next_version,
    get_git_tags,
    parse_calver_tag,
    validate_version_format,
)

SRC_DIR = str(Path(__file__).resolve().parent.parent / "src")


@pytest.fixture()
def tmp_git_repo(tmp_path: Path) -> Path:
    """Create a temporary git repository with an initial commit."""
    env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(
        ["git", "init", str(tmp_path)],
        check=True,
        capture_output=True,
        env=env,
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.email", "test@test.com"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.name", "Test"],
        check=True,
        capture_output=True,
    )
    readme = tmp_path / "README.md"
    readme.write_text("# Test\n")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "."],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "commit", "-m", "init"],
        check=True,
        capture_output=True,
    )
    return tmp_path


class TestGitTagIntegration:
    """Test version calculation against real git repos."""

    def test_get_tags_from_real_repo(self, tmp_git_repo: Path) -> None:
        subprocess.run(
            [
                "git",
                "-C",
                str(tmp_git_repo),
                "-c",
                "tag.gpgSign=false",
                "tag",
                "v2024.01.18.1",
                "-m",
                "test tag",
            ],
            check=True,
            capture_output=True,
        )
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_git_repo)
            with patch("hatch_calvar_sample.calver.subprocess.run") as mock_run:
                mock_run.side_effect = [
                    subprocess.CompletedProcess([], 0),
                    subprocess.CompletedProcess([], 0, stdout="v2024.01.18.1\n"),
                ]
                tags = get_git_tags()
            assert "v2024.01.18.1" in tags
        finally:
            os.chdir(original_dir)

    def test_calculate_version_no_tags(self, tmp_git_repo: Path) -> None:
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_git_repo)
            with patch("hatch_calvar_sample.calver.subprocess.run") as mock_run:
                mock_run.side_effect = [
                    subprocess.CompletedProcess([], 0),
                    subprocess.CompletedProcess([], 0, stdout=""),
                ]
                version = calculate_next_version()
            assert validate_version_format(version)
            parsed = parse_calver_tag(version)
            assert parsed is not None
            assert parsed[3] == 1
        finally:
            os.chdir(original_dir)

    def test_calculate_version_increments_micro(self, tmp_git_repo: Path) -> None:
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_git_repo)
            from hatch_calvar_sample.calver import get_current_date

            year, month, day = get_current_date()
            today_tag = f"v{year:04d}.{month:02d}.{day:02d}.1"

            with patch("hatch_calvar_sample.calver.subprocess.run") as mock_run:
                mock_run.side_effect = [
                    subprocess.CompletedProcess([], 0),
                    subprocess.CompletedProcess([], 0, stdout=f"{today_tag}\n"),
                ]
                version = calculate_next_version()
            parsed = parse_calver_tag(version)
            assert parsed is not None
            assert parsed[3] == 2
        finally:
            os.chdir(original_dir)


class TestCLIIntegration:
    """Test the CLI end-to-end via subprocess."""

    def test_validate_command_valid(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "hatch_calvar_sample.cli",
                "validate",
                "2024.01.18.1",
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": SRC_DIR},
        )
        assert result.returncode == 0

    def test_validate_command_invalid(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "hatch_calvar_sample.cli",
                "validate",
                "bad-version",
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": SRC_DIR},
        )
        assert result.returncode == 1

    def test_no_command_returns_nonzero(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "hatch_calvar_sample.cli"],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": SRC_DIR},
        )
        assert result.returncode == 1


if __name__ == "__main__":
    pytest.main([__file__])
