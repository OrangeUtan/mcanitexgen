from mcanitexgen.animation import Sequence, State, TextureAnimation, animation


@animation("example.png")
class Example2(TextureAnimation):
    A = State(0)
    B = State(1)
    C = State(2)
    D = State(3)

    main = Sequence(A, B, C, D)
