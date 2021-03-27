from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mcanitexgen.animation import generator
from mcanitexgen.animation.generator import Sequence, State, TextureAnimation, animation


@pytest.fixture
def simple_texture_animation():
    @animation("test.png")
    class Anim(TextureAnimation):
        A = State(0)
        B = State(1)

        main = Sequence(A, B, A)

    return Anim


def test(simple_texture_animation):
    with patch("builtins.open", new=MagicMock()):
        with patch("json.dump", new=MagicMock()) as mock_dump:
            generator.write_mcmeta_files({"test": simple_texture_animation}, Path("test"))

            mock_dump.assert_called_once()
            assert mock_dump.call_args_list[0][0][0] == {
                "animation": {
                    "frametime": 1,
                    "interpolate": False,
                    "frames": [
                        {"index": 0, "time": 1},
                        {"index": 1, "time": 1},
                        {"index": 0, "time": 1},
                    ],
                }
            }
