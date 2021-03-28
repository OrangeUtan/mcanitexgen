import os
from typing import Any

import pytest
from beet import run_beet
from pytest_insta import SnapshotFixture


@pytest.mark.parametrize("directory", os.listdir("tests/integration/beet/examples"))  # type: ignore
def test_build(snapshot: SnapshotFixture, directory: str):
    with run_beet(directory=f"tests/integration/beet/examples/{directory}") as ctx:
        texture_mcmetas = list(
            map(lambda l: {l[0]: l[1].content}, ctx.assets.textures_mcmeta.items())
        )
        assert snapshot("mcmetas.json") == texture_mcmetas
