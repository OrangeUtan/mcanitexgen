import pytest
from _pytest.fixtures import fixture
from PIL.Image import Image

from mcanitexgen import __main__ as cli_main
from mcanitexgen.generator import Animation


class MockImage:
    def __init__(self, id: int):
        self.id = id

    def __eq__(self, o: object) -> bool:
        return isinstance(o, MockImage) and o.id == self.id


def frame(index: int, time: int):
    return {"index": index, "time": time}


@fixture
def states():
    return [0, 1, 2, 3, 4, 5]


@pytest.mark.parametrize(
    "frames, expected_frames, expected_durations",
    [
        ([frame(0, 1)], [0], [0.05]),
        ([frame(0, 10)], [0], [0.5]),
        ([frame(0, 10), frame(2, 5), frame(5, 10)], [0, 2, 5], [0.5, 0.25, 0.5]),
    ],
)
def test(frames, expected_frames, expected_durations, states):
    frames, durations = zip(*cli_main.convert_to_gif_frames(frames, states, 1))

    assert list(frames) == expected_frames
    assert list(durations) == expected_durations


@pytest.mark.parametrize(
    "frames, frametime, expected_frames, expected_durations",
    [
        ([frame(0, 1)], 10, [0], [0.5]),
        ([frame(0, 10), frame(2, 5), frame(5, 10)], 10, [0, 2, 5], [5, 2.5, 5]),
    ],
)
def test_frametime(frames, frametime, expected_frames, expected_durations, states):
    frames, durations = zip(*cli_main.convert_to_gif_frames(frames, states, frametime))

    assert list(frames) == expected_frames
    assert list(durations) == expected_durations
