from mcanitexgen.animation import Sequence, State, TextureAnimation, animation


@animation("head.png")
class Head(TextureAnimation):
    A = State(0)
    B = State(1)

    nested_unweighted = Sequence(A(duration=4))

    weighted = Sequence(B(weight=1), nested_unweighted)

    main = Sequence(weighted(duration=120))
