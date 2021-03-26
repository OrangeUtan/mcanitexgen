from pathlib import Path
from typing import Tuple
from unittest.mock import MagicMock, patch

import PIL
import PIL.Image
import pytest
from pytest import approx, fixture

from mcanitexgen import cli


def frame(index: int, time: int):
    return {"index": index, "time": time}


class Test_get_animation_states_from_texture:
    @pytest.mark.parametrize(
        "width, height, expected_num_states", [(1, 2, 2), (2, 2, 1), (4, 16, 4), (16, 128, 8)]
    )
    def test_number_of_states(self, width, height, expected_num_states):
        img = PIL.Image.new("RGBA", (width, height), color="red")
        states = cli.get_animation_states_from_texture(img)

        assert len(states) == expected_num_states

    @pytest.mark.parametrize(
        "texture_size, expected_size", [((16, 512), (16, 16)), ((32, 128), (32, 32))]
    )
    def test_state_sizes(self, texture_size, expected_size):
        img = PIL.Image.new("RGBA", texture_size, color="red")
        states = cli.get_animation_states_from_texture(img)

        for state in states:
            assert state.size == expected_size

    @pytest.mark.parametrize("width", [3, 5, 9, 10, 100])
    def test_invalid_width(self, width):
        img = PIL.Image.new("RGBA", (width, 2 * width), color="red")

        with pytest.raises(ValueError, match=f"Texture width '{width}' is not power of 2"):
            cli.get_animation_states_from_texture(img)

    @pytest.mark.parametrize("width, height", [(16, 31), (16, 127)])
    def test_height_is_not_multiple_of_width(self, width, height):
        img = PIL.Image.new("RGBA", (width, height), color="red")

        with pytest.raises(
            ValueError,
            match=f"Texture height '{height}' is not multiple of its width '{width}'",
        ):
            cli.get_animation_states_from_texture(img)

    @pytest.mark.parametrize(
        "texture_size, expected_cropped_boxes",
        [
            ((16, 16), [(0, 0, 16, 16)]),
            ((16, 32), [(0, 0, 16, 16), (0, 16, 16, 32)]),
            ((32, 128), [(0, 0, 32, 32), (0, 32, 32, 64), (0, 64, 32, 96), (0, 96, 32, 128)]),
        ],
    )
    def test_crop_args(self, texture_size, expected_cropped_boxes):
        img = PIL.Image.new("RGBA", texture_size, color="red")

        cropped_boxes = []

        def crop(box: Tuple[int, int, int, int]):
            cropped_boxes.append(tuple(box))

        with patch.object(img, "crop", new=crop):
            cli.get_animation_states_from_texture(img)

        assert cropped_boxes == expected_cropped_boxes


class Test_convert_to_gif_frames:
    @fixture
    def states(self):
        return [0, 1, 2, 3, 4, 5]

    @pytest.mark.parametrize(
        "frames, expected_frames, expected_durations",
        [
            ([frame(0, 1)], [0], [0.05]),
            ([frame(0, 10)], [0], [0.5]),
            ([frame(0, 10), frame(2, 5), frame(5, 10)], [0, 2, 5], [0.5, 0.25, 0.5]),
        ],
    )
    def test(self, frames, expected_frames, expected_durations, states):
        frames, durations = zip(*cli.convert_to_gif_frames(frames, states, 1))

        assert list(frames) == expected_frames
        assert list(durations) == expected_durations

    @pytest.mark.parametrize(
        "frames, frametime, expected_frames, expected_durations",
        [
            ([frame(0, 1)], 10, [0], [0.5]),
            ([frame(0, 10), frame(2, 5), frame(5, 10)], 10, [0, 2, 5], [5, 2.5, 5]),
        ],
    )
    def test_frametime(self, frames, frametime, expected_frames, expected_durations, states):
        frames, durations = zip(*cli.convert_to_gif_frames(frames, states, frametime))

        assert list(frames) == expected_frames
        assert list(durations) == expected_durations


class Test_create_gif:
    @fixture
    def texture(self):
        return PIL.Image.new("RGBA", (16, 64), "red")

    def test_pass_no_frames(self, texture):
        with pytest.warns(UserWarning, match="No frames.*"):
            cli.create_gif([], texture, 1, Path("test.gif"))

    def test(self):
        frames = [frame(0, 10), frame(1, 12)]
        texture = PIL.Image.new("RGBA", (16, 64), "red")
        expected_frametime = 1
        expected_dest = Path("test.gif")

        with patch("mcanitexgen.images2gif.writeGif", new=MagicMock()) as mock_writeGif:
            cli.create_gif(frames, texture, expected_frametime, expected_dest)

            mock_writeGif.assert_called_once()
            dest, images, durations = mock_writeGif.call_args_list[0][0]
            assert dest == expected_dest
            assert len(images) == len(frames)
            assert len(durations) == len(frames)
            assert durations == (approx(0.5), approx(0.6))
