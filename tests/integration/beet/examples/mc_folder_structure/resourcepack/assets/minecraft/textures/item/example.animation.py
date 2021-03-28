from mcanitexgen.animation import Sequence, State, TextureAnimation, animation


@animation("example.png")
class Example(TextureAnimation):
    A = State(0)
    B = State(1)

    main = Sequence(A, B, A)
