from contextlib import contextmanager
from io import TextIOWrapper
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from mcanitexgen import __main__ as cli


@pytest.fixture
def runner():
    return CliRunner()


class Test_generate:
    @pytest.fixture
    def steve_mcmeta(self):
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

    def test_animation_file_doesnt_exist(self, runner: CliRunner):
        result = runner.invoke(cli.app, "generate doesnt_exist")

        assert result.exit_code == 2
        assert "does not exist" in result.stdout

    @pytest.mark.parametrize(
        "out_dir, expected_mcmeta_path",
        [
            ("", "tests/cli/res/steve.png.mcmeta"),
            (".", "steve.png.mcmeta"),
            ("build/generated", "build/generated/steve.png.mcmeta"),
        ],
    )
    def test_out_dir(self, out_dir, expected_mcmeta_path, steve_mcmeta, runner: CliRunner):
        with patch("pathlib.Path.mkdir", new=MagicMock()):
            with patch("io.open", new=MagicMock()) as mock_open:
                with patch("json.dump", new=MagicMock()) as mock_dump:
                    runner.invoke(
                        cli.app, f"generate tests/cli/res/steve.animation.py {out_dir}"
                    )

                    mock_open.assert_called_once()
                    assert mock_open.call_args_list[0][0][0] == Path(expected_mcmeta_path)

                    mock_dump.assert_called_once()
                    assert mock_dump.call_args_list[0][0][0] == steve_mcmeta
