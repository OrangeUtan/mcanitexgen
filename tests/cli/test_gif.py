from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from mcanitexgen import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_file_doesnt_exist(runner: CliRunner):
    result = runner.invoke(cli.app, "gif doesnt_exist", catch_exceptions=False)

    assert result.exit_code == 2
    assert "does not exist" in result.stdout


def test_steve(runner: CliRunner):
    with patch("PIL.Image.open", new=MagicMock()) as mock_open:
        with patch("mcanitexgen.gif.create_gif", new=MagicMock()) as mock_create_gif:
            runner.invoke(
                cli.app,
                "gif tests/animation/examples/steve.animation.py",
                catch_exceptions=False,
            )

            mock_open.assert_called_once()
            assert mock_open.call_args_list[0][0][0] == Path(
                "tests/animation/examples/steve.png"
            )

            mock_create_gif.assert_called_once()
            frames, texture, frametime, dest = mock_create_gif.call_args_list[0][0]
            assert texture == mock_open.return_value
            assert dest == Path("tests/animation/examples/steve.gif")


class Test_out_arg:
    @pytest.mark.parametrize(
        "out, expected_dest",
        [
            (".", "steve.gif"),
            ("build/generated", "build/generated/steve.gif"),
        ],
    )
    def test_out_dir(self, out, expected_dest, runner: CliRunner):
        with patch("PIL.Image.open", new=MagicMock()) as mock_open:
            with patch("mcanitexgen.gif.create_gif", new=MagicMock()) as mock_create_gif:
                runner.invoke(
                    cli.app,
                    f"gif tests/animation/examples/steve.animation.py -o {out}",
                    catch_exceptions=False,
                )

                mock_open.assert_called_once()
                assert mock_open.call_args_list[0][0][0] == Path(
                    "tests/animation/examples/steve.png"
                )

                mock_create_gif.assert_called_once()
                frames, texture, frametime, dest = mock_create_gif.call_args_list[0][0]
                assert texture == mock_open.return_value
                assert dest == Path(expected_dest)

    def test_defaults_to_parent_of_file(self, runner: CliRunner):
        with patch("PIL.Image.open", new=MagicMock()) as mock_open:
            with patch("mcanitexgen.gif.create_gif", new=MagicMock()) as mock_create_gif:

                runner.invoke(
                    cli.app,
                    f"gif tests/animation/examples/steve.animation.py",
                    catch_exceptions=False,
                )

                mock_create_gif.assert_called_once()
                assert mock_create_gif.call_args_list[0][0][3] == Path(
                    "tests/animation/examples/steve.gif"
                )
