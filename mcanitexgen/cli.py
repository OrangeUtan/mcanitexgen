from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import PIL.Image
import typer

import mcanitexgen
from mcanitexgen.animation import (
    load_animations,
    load_animations_from_file,
    write_mcmeta_files,
)


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
    src: Path = typer.Argument(
        ..., exists=True, readable=True, help="File or directory containing animations"
    ),
    out: Optional[Path] = typer.Option(
        None,
        "-o",
        "--out",
        help="The output directory of the generated files",
        file_okay=False,
        writable=True,
    ),
    minify: bool = typer.Option(
        False, "--minify", "-m", is_flag=True, flag_value=True, help="Minify generated files"
    ),
    indent: str = typer.Option(
        "\t", "--indent", "-i", help="Indentation used when generating files"
    ),
    dry: bool = typer.Option(
        False, "--dry", help="Dry run. Don't generate any files", is_flag=True
    ),
):
    if out is None:
        out = src if src.is_dir() else src.parent

    texture_animations = load_animations(src)
    if not dry:
        out.mkdir(parents=True, exist_ok=True)
        write_mcmeta_files(texture_animations, out, indent if not minify else None)


@app.command(help="Create gifs for all animations in an animation file")
def gif(
    file: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    out: Optional[Path] = typer.Option(
        None,
        "-o",
        "--out",
        help="The output directory of the generated gif",
        file_okay=False,
        writable=True,
    ),
):
    out = out if out else file.parent
    out.mkdir(parents=True, exist_ok=True)

    for animation in load_animations_from_file(file).values():
        texture_path = Path(file.parent, animation.texture)
        dest = Path(out, f"{os.path.splitext(animation.texture.name)[0]}.gif")
        texture = PIL.Image.open(texture_path)
        mcanitexgen.gif.create_gif(animation.frames, texture, animation.frametime, dest)
