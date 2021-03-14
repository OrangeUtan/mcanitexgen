from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import PIL.Image
import typer
from PIL.Image import Image

import mcanitexgen.images2gif
from mcanitexgen import load_animations_from_file
from mcanitexgen.generator import Animation

app = typer.Typer()


def get_animation_states_from_texture(texture: Image):
    state_size, img_height = texture.size
    assert state_size % 2 == 0
    assert img_height % state_size == 0
    num_states = int(img_height / state_size)

    return [
        texture.crop((0, i * state_size, state_size, (i + 1) * state_size))
        for i in range(num_states)
    ]


def convert_to_gif_frames(frames: list[dict], states: list[Image], frametime: float):
    frametime = 1 / 20 * frametime
    for frame in frames:
        yield (states[frame["index"]], frametime * frame["time"])


if __name__ == "__main__":

    @app.command(help="Generate .mcmeta files for all animations in an animation file")
    def generate(
        animations_file: str,
        out_dir: Optional[str] = typer.Argument(
            None, help="Directory animation files will be generated in"
        ),
    ):
        animations_path: Path = Path(animations_file)
        if not animations_path.exists():
            raise FileNotFoundError(animations_path)
        out_dir_path: Path = Path(out_dir) if out_dir else animations_path.parent
        out_dir_path.mkdir(parents=True, exist_ok=True)

        texture_animations = load_animations_from_file(animations_path)
        for animation in texture_animations.values():
            with Path(out_dir_path, f"{animation.texture}.mcmeta").open("w") as f:
                json.dump(animation.to_mcmeta(), f)

    @app.command(help="Create gifs for all animations in an animation file")
    def gif(
        animations_file: str,
        out_dir: Optional[str] = typer.Argument(
            None, help="Directory gif files will be generated in"
        ),
    ):
        animations_path: Path = Path(animations_file)
        if not animations_path.exists():
            raise FileNotFoundError(animations_path)
        out_dir_path: Path = Path(out_dir) if out_dir else animations_path.parent
        out_dir_path.mkdir(parents=True, exist_ok=True)

        for animation in load_animations_from_file(animations_path).values():
            texture_path = Path(animations_path.parent, animation.texture)
            gif_path = Path(out_dir_path, f"{os.path.splitext(animation.texture.name)[0]}.gif")

            states = get_animation_states_from_texture(PIL.Image.open(texture_path))
            frames, durations = zip(
                *convert_to_gif_frames(animation.frames, states, animation.frametime)
            )

            mcanitexgen.images2gif.writeGif(
                gif_path, images=frames, duration=durations, subRectangles=True
            )

    app()
