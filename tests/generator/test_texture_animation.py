import pytest

from mcanitexgen import generator
from mcanitexgen.generator import Animation, TextureAnimation


def frame(index: int, time: int):
    return {"index": index, "time": time}


def mcmeta(interpolate, frametime, frames):
    return {
        "animation": {
            "interpolate": interpolate,
            "frametime": frametime,
            "frames": frames,
        }
    }


class Test_to_mcmeta:
    @pytest.mark.parametrize(
        "interpolate, frametime, frames, expected_mcmeta",
        [
            # Interpolate
            (False, 1, [frame(0, 10)], mcmeta(False, 1, [frame(0, 10)])),
            (True, 1, [frame(0, 10)], mcmeta(True, 1, [frame(0, 10)])),
            # Frametime
            (False, 10, [frame(0, 10)], mcmeta(False, 10, [frame(0, 10)])),
        ],
    )
    def test(self, interpolate, frametime, frames, expected_mcmeta):
        class TestAnim(TextureAnimation):
            pass

        TestAnim.interpolate = interpolate
        TestAnim.frametime = frametime
        TestAnim.animation = Animation(0, 100, frames)

        assert TestAnim.to_mcmeta() == expected_mcmeta
