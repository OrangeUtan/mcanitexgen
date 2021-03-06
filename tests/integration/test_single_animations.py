import pytest
import ruamel.yaml as yaml

from mcanitexgen import generator, parser
from mcanitexgen.generator import AnimationContext, GeneratorError, Mark
from mcanitexgen.parser import Sequence, SequenceAction, StateAction, TextureAnimation
from tests.generator.test_sequences_constant import frame


def state(r, s=None, e=None, m=None, w=0, d=None):
    return StateAction(state=r, start=s, end=e, mark=m, weight=w, duration=d)


def sequence(ref, rep=1, s=None, e=None, m=None, w=0, d=None):
    return SequenceAction(ref=ref, repeat=rep, start=s, end=e, mark=m, weight=w, duration=d)


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

    expected_frames = [
        frame(0, 120),
        frame(1, 4),
        frame(0, 120),
        frame(1, 4),
        frame(0, 120),
        frame(1, 4),
    ]

    frames = generator.animation_to_frames(parser.parse_animations(json)[0])
    assert frames == expected_frames


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

    expected_frames = [
        frame(0, 100),
        frame(1, 20),
        frame(0, 100),
        frame(1, 20),
        frame(0, 100),
        frame(1, 20),
    ]

    frames = generator.animation_to_frames(parser.parse_animations(json)[0])
    assert frames == expected_frames


def test_weighted_blinking():
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

    expected_frames = [
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
    ]

    frames = generator.animation_to_frames(parser.parse_animations(json)[0])
    assert frames == expected_frames
