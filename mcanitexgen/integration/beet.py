import logging
from pathlib import Path
from typing import Iterable

from beet import Context, TextureMcmeta

import mcanitexgen

logger = logging.getLogger(__name__)


def beet_default(ctx: Context):
    """ Entry point into beet pipeline. Loads configuration and executes mcanitexgen plugin """

    config = ctx.meta.get("mcanitexgen", {})
    load = config.get("load", ())

    ctx.require(create_mcanitexgen_plugin(load))


def create_mcanitexgen_plugin(load: Iterable[str] = ()):
    def plugin(ctx: Context):
        for pattern in load:
            for path in ctx.directory.glob(pattern):
                animations = mcanitexgen.animation.load_animations_from_file(path)

                for anim in animations.values():
                    texture = Path(anim.texture.parent, anim.texture.stem).as_posix()
                    if not texture in ctx.assets.textures:
                        logger.error(
                            f"Texture '{anim.texture}' referenced by {path.stem + path.suffix}::{anim.__name__} does not exist"
                        )
                        continue

                    ctx.assets.textures_mcmeta.merge(
                        {texture: TextureMcmeta(anim.to_mcmeta())}
                    )

    return plugin
