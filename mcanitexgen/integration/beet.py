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
                animations = mcanitexgen.animation.load_animations(path)

                minecraft.textures_mcmeta.merge(
                    {
                        name: TextureMcmeta(texanim.to_mcmeta())
                        for name, texanim in animations.items()
                    }
                )

    return plugin
