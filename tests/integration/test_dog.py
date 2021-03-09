from pathlib import Path

import ruamel.yaml as yaml

from mcanitexgen import generator, parser
from mcanitexgen.generator import Animation, Mark


def frame(index: int, time: int):
    return {"index": index, "time": time}


def test_head():
    texture_animations = parser.parse_animation_file(
        Path("tests/integration/res/dog.animation.yml")
    )

    head_anim = generator.create_animation(texture_animations["head"])
    expected_head_anim = Animation(
        0,
        2074,
        [
            # bored: 840
            frame(2, 116),
            frame(3, 4),
            frame(2, 116),
            frame(3, 4),
            frame(2, 116),
            frame(3, 4),
            frame(2, 116),
            frame(3, 4),
            frame(2, 116),
            frame(3, 4),
            frame(2, 116),
            frame(3, 4),
            frame(2, 116),
            frame(3, 4),
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
            frame(4, 1),
            frame(2, 5),
            frame(4, 1),
            frame(2, 5),
            frame(3, 4),
            frame(4, 1),
            frame(2, 5),
            frame(4, 1),
            frame(2, 5),
            frame(3, 4),
            frame(4, 1),
            frame(2, 5),
            frame(4, 1),
            frame(2, 5),
            frame(3, 4),
            frame(4, 1),
            frame(2, 5),
            frame(4, 1),
            frame(2, 5),
            frame(3, 4),
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
