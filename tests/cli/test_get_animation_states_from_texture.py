from typing import Tuple
from unittest.mock import patch

import pytest
from PIL import Image

from mcanitexgen import __main__ as cli_main


@pytest.mark.parametrize(
    "width, height, expected_num_states", [(1, 2, 2), (2, 2, 1), (4, 16, 4), (16, 128, 8)]
)
def test_number_of_states(width, height, expected_num_states):
    img = Image.new("RGBA", (width, height), color="red")
    states = cli_main.get_animation_states_from_texture(img)

    assert len(states) == expected_num_states


@pytest.mark.parametrize(
    "texture_size, expected_size", [((16, 512), (16, 16)), ((32, 128), (32, 32))]
)
def test_state_sizes(texture_size, expected_size):
    img = Image.new("RGBA", texture_size, color="red")
    states = cli_main.get_animation_states_from_texture(img)

    for state in states:
        assert state.size == expected_size


@pytest.mark.parametrize("width", [3, 5, 9, 10, 100])
def test_invalid_width(width):
    img = Image.new("RGBA", (width, 2 * width), color="red")

    with pytest.raises(ValueError, match=f"Texture width '{width}' is not power of 2"):
        cli_main.get_animation_states_from_texture(img)


@pytest.mark.parametrize("width, height", [(16, 31), (16, 127)])
def test_height_is_not_multiple_of_width(width, height):
    img = Image.new("RGBA", (width, height), color="red")

    with pytest.raises(
        ValueError, match=f"Texture height '{height}' is not multiple of its width '{width}'"
    ):
        cli_main.get_animation_states_from_texture(img)


@pytest.mark.parametrize(
    "texture_size, expected_cropped_boxes",
    [
        ((16, 16), [(0, 0, 16, 16)]),
        ((16, 32), [(0, 0, 16, 16), (0, 16, 16, 32)]),
        ((32, 128), [(0, 0, 32, 32), (0, 32, 32, 64), (0, 64, 32, 96), (0, 96, 32, 128)]),
    ],
)
def test_crop_args(texture_size, expected_cropped_boxes):
    img = Image.new("RGBA", texture_size, color="red")

    cropped_boxes = []

    def crop(box: Tuple[int, int, int, int]):
        cropped_boxes.append(tuple(box))

    with patch.object(img, "crop", new=crop):
        cli_main.get_animation_states_from_texture(img)

    assert cropped_boxes == expected_cropped_boxes
