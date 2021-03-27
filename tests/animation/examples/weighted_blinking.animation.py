from mcanitexgen.animation import Sequence, State, TextureAnimation, animation


@animation("head.png")
class Head(TextureAnimation):
    NEUTRAL_OPEN = State(0)
    NEUTRAL_CLOSED = State(1)

    blink = Sequence(NEUTRAL_OPEN(weight=5), NEUTRAL_CLOSED(weight=1))

    blinking = Sequence(3 * blink(duration=120))

    main = Sequence(blinking)
