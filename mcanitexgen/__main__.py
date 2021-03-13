import json
from pathlib import Path
from typing import Optional

import typer

from mcanitexgen import load_animations_from_file

app = typer.Typer()


@app.command()
def main(
    animations_file: str,
    out_dir: Optional[str] = typer.Argument(
        None, help="Directory animation files will be generated in"
    ),
):
    animations_file: Path = Path(animations_file)
    out_dir: Path = Path(out_dir) if out_dir else animations_file.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    if not animations_file.exists():
        raise FileNotFoundError(animations_file)

    texture_animations = load_animations_from_file(animations_file)
    for animation in texture_animations.values():
        with Path(out_dir, f"{animation.texture}.mcmeta").open("w") as f:
            data = {
                "animation": {"interpolate": False, "frametime": 1, "frames": animation.frames}
            }

            json.dump(data, f)


app()
