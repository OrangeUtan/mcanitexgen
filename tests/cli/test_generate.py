from contextlib import contextmanager
from io import TextIOWrapper
from pathlib import Path
from typing import Tuple
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from mcanitexgen import __main__ as cli


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


def test_animation_file_doesnt_exist(runner: CliRunner):
    result = runner.invoke(cli.app, "generate doesnt_exist")

    assert result.exit_code == 2
    assert "does not exist" in result.stdout


@pytest.mark.parametrize(
    "out_dir, expected_mcmeta_path",
    [
        ("", "tests/cli/res/steve.png.mcmeta"),
        ("build/generated", "build/generated/steve.png.mcmeta"),
    ],
)
def test_out_dir(out_dir, expected_mcmeta_path, steve_mcmeta, runner: CliRunner):
    mcmeta_paths = []

    def mkdir(*args, **kwargs):
        pass

    @contextmanager
    def open(path: Path, mode: str):
        mcmeta_paths.append(path)
        yield

    generated_mcmeta: list[dict] = []

    def dump(json_data, file_pointer, **kwargs):
        generated_mcmeta.append(json_data)

    with patch("pathlib.Path.mkdir", new=mkdir):
        with patch("pathlib.Path.open", new=open):
            with patch("json.dump", new=dump):
                runner.invoke(cli.app, f"generate tests/cli/res/steve.animation.py {out_dir}")

    assert len(mcmeta_paths) == 1
    assert mcmeta_paths[0] == Path(expected_mcmeta_path)
    assert len(generated_mcmeta) == 1
    assert generated_mcmeta[0] == steve_mcmeta
