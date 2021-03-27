from mcanitexgen.animation import Sequence, State, animation
from mcanitexgen.animation.generator import Animation, TextureAnimation


def frame(index: int, time: int):
    return {"index": index, "time": time}


def test_simple_blinking():
    @animation("head.png")
    class Head(TextureAnimation):
        NEUTRAL_OPEN = State(0)
        NEUTRAL_CLOSED = State(1)

        blink = Sequence(NEUTRAL_OPEN(duration=120), NEUTRAL_CLOSED(duration=4))

        blinking = Sequence(3 * blink)

        main = Sequence(blinking)

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

    assert Head.animation == expected_anim
    assert sum(map(lambda f: f["time"], Head.frames)) == expected_anim.end


def test_weighted_blinking():
    @animation("head.png")
    class Head(TextureAnimation):
        NEUTRAL_OPEN = State(0)
        NEUTRAL_CLOSED = State(1)

        blink = Sequence(NEUTRAL_OPEN(weight=5), NEUTRAL_CLOSED(weight=1))

        blinking = Sequence(3 * blink(duration=120))

        main = Sequence(blinking)

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

    assert Head.animation == expected_anim
    assert sum(map(lambda f: f["time"], Head.frames)) == expected_anim.end


def test_weighted_blinking_2():
    @animation("head.png")
    class Head(TextureAnimation):
        NEUTRAL_OPEN = State(0)
        NEUTRAL_CLOSED = State(1)

        blink = Sequence(NEUTRAL_OPEN(weight=1), NEUTRAL_CLOSED(duration=4))

        blinking = Sequence(2 * blink(weight=1), NEUTRAL_CLOSED(duration=4))

        main = Sequence(2 * blinking(duration=39))

    expected_anim = Animation(
        0,
        78,
        [
            frame(0, 14),
            frame(1, 4),
            frame(0, 13),
            frame(1, 4),
            frame(1, 4),
            #
            frame(0, 14),
            frame(1, 4),
            frame(0, 13),
            frame(1, 4),
            frame(1, 4),
        ],
    )

    assert Head.animation == expected_anim
    assert sum(map(lambda f: f["time"], Head.frames)) == expected_anim.end


def test_unweighted_seq_in_weighted_seq():
    @animation("head.png")
    class Head(TextureAnimation):
        A = State(0)
        B = State(1)

        nested_unweighted = Sequence(A(duration=4))

        weighted = Sequence(B(weight=1), nested_unweighted)

        main = Sequence(weighted(duration=120))

    expected_anim = Animation(
        0,
        120,
        [
            frame(1, 116),
            frame(0, 4),
        ],
    )

    assert Head.animation == expected_anim
    assert sum(map(lambda f: f["time"], Head.frames)) == expected_anim.end
