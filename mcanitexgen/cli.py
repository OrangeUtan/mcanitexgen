from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import PIL.Image
import typer

import mcanitexgen
from mcanitexgen.animation import load_animations_from_file, write_mcmeta_files


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
    dry: bool = typer.Option(
        False, "--dry", help="Dry run. Don't generate any files", is_flag=True
    ),
):
    out_dir = out_dir if out_dir else file.parent

    texture_animations = load_animations_from_file(file)

    if not dry:
        out_dir.mkdir(parents=True, exist_ok=True)
        write_mcmeta_files(texture_animations, out_dir, indent=None if no_indent else 2)


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
        mcanitexgen.gif.create_gif(animation.frames, texture, animation.frametime, dest)
