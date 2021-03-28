from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pytest_insta import SnapshotFixture
from typer.testing import CliRunner

from mcanitexgen import cli


@pytest.fixture
def runner():
    return CliRunner()


class Test_file_arg:
    def test_no_file_arg(self, runner: CliRunner):
        result = runner.invoke(cli.app, "generate", catch_exceptions=False)
        assert result.exit_code != 0
        assert "Missing argument" in result.output

    def test_file_doesnt_exist(self, runner: CliRunner):
        result = runner.invoke(cli.app, "generate doesnt_exist", catch_exceptions=False)

        assert result.exit_code == 2
        assert "does not exist" in result.stdout

    def test_file_is_dir(self, runner: CliRunner):
        result = runner.invoke(
            cli.app, "generate tests/animation/examples", catch_exceptions=False
        )
        assert result.exit_code != 0
        assert "is a directory" in result.output


class Test_out_arg:
    @pytest.mark.parametrize(
        "out, expected_out",
        [
            (".", "."),
            ("build/generated", "build/generated"),
        ],
    )
    def test(self, out, expected_out, runner: CliRunner):
        with patch("mcanitexgen.cli.write_mcmeta_files", new=MagicMock()) as mock_write:
            runner.invoke(
                cli.app, f"generate tests/animation/examples/steve.animation.py {out}"
            )

            mock_write.assert_called_once()
            assert mock_write.call_args_list[0][0][1] == Path(expected_out)

    def test_defaults_to_parent_of_file(self, runner: CliRunner):
        with patch("mcanitexgen.cli.write_mcmeta_files", new=MagicMock()) as mock_write:
            runner.invoke(cli.app, f"generate tests/animation/examples/steve.animation.py")

            mock_write.assert_called_once()
            assert mock_write.call_args_list[0][0][1] == Path("tests/animation/examples")


def test_dry_arg(runner: CliRunner):
    with patch("pathlib.Path.mkdir", new=MagicMock()) as mock_mkdir:
        with patch("mcanitexgen.cli.write_mcmeta_files", new=MagicMock()) as mock_write:
            runner.invoke(
                cli.app, f"generate tests/animation/examples/steve.animation.py --dry"
            )

            mock_mkdir.assert_not_called()
            mock_write.assert_not_called()
