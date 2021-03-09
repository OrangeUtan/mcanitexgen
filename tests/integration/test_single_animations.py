import pytest
import ruamel.yaml as yaml

from mcanitexgen import generator, parser
from mcanitexgen.generator import Animation, GeneratorError, Mark
from mcanitexgen.parser import Sequence, SequenceAction, StateAction, TextureAnimation


def frame(index: int, time: int):
    return {"index": index, "time": time}


def test_simple_blinking():
    json = yaml.safe_load(
        """
    head.png:
        states: [
            NEUTRAL_OPEN,
            NEUTRAL_CLOSED,
        ]

        blink():
            - NEUTRAL_OPEN: {duration: 120}
            - NEUTRAL_CLOSED: {duration: 4}

        blinking():
            - 3 * blink()

        main(): [
            blinking()
        ]
    """
    )

    expected_anim = Animation(
        0,
        372,
        [
            frame(0, 120),
            frame(1, 4),
            frame(0, 120),
            frame(1, 4),
            frame(0, 120),
            frame(1, 4),
        ],
    )

    animation = generator.create_animation(parser.parse_animations(json)[0])
    assert animation == expected_anim
    assert sum(map(lambda f: f["time"], animation.frames)) == expected_anim.end


def test_weighted_blinking():
    json = yaml.safe_load(
        """
    head.png:
        states: [
            NEUTRAL_OPEN,
            NEUTRAL_CLOSED,
        ]

        blink():
            - NEUTRAL_OPEN: {weight: 5}
            - NEUTRAL_CLOSED: {weight: 1}

        blinking():
            - 3 * blink(): {duration: 120}

        main(): [
            blinking()
        ]
    """
    )

    expected_anim = Animation(
        0,
        360,
        [
            frame(0, 100),
            frame(1, 20),
            frame(0, 100),
            frame(1, 20),
            frame(0, 100),
            frame(1, 20),
        ],
    )

    animation = generator.create_animation(parser.parse_animations(json)[0])
    assert animation == expected_anim
    assert sum(map(lambda f: f["time"], animation.frames)) == expected_anim.end


def test_weighted_blinking_2():
    json = yaml.safe_load(
        """
    head.png:
        states: [
            NEUTRAL_OPEN,
            NEUTRAL_CLOSED,
        ]

        blinking():
            - 2 * blink(): {weight: 1}
            - NEUTRAL_CLOSED: {duration: 10}

        blink():
            - NEUTRAL_OPEN: {weight: 1}
            - NEUTRAL_CLOSED: {duration: 4}

        main(): [
            2 * blinking(): {duration: 39}
        ]
    """
    )

    expected_anim = Animation(
        0,
        78,
        [
            frame(0, 11),
            frame(1, 4),
            frame(0, 10),
            frame(1, 4),
            frame(1, 10),
            #
            frame(0, 11),
            frame(1, 4),
            frame(0, 10),
            frame(1, 4),
            frame(1, 10),
        ],
    )

    animation = generator.create_animation(parser.parse_animations(json)[0])
    assert animation == expected_anim
    assert sum(map(lambda f: f["time"], animation.frames)) == expected_anim.end


def test_unweighted_seq_in_weighted_seq():
    json = yaml.safe_load(
        """
    head.png:
        states: [
            A,
            B,
        ]

        nested_unweighted():
            - A: {duration: 4}

        weighted():
            - B: {weight: 1}
            - nested_unweighted()

        main():
            - weighted(): {duration: 120}
    """
    )

    expected_anim = Animation(
        0,
        120,
        [
            frame(1, 116),
            frame(0, 4),
        ],
    )

    animation = generator.create_animation(parser.parse_animations(json)[0])
    assert animation == expected_anim
