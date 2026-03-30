"""Tests for version checking CLI tool."""

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from hatch_calvar_sample import cli


class TestVersionCalc:
    """Test version calculation command."""

    @patch("hatch_calvar_sample.cli.calculate_next_version")
    def test_success(self, mock_calc: MagicMock) -> None:
        mock_calc.return_value = "2024.01.18.1"
        args = MagicMock()
        args.json = False
        assert cli.version_calc(args) == 0

    @patch("hatch_calvar_sample.cli.calculate_next_version")
    def test_json_output(
        self, mock_calc: MagicMock, capsys: pytest.CaptureFixture
    ) -> None:
        mock_calc.return_value = "2024.01.18.1"
        args = MagicMock()
        args.json = True
        assert cli.version_calc(args) == 0
        output = json.loads(capsys.readouterr().out)
        assert output["version"] == "2024.01.18.1"

    @patch("hatch_calvar_sample.cli.calculate_next_version")
    def test_error_handling(self, mock_calc: MagicMock) -> None:
        mock_calc.side_effect = RuntimeError("git failed")
        args = MagicMock()
        args.json = False
        assert cli.version_calc(args) == 1


class TestVersionCheck:
    """Test version check command."""

    @patch("hatch_calvar_sample.cli.get_package_version_from_metadata")
    @patch("hatch_calvar_sample.cli.get_git_tags")
    def test_with_package_version(
        self, mock_tags: MagicMock, mock_pkg_version: MagicMock
    ) -> None:
        mock_pkg_version.return_value = "2024.01.18.1"
        mock_tags.return_value = []
        args = MagicMock()
        args.json = False
        assert cli.version_check(args) == 0

    @patch("hatch_calvar_sample.cli.get_package_version_from_metadata")
    @patch("hatch_calvar_sample.cli.get_git_tags")
    def test_no_versions_found(
        self, mock_tags: MagicMock, mock_pkg_version: MagicMock
    ) -> None:
        mock_pkg_version.return_value = None
        mock_tags.return_value = []
        args = MagicMock()
        args.json = False
        assert cli.version_check(args) == 1

    @patch("hatch_calvar_sample.cli.get_package_version_from_metadata")
    @patch("hatch_calvar_sample.cli.get_git_tags")
    def test_json_output(
        self,
        mock_tags: MagicMock,
        mock_pkg_version: MagicMock,
        capsys: pytest.CaptureFixture,
    ) -> None:
        mock_pkg_version.return_value = "2024.01.18.1"
        mock_tags.return_value = ["v2024.01.18.1"]
        args = MagicMock()
        args.json = True
        assert cli.version_check(args) == 0
        output = json.loads(capsys.readouterr().out)
        assert "versions" in output

    @patch("hatch_calvar_sample.cli.get_package_version_from_metadata")
    @patch("hatch_calvar_sample.cli.get_git_tags")
    def test_with_git_tags(
        self, mock_tags: MagicMock, mock_pkg_version: MagicMock
    ) -> None:
        mock_pkg_version.return_value = None
        mock_tags.return_value = ["v2024.01.18.2", "v2024.01.18.1"]
        args = MagicMock()
        args.json = False
        assert cli.version_check(args) == 0


class TestVersionValidate:
    """Test version validate command."""

    @patch("hatch_calvar_sample.cli.validate_version_format")
    @patch("hatch_calvar_sample.cli.check_pep440_compliance")
    def test_valid_version(
        self, mock_pep440: MagicMock, mock_validate: MagicMock
    ) -> None:
        mock_validate.return_value = True
        mock_pep440.return_value = True
        args = MagicMock()
        args.version = "2024.01.18.1"
        args.json = False
        assert cli.version_validate(args) == 0

    @patch("hatch_calvar_sample.cli.validate_version_format")
    def test_invalid_format(self, mock_validate: MagicMock) -> None:
        mock_validate.return_value = False
        args = MagicMock()
        args.version = "invalid"
        args.json = False
        assert cli.version_validate(args) == 1

    def test_missing_version(self) -> None:
        args = MagicMock()
        args.version = None
        assert cli.version_validate(args) == 1

    @patch("hatch_calvar_sample.cli.validate_version_format")
    @patch("hatch_calvar_sample.cli.check_pep440_compliance")
    def test_json_output_valid(
        self,
        mock_pep440: MagicMock,
        mock_validate: MagicMock,
        capsys: pytest.CaptureFixture,
    ) -> None:
        mock_validate.return_value = True
        mock_pep440.return_value = True
        args = MagicMock()
        args.version = "2024.01.18.1"
        args.json = True
        assert cli.version_validate(args) == 0
        output = json.loads(capsys.readouterr().out)
        assert output["valid_format"] is True
        assert output["pep440_compliant"] is True


class TestVersionCompare:
    """Test version compare command."""

    @patch("hatch_calvar_sample.cli.parse_calver_tag")
    def test_less_than(self, mock_parse: MagicMock) -> None:
        mock_parse.side_effect = [(2024, 1, 18, 1), (2024, 1, 18, 2)]
        args = MagicMock()
        args.versions = ["2024.01.18.1", "2024.01.18.2"]
        args.json = False
        assert cli.version_compare(args) == 0

    @patch("hatch_calvar_sample.cli.parse_calver_tag")
    def test_equal(self, mock_parse: MagicMock) -> None:
        mock_parse.return_value = (2024, 1, 18, 1)
        args = MagicMock()
        args.versions = ["2024.01.18.1", "2024.01.18.1"]
        args.json = False
        assert cli.version_compare(args) == 0

    @patch("hatch_calvar_sample.cli.parse_calver_tag")
    def test_greater_than(
        self, mock_parse: MagicMock, capsys: pytest.CaptureFixture
    ) -> None:
        mock_parse.side_effect = [(2024, 2, 1, 1), (2024, 1, 18, 1)]
        args = MagicMock()
        args.versions = ["2024.02.01.1", "2024.01.18.1"]
        args.json = False
        assert cli.version_compare(args) == 0
        assert ">" in capsys.readouterr().out

    @patch("hatch_calvar_sample.cli.parse_calver_tag")
    def test_invalid_version(self, mock_parse: MagicMock) -> None:
        mock_parse.side_effect = [(2024, 1, 18, 1), None]
        args = MagicMock()
        args.versions = ["2024.01.18.1", "invalid"]
        args.json = False
        assert cli.version_compare(args) == 1

    def test_wrong_number_of_versions(self) -> None:
        args = MagicMock()
        args.versions = ["2024.01.18.1"]
        assert cli.version_compare(args) == 1

    @patch("hatch_calvar_sample.cli.parse_calver_tag")
    def test_json_output(
        self, mock_parse: MagicMock, capsys: pytest.CaptureFixture
    ) -> None:
        mock_parse.side_effect = [(2024, 1, 18, 1), (2024, 1, 18, 2)]
        args = MagicMock()
        args.versions = ["2024.01.18.1", "2024.01.18.2"]
        args.json = True
        assert cli.version_compare(args) == 0
        output = json.loads(capsys.readouterr().out)
        assert output["comparison"] == "<"


class TestVersionInfo:
    """Test version info command."""

    @patch("hatch_calvar_sample.cli.calculate_next_version")
    @patch("hatch_calvar_sample.cli.get_package_version_from_metadata")
    def test_success(self, mock_pkg_version: MagicMock, mock_calc: MagicMock) -> None:
        mock_calc.return_value = "2024.01.18.2"
        mock_pkg_version.return_value = "2024.01.18.1"
        args = MagicMock()
        args.json = False
        assert cli.version_info(args) == 0

    @patch("hatch_calvar_sample.cli.calculate_next_version")
    @patch("hatch_calvar_sample.cli.get_package_version_from_metadata")
    def test_json_output(
        self,
        mock_pkg_version: MagicMock,
        mock_calc: MagicMock,
        capsys: pytest.CaptureFixture,
    ) -> None:
        mock_calc.return_value = "2024.01.18.2"
        mock_pkg_version.return_value = "2024.01.18.1"
        args = MagicMock()
        args.json = True
        assert cli.version_info(args) == 0
        output = json.loads(capsys.readouterr().out)
        assert "next_version" in output

    @patch("hatch_calvar_sample.cli.calculate_next_version")
    @patch("hatch_calvar_sample.cli.get_package_version_from_metadata")
    def test_calc_error_handled(
        self, mock_pkg_version: MagicMock, mock_calc: MagicMock
    ) -> None:
        mock_calc.side_effect = RuntimeError("git error")
        mock_pkg_version.return_value = None
        args = MagicMock()
        args.json = False
        assert cli.version_info(args) == 0


class TestVersionTag:
    """Test version tag command."""

    @patch("hatch_calvar_sample.cli.calculate_next_version")
    def test_dry_run(self, mock_calc: MagicMock, capsys: pytest.CaptureFixture) -> None:
        mock_calc.return_value = "2024.01.18.1"
        args = MagicMock()
        args.dry_run = True
        args.json = False
        assert cli.version_tag(args) == 0
        assert "Would create tag" in capsys.readouterr().out

    @patch("hatch_calvar_sample.cli.calculate_next_version")
    def test_dry_run_json(
        self, mock_calc: MagicMock, capsys: pytest.CaptureFixture
    ) -> None:
        mock_calc.return_value = "2024.01.18.1"
        args = MagicMock()
        args.dry_run = True
        args.json = True
        assert cli.version_tag(args) == 0
        output = json.loads(capsys.readouterr().out)
        assert output["dry_run"] is True
        assert output["tag"] == "v2024.01.18.1"

    @patch("hatch_calvar_sample.cli.subprocess.run")
    @patch("hatch_calvar_sample.cli.calculate_next_version")
    def test_create_tag_success(
        self,
        mock_calc: MagicMock,
        mock_run: MagicMock,
        capsys: pytest.CaptureFixture,
    ) -> None:
        mock_calc.return_value = "2024.01.18.1"
        mock_run.return_value = MagicMock(returncode=0)
        args = MagicMock()
        args.dry_run = False
        args.json = False
        assert cli.version_tag(args) == 0
        assert "Created tag" in capsys.readouterr().out

    @patch("hatch_calvar_sample.cli.subprocess.run")
    @patch("hatch_calvar_sample.cli.calculate_next_version")
    def test_create_tag_failure(
        self, mock_calc: MagicMock, mock_run: MagicMock
    ) -> None:
        mock_calc.return_value = "2024.01.18.1"
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git", stderr="tag already exists"
        )
        args = MagicMock()
        args.dry_run = False
        args.json = False
        assert cli.version_tag(args) == 1

    @patch("hatch_calvar_sample.cli.calculate_next_version")
    def test_calc_error(self, mock_calc: MagicMock) -> None:
        mock_calc.side_effect = RuntimeError("git failed")
        args = MagicMock()
        args.dry_run = False
        args.json = False
        assert cli.version_tag(args) == 1


class TestMainCLI:
    """Test CLI argument parsing and main entry point."""

    def test_no_command_shows_help(self) -> None:
        with patch("sys.argv", ["calver-check"]):
            assert cli.main() == 1

    @patch("hatch_calvar_sample.cli.calculate_next_version")
    def test_calc_command_parsing(self, mock_calc: MagicMock) -> None:
        mock_calc.return_value = "2024.01.18.1"
        with patch("sys.argv", ["calver-check", "calc"]):
            assert cli.main() == 0

    @patch("hatch_calvar_sample.cli.calculate_next_version")
    def test_calc_with_json_flag(self, mock_calc: MagicMock) -> None:
        mock_calc.return_value = "2024.01.18.1"
        with patch("sys.argv", ["calver-check", "--json", "calc"]):
            assert cli.main() == 0

    @patch("hatch_calvar_sample.cli.validate_version_format")
    @patch("hatch_calvar_sample.cli.check_pep440_compliance")
    def test_validate_command_parsing(
        self, mock_pep440: MagicMock, mock_validate: MagicMock
    ) -> None:
        mock_validate.return_value = True
        mock_pep440.return_value = True
        with patch("sys.argv", ["calver-check", "validate", "2024.01.18.1"]):
            assert cli.main() == 0

    @patch("hatch_calvar_sample.cli.parse_calver_tag")
    def test_compare_command_parsing(self, mock_parse: MagicMock) -> None:
        mock_parse.side_effect = [(2024, 1, 18, 1), (2024, 1, 18, 2)]
        with patch(
            "sys.argv",
            ["calver-check", "compare", "2024.01.18.1", "2024.01.18.2"],
        ):
            assert cli.main() == 0

    @patch("hatch_calvar_sample.cli.calculate_next_version")
    def test_tag_dry_run_parsing(self, mock_calc: MagicMock) -> None:
        mock_calc.return_value = "2024.01.18.1"
        with patch("sys.argv", ["calver-check", "tag", "--dry-run"]):
            assert cli.main() == 0


if __name__ == "__main__":
    pytest.main([__file__])
