"""Tests for CalVer version calculation logic."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from hatch_calvar_sample.calver import (
    calculate_next_version,
    check_pep440_compliance,
    get_current_date,
    get_git_tags,
    parse_calver_tag,
    validate_version_format,
)


class TestParseCalverTag:
    """Test CalVer tag parsing."""

    def test_parse_valid_tag_with_v_prefix(self) -> None:
        result = parse_calver_tag("v2024.01.18.1")
        assert result == (2024, 1, 18, 1)

    def test_parse_valid_tag_without_v_prefix(self) -> None:
        result = parse_calver_tag("2024.01.18.1")
        assert result == (2024, 1, 18, 1)

    def test_parse_high_micro_number(self) -> None:
        result = parse_calver_tag("2024.01.18.999")
        assert result == (2024, 1, 18, 999)

    def test_parse_tag_with_whitespace(self) -> None:
        result = parse_calver_tag("  v2024.01.18.1  ")
        assert result == (2024, 1, 18, 1)

    def test_parse_invalid_tag_format(self) -> None:
        assert parse_calver_tag("2024.1.18.1") is None
        assert parse_calver_tag("v1.2.3") is None
        assert parse_calver_tag("2024.01.18") is None
        assert parse_calver_tag("invalid") is None
        assert parse_calver_tag("") is None

    def test_parse_invalid_month_values(self) -> None:
        assert parse_calver_tag("2024.13.18.1") is None
        assert parse_calver_tag("2024.00.18.1") is None

    def test_parse_invalid_day_values(self) -> None:
        assert parse_calver_tag("2024.01.32.1") is None
        assert parse_calver_tag("2024.01.00.1") is None

    def test_parse_invalid_micro(self) -> None:
        assert parse_calver_tag("2024.01.18.0") is None

    def test_parse_boundary_month_values(self) -> None:
        assert parse_calver_tag("2024.01.15.1") == (2024, 1, 15, 1)
        assert parse_calver_tag("2024.12.15.1") == (2024, 12, 15, 1)

    def test_parse_boundary_day_values(self) -> None:
        assert parse_calver_tag("2024.01.01.1") == (2024, 1, 1, 1)
        assert parse_calver_tag("2024.01.31.1") == (2024, 1, 31, 1)


class TestValidateVersionFormat:
    """Test version format validation."""

    def test_validate_valid_versions(self) -> None:
        assert validate_version_format("2024.01.18.1") is True
        assert validate_version_format("v2024.01.18.1") is True
        assert validate_version_format("2024.12.31.999") is True

    def test_validate_invalid_versions(self) -> None:
        assert validate_version_format("2024.1.18.1") is False
        assert validate_version_format("1.2.3") is False
        assert validate_version_format("invalid") is False
        assert validate_version_format("") is False


class TestGetCurrentDate:
    """Test getting current date."""

    def test_get_current_date_format(self) -> None:
        date = get_current_date()
        assert len(date) == 3
        year, month, day = date
        assert isinstance(year, int)
        assert isinstance(month, int)
        assert isinstance(day, int)
        assert 1 <= month <= 12
        assert 1 <= day <= 31

    @patch("hatch_calvar_sample.calver.datetime")
    def test_get_current_date_uses_utc(self, mock_datetime: MagicMock) -> None:
        from datetime import timezone

        mock_now = MagicMock()
        mock_now.year = 2024
        mock_now.month = 6
        mock_now.day = 15
        mock_datetime.now.return_value = mock_now

        get_current_date()
        mock_datetime.now.assert_called_once_with(timezone.utc)


class TestGetGitTags:
    """Test getting git tags."""

    @patch("hatch_calvar_sample.calver.subprocess.run")
    def test_get_git_tags_success(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            stdout="v2024.01.18.1\n2024.01.17.5\ntag1\n", returncode=0
        )
        tags = get_git_tags()
        assert isinstance(tags, list)
        assert len(tags) > 0

    @patch("hatch_calvar_sample.calver.subprocess.run")
    def test_get_git_tags_failure(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")
        tags = get_git_tags()
        assert tags == []

    @patch("hatch_calvar_sample.calver.subprocess.run")
    def test_get_git_tags_git_not_found(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = FileNotFoundError()
        tags = get_git_tags()
        assert tags == []


class TestCalculateNextVersion:
    """Test calculating next version."""

    @patch("hatch_calvar_sample.calver.get_git_tags")
    @patch("hatch_calvar_sample.calver.get_current_date")
    def test_no_existing_tags(self, mock_date: MagicMock, mock_tags: MagicMock) -> None:
        mock_date.return_value = (2024, 1, 18)
        mock_tags.return_value = []
        version = calculate_next_version()
        assert version == "2024.01.18.1"
        assert validate_version_format(version)

    @patch("hatch_calvar_sample.calver.get_git_tags")
    @patch("hatch_calvar_sample.calver.get_current_date")
    def test_tags_same_date_increments(
        self, mock_date: MagicMock, mock_tags: MagicMock
    ) -> None:
        mock_date.return_value = (2024, 1, 18)
        mock_tags.return_value = ["v2024.01.18.1", "v2024.01.18.2"]
        version = calculate_next_version()
        assert version == "2024.01.18.3"

    @patch("hatch_calvar_sample.calver.get_git_tags")
    @patch("hatch_calvar_sample.calver.get_current_date")
    def test_tags_different_date_resets_micro(
        self, mock_date: MagicMock, mock_tags: MagicMock
    ) -> None:
        mock_date.return_value = (2024, 1, 19)
        mock_tags.return_value = ["v2024.01.18.1", "v2024.01.18.5"]
        version = calculate_next_version()
        assert version == "2024.01.19.1"

    @patch("hatch_calvar_sample.calver.get_git_tags")
    @patch("hatch_calvar_sample.calver.get_current_date")
    def test_ignores_invalid_tags(
        self, mock_date: MagicMock, mock_tags: MagicMock
    ) -> None:
        mock_date.return_value = (2024, 1, 18)
        mock_tags.return_value = ["invalid-tag", "v2024.01.18.1", "not-a-version"]
        version = calculate_next_version()
        assert version == "2024.01.18.2"

    @patch("hatch_calvar_sample.calver.get_git_tags")
    @patch("hatch_calvar_sample.calver.get_current_date")
    def test_year_boundary(self, mock_date: MagicMock, mock_tags: MagicMock) -> None:
        mock_date.return_value = (2025, 1, 1)
        mock_tags.return_value = ["v2024.12.31.5"]
        version = calculate_next_version()
        assert version == "2025.01.01.1"

    @patch("hatch_calvar_sample.calver.get_git_tags")
    @patch("hatch_calvar_sample.calver.get_current_date")
    def test_high_micro_number(
        self, mock_date: MagicMock, mock_tags: MagicMock
    ) -> None:
        mock_date.return_value = (2024, 1, 18)
        mock_tags.return_value = ["v2024.01.18.100"]
        version = calculate_next_version()
        assert version == "2024.01.18.101"

    @patch("hatch_calvar_sample.calver.get_git_tags")
    @patch("hatch_calvar_sample.calver.get_current_date")
    def test_mixed_v_prefix_tags(
        self, mock_date: MagicMock, mock_tags: MagicMock
    ) -> None:
        mock_date.return_value = (2024, 1, 18)
        mock_tags.return_value = ["v2024.01.18.1", "2024.01.18.3"]
        version = calculate_next_version()
        assert version == "2024.01.18.4"


class TestPEP440Compliance:
    """Test PEP 440 compliance checking."""

    def test_valid_calver_version(self) -> None:
        result = check_pep440_compliance("2024.01.18.1")
        assert isinstance(result, bool)

    def test_invalid_version_fails(self) -> None:
        result = check_pep440_compliance("not-a-version")
        assert result is False

    def test_empty_string_fails(self) -> None:
        result = check_pep440_compliance("")
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
