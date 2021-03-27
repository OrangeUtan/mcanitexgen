from mcanitexgen.animation import Sequence, State, TextureAnimation, animation


@animation("head.png")
class Head(TextureAnimation):
    NEUTRAL_OPEN = State(0)
    NEUTRAL_CLOSED = State(1)

    blink = Sequence(NEUTRAL_OPEN(weight=1), NEUTRAL_CLOSED(duration=4))

    blinking = Sequence(2 * blink(weight=1), NEUTRAL_CLOSED(duration=4))

    main = Sequence(2 * blinking(duration=39))
