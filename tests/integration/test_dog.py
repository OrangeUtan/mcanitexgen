from pathlib import Path

import ruamel.yaml as yaml

from mcanitexgen import generator, parser
from mcanitexgen.generator import Animation, Mark


def frame(index: int, time: int):
    return {"index": index, "time": time}


def test():
    texture_animations = parser.parse_animation_file(
        Path("tests/integration/res/dog.animation.yml")
    )

    head_anim = generator.create_animation(texture_animations["head"])
    expected_head_anim = Animation(
        0,
        2074,
        [
            # bored: 840
            *[frame(2, 116), frame(3, 4)] * 7,
            # fall_asleep: 75
            frame(2, 50),
            frame(5, 25),
            # asleep: 600
            frame(3, 288),
            frame(5, 25),
            frame(3, 287),
            # wake_up: 75
            frame(5, 25),
            frame(2, 50),
            # happy: 64
            *[*[frame(4, 1), frame(2, 5)] * 2, frame(3, 4)] * 4,
            # curious: 400
            frame(0, 22),
            frame(1, 22),
            frame(0, 22),
            frame(1, 334),
            # NEUTRAL: 20
            frame(0, 20),
        ],
        {"asleep": Mark(915, 1515), "peek_while_sleeping": Mark(1203, 1228)},
    )

    assert head_anim == expected_head_anim
    assert sum(map(lambda f: f["time"], head_anim.frames)) == expected_head_anim.end

    expr_locals = {"head": expected_head_anim}

    tail_n_hindlegs_anim = generator.create_animation(
        texture_animations["tail_and_hindlegs"], expr_locals
    )
    expected_tail_n_hindlegs_anim = Animation(
        0,
        2074,
        [
            # bored: 800
            *[
                *[frame(3, 12), frame(4, 12)] * 5,
                frame(2, 80),
            ]
            * 4,
            # TAIL_LOW: 650
            frame(2, 650),
            # wagging_with_pause: 600
            *[
                *[
                    frame(1, 5),
                    frame(0, 5),
                ]
                * 9,
                *[
                    frame(1, 8),
                    frame(0, 7),
                ]
                * 4,
                frame(1, 10),
                frame(2, 40),
            ]
            * 3,
            frame(2, 24),
        ],
    )

    assert tail_n_hindlegs_anim == expected_tail_n_hindlegs_anim
    assert (
        sum(map(lambda f: f["time"], tail_n_hindlegs_anim.frames))
        == expected_tail_n_hindlegs_anim.end
    )
