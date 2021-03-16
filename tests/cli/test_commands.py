from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

import mcanitexgen
from mcanitexgen import __main__ as cli
from mcanitexgen.generator import Animation


@pytest.fixture
def runner():
    return CliRunner()


class Test_main:
    def test_version(self, runner: CliRunner):
        result = runner.invoke(cli.app, "--version", catch_exceptions=False)
        assert mcanitexgen.__version__ in result.stdout


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

    def test_file_doesnt_exist(self, runner: CliRunner):
        result = runner.invoke(cli.app, "generate doesnt_exist", catch_exceptions=False)

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


class Test_gif:
    def test_file_doesnt_exist(self, runner: CliRunner):
        result = runner.invoke(cli.app, "gif doesnt_exist", catch_exceptions=False)

        assert result.exit_code == 2
        assert "does not exist" in result.stdout

    def test_steve(self, runner: CliRunner):
        with patch("PIL.Image.open", new=MagicMock()) as mock_open:
            with patch("mcanitexgen.__main__.create_gif", new=MagicMock()) as mock_create_gif:
                runner.invoke(
                    cli.app, "gif tests/cli/res/steve.animation.py", catch_exceptions=False
                )

                mock_open.assert_called_once()
                assert mock_open.call_args_list[0][0][0] == Path("tests/cli/res/steve.png")

                mock_create_gif.assert_called_once()
                frames, texture, frametime, dest = mock_create_gif.call_args_list[0][0]
                assert texture == mock_open.return_value
                assert dest == Path("tests/cli/res/steve.gif")

    @pytest.mark.parametrize(
        "out_dir, expected_dest",
        [
            ("", "tests/cli/res/steve.gif"),
            (".", "steve.gif"),
            ("build/generated", "build/generated/steve.gif"),
        ],
    )
    def test_out_dir(self, out_dir, expected_dest, runner: CliRunner):
        with patch("PIL.Image.open", new=MagicMock()) as mock_open:
            with patch("mcanitexgen.__main__.create_gif", new=MagicMock()) as mock_create_gif:
                runner.invoke(
                    cli.app,
                    f"gif tests/cli/res/steve.animation.py {out_dir}",
                    catch_exceptions=False,
                )

                mock_open.assert_called_once()
                assert mock_open.call_args_list[0][0][0] == Path("tests/cli/res/steve.png")

                mock_create_gif.assert_called_once()
                frames, texture, frametime, dest = mock_create_gif.call_args_list[0][0]
                assert texture == mock_open.return_value
                assert dest == Path(expected_dest)
