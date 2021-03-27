from pathlib import Path
from unittest.mock import MagicMock, patch

import PIL
import pytest
from pytest import approx

from mcanitexgen.gif import generator


def frame(index: int, time: int):
    return {"index": index, "time": time}


@pytest.fixture
def texture():
    return PIL.Image.new("RGBA", (16, 64), "red")


def test():
    frames = [frame(0, 10), frame(1, 12)]
    texture = PIL.Image.new("RGBA", (16, 64), "red")
    expected_frametime = 1
    expected_dest = Path("test.gif")

    with patch("mcanitexgen.gif.images2gif.writeGif", new=MagicMock()) as mock_writeGif:
        generator.create_gif(frames, texture, expected_frametime, expected_dest)

        mock_writeGif.assert_called_once()
        dest, images, durations = mock_writeGif.call_args_list[0][0]
        assert dest == expected_dest
        assert len(images) == len(frames)
        assert len(durations) == len(frames)
        assert durations == (approx(0.5), approx(0.6))


def test_pass_no_frames(texture):
    with pytest.warns(UserWarning, match="No frames.*"):
        generator.create_gif([], texture, 1, Path("test.gif"))
