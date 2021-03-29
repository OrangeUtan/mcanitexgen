from pathlib import Path
from typing import Iterable

from beet import Context, TextureMcmeta

import mcanitexgen


def beet_default(ctx: Context):
    """ Entry point into beet pipeline. Loads configuration and executes mcanitexgen plugin """

    config = ctx.meta.get("mcanitexgen", {})
    load = config.get("load", ())

    ctx.require(create_mcanitexgen_plugin(load))


def create_mcanitexgen_plugin(load: Iterable[str] = ()):
    def plugin(ctx: Context):
        minecraft = ctx.assets["minecraft"]

        for pattern in load:
            for path in ctx.directory.glob(pattern):
                animations = mcanitexgen.animation.load_animations_from_file(path)

                minecraft.textures_mcmeta.merge(
                    {
                        get_mcmeta_path(ctx.directory, path, texanim.texture): TextureMcmeta(
                            texanim.to_mcmeta()
                        )
                        for _, texanim in animations.items()
                    }
                )

    return plugin


def get_mcmeta_path(ctx_path: Path, animation_file_path: Path, texture_path: Path):
    # Remove suffix
    texture_path = Path(texture_path.parent, texture_path.stem)
    # Get texture relative to animation file
    texture_path = Path(animation_file_path.parent, texture_path).resolve()

    return texture_path.relative_to(ctx_path).as_posix()
