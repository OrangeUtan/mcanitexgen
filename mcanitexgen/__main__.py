from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer

from mcanitexgen import load_animations_from_file

app = typer.Typer()


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


def get_animation_states(img):
    state_size, img_height = img.size
    assert state_size % 2 == 0
    assert img_height % state_size == 0
    num_states = int(img_height / state_size)

    return [
        img.crop((0, i * state_size, state_size, (i + 1) * state_size))
        for i in range(num_states)
    ]


@app.command(help="Create gifs for all animations in an animation file")
def gif(
    animations_file: str,
    out_dir: Optional[str] = typer.Argument(
        None, help="Directory gif files will be generated in"
    ),
):
    import PIL.Image
    from PIL.Image import Image

    import mcanitexgen.images2gif

    animations_path: Path = Path(animations_file)
    if not animations_path.exists():
        raise FileNotFoundError(animations_path)
    out_dir_path: Path = Path(out_dir) if out_dir else animations_path.parent
    out_dir_path.mkdir(parents=True, exist_ok=True)

    for animation in load_animations_from_file(animations_path).values():
        texture_path = Path(animations_path.parent, animation.texture)
        gif_path = Path(out_dir_path, f"{os.path.splitext(animation.texture.name)[0]}.gif")

        states = get_animation_states(PIL.Image.open(texture_path))
        frametime = 1 / 20 * animation.frametime

        frames: list[Image] = []
        durations = []
        for frame in animation.frames:
            frames.append(states[frame["index"]])
            durations.append(frametime * frame["time"])

        mcanitexgen.images2gif.writeGif(
            gif_path, images=frames, duration=durations, subRectangles=True
        )


app()
