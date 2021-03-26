import pytest
from typer.testing import CliRunner

import mcanitexgen
from mcanitexgen import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_version(runner: CliRunner):
    result = runner.invoke(cli.app, "--version", catch_exceptions=False)
    assert mcanitexgen.__version__ in result.stdout
