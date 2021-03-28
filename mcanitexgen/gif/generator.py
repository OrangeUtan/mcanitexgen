from __future__ import annotations

__all__ = ["create_gif"]

import math
import warnings
from pathlib import Path

from PIL.Image import Image

from . import images2gif


def get_animation_states_from_texture(texture: Image):
    width, height = texture.size

    if not math.log(width, 2).is_integer():
        raise ValueError(f"Texture width '{width}' is not power of 2")

    if not height % width == 0:
        raise ValueError(f"Texture height '{height}' is not multiple of its width '{width}'")

    return [
        texture.crop((0, i * width, width, (i + 1) * width))
        for i in range(int(height / width))
    ]


def convert_to_gif_frames(frames: list[dict], states: list[Image], frametime: float):
    frametime = 1 / 20 * frametime
    for frame in frames:
        yield (states[frame["index"]], frametime * frame["time"])


def create_gif(frames: list[dict], texture: Image, frametime: int, dest: Path):
    states = get_animation_states_from_texture(texture)

    if frames:
        images, durations = zip(*convert_to_gif_frames(frames, states, frametime))
        images2gif.writeGif(dest, images, durations, subRectangles=False, dispose=2)
    else:
        warnings.warn(f"No frames to create gif '{str(dest)}'")
