from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from mcanitexgen import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def steve_mcmeta():
    return {
        "animation": {
            "interpolate": False,
            "frametime": 1,
            "frames": [
                {"index": 0, "time": 60},
                {"index": 1, "time": 2},
                {"index": 0, "time": 60},
                {"index": 1, "time": 2},
                {"index": 0, "time": 60},
                {"index": 1, "time": 2},
                {"index": 0, "time": 60},
                {"index": 3, "time": 30},
                {"index": 0, "time": 60},
                {"index": 1, "time": 2},
                {"index": 0, "time": 60},
                {"index": 2, "time": 30},
            ],
        }
    }


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
        result = runner.invoke(cli.app, "generate tests/cli/examples", catch_exceptions=False)
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
        with patch("mcanitexgen.generator.write_mcmeta_files", new=MagicMock()) as mock_write:
            runner.invoke(cli.app, f"generate tests/cli/res/steve.animation.py {out}")

            mock_write.assert_called_once()
            assert mock_write.call_args_list[0][0][1] == Path(expected_out)

    def test_defaults_to_parent_of_file(self, runner: CliRunner):
        with patch("mcanitexgen.generator.write_mcmeta_files", new=MagicMock()) as mock_write:
            runner.invoke(cli.app, f"generate tests/cli/res/steve.animation.py")

            mock_write.assert_called_once()
            assert mock_write.call_args_list[0][0][1] == Path("tests/cli/res")
