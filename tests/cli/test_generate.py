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


@pytest.mark.parametrize(
    "out_dir, expected_mcmeta_path",
    [
        ("", "tests/cli/res/steve.png.mcmeta"),
        (".", "steve.png.mcmeta"),
        ("build/generated", "build/generated/steve.png.mcmeta"),
    ],
)
def test_out_dir(out_dir, expected_mcmeta_path, steve_mcmeta, runner: CliRunner):
    with patch("pathlib.Path.mkdir", new=MagicMock()):
        with patch("io.open", new=MagicMock()) as mock_open:
            with patch("json.dump", new=MagicMock()) as mock_dump:
                runner.invoke(cli.app, f"generate tests/cli/res/steve.animation.py {out_dir}")

                mock_open.assert_called_once()
                assert mock_open.call_args_list[0][0][0] == Path(expected_mcmeta_path)

                mock_dump.assert_called_once()
                assert mock_dump.call_args_list[0][0][0] == steve_mcmeta