from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Optional

import PIL.Image
import typer
from PIL.Image import Image

import mcanitexgen.images2gif
from mcanitexgen import load_animations_from_file


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


app = typer.Typer()


@app.command(help="Generate .mcmeta files for all animations in an animation file")
def generate(
    animations_file: str,
    out_dir: Optional[str] = typer.Argument(
        None, help="Directory animation files will be generated in"
    ),
    no_indent: int = typer.Option(
        False, help="Pretty print json with indentation", is_flag=True, flag_value=True
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
            json.dump(animation.to_mcmeta(), f, indent=None if no_indent else 2)


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
            gif_path, images=frames, duration=durations, subRectangles=False, dispose=2
        )


if __name__ == "__main__":
    app()
