from mcanitexgen.animation import Sequence, State, TextureAnimation, animation


@animation("minecraft:item/example1.png")
class Example1(TextureAnimation):
    A = State(0)
    B = State(1)

    main = Sequence(A, B, A)
