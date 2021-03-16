from __future__ import annotations

import json
import math
import os
import warnings
from pathlib import Path
from typing import Optional, cast

import PIL.Image
import typer
from PIL.Image import Image

import mcanitexgen.images2gif
from mcanitexgen import load_animations_from_file
from mcanitexgen.generator import TextureAnimation, TextureAnimationMeta


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
        mcanitexgen.images2gif.writeGif(
            dest, images, durations, subRectangles=False, dispose=2
        )
    else:
        warnings.warn(f"No frames to create gif '{str(dest)}'")


def version_callback(value: bool):
    if value:
        typer.echo(f"Mcanitexgen: {mcanitexgen.__version__}")
        raise typer.Exit()


def main(
    version: bool = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True
    )
):
    pass


app = typer.Typer(callback=main)


@app.command(help="Generate .mcmeta files for all animations in an animation file")
def generate(
    file: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    out_dir: Optional[Path] = typer.Argument(
        None,
        help="Directory animation files will be generated in",
        file_okay=False,
        writable=True,
    ),
    no_indent: int = typer.Option(
        False, help="Pretty print json with indentation", is_flag=True, flag_value=True
    ),
):
    out_dir = out_dir if out_dir else file.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    texture_animations = load_animations_from_file(file)
    for animation in texture_animations.values():
        with Path(out_dir, f"{animation.texture}.mcmeta").open("w") as f:
            json.dump(animation.to_mcmeta(), f, indent=None if no_indent else 2)


@app.command(help="Create gifs for all animations in an animation file")
def gif(
    file: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    out_dir: Optional[Path] = typer.Argument(
        None, help="Directory gif files will be generated in", file_okay=False, writable=True
    ),
):
    out_dir = out_dir if out_dir else file.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    for animation in load_animations_from_file(file).values():
        texture_path = Path(file.parent, animation.texture)
        dest = Path(out_dir, f"{os.path.splitext(animation.texture.name)[0]}.gif")
        texture = PIL.Image.open(texture_path)
        create_gif(animation.frames, texture, animation.frametime, dest)


if __name__ == "__main__":
    app()  # pragma: no cover
