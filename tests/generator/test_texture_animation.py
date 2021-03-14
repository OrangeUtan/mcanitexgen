import pytest
from hypothesis import given, settings
from hypothesis.strategies import builds, integers
from hypothesis.strategies._internal.core import lists

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


class Test_combine_consecutive_frames:
    @pytest.mark.parametrize(
        "frames, expected_frames",
        [
            ([frame(0, 10), frame(0, 10)], [frame(0, 20)]),
            (
                [frame(1, 10), frame(0, 20), frame(0, 1), frame(2, 20)],
                [frame(1, 10), frame(0, 21), frame(2, 20)],
            ),
        ],
    )
    def test(self, frames, expected_frames):
        assert list(TextureAnimation.combine_consecutive_frames(frames)) == expected_frames

    @given(lists(builds(frame, integers(min_value=0), integers(min_value=1))))
    @settings(max_examples=30)
    def test_fuzzy(self, frames):
        combined_frames = list(TextureAnimation.combine_consecutive_frames(frames))

        assert sum(map(lambda f: f["time"], frames)) == sum(
            map(lambda f: f["time"], combined_frames)
        )
