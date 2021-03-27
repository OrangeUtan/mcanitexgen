from mcanitexgen.animation import Sequence, State, TextureAnimation, animation


@animation("head.png")
class Head(TextureAnimation):
    NEUTRAL_OPEN = State(0)
    NEUTRAL_CLOSED = State(1)

    blink = Sequence(NEUTRAL_OPEN(duration=120), NEUTRAL_CLOSED(duration=4))

    blinking = Sequence(3 * blink)

    main = Sequence(blinking)
