from typing import Iterable

from beet import Context
from beet.library.resource_pack import Language, TextureMcmeta
from beet.toolchain.context import Plugin

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
                print(path)
                animations = mcanitexgen.animation.load_animations_from_file(path)

                minecraft.textures_mcmeta.merge(
                    {
                        name: TextureMcmeta(texanim.to_mcmeta())
                        for name, texanim in animations.items()
                    }
                )

    return plugin
