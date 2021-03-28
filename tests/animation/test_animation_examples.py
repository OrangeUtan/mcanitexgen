from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pytest_insta import SnapshotFixture

import mcanitexgen


@pytest.mark.parametrize(
    "file",
    [
        "steve.animation.py",
        "dog.animation.py",
        "unweighted_seq_in_weighted.animation.py",
        "weighted_blinking.animation.py",
        "weighted_blinking_2.animation.py",
        "simple_blinking.animation.py",
    ],
)
def test(file: str, snapshot: SnapshotFixture):
    animations = mcanitexgen.animation.load_animations_from_file(
        Path("tests/animation/examples/" + file)
    )

    with patch("builtins.open", new=MagicMock()) as mock_open:
        with patch("json.dump", new=MagicMock()) as mock_dump:
            mcanitexgen.animation.write_mcmeta_files(animations, Path("out"))

            assert mock_dump.call_count == len(animations)
            for i, (name, _) in enumerate(animations.items()):
                mcmeta = mock_dump.call_args_list[i][0][0]
                assert snapshot(f"{name}.json") == mcmeta
