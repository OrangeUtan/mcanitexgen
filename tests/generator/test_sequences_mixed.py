import pytest

from mcanitexgen import generator
from mcanitexgen.generator import Animation
from mcanitexgen.parser import Duration, Sequence, SequenceAction, State, StateAction, Weight


def frame(index: int, time: int):
    return {"index": index, "time": time}


class Test_weighted_sequence_to_animation:
    @pytest.mark.parametrize(
        "actions, duration, expected_anim",
        [
            (
                [StateAction(State(0), Weight(1)), StateAction(State(1), Duration(10))],
                100,
                Animation(0, 100, [frame(0, 90), frame(1, 10)]),
            ),
            (
                [StateAction(State(0), Weight(1)), StateAction(State(1), Duration(90))],
                100,
                Animation(0, 100, [frame(0, 10), frame(1, 90)]),
            ),
            (
                [
                    StateAction(State(0), Weight(1)),
                    StateAction(State(2), Duration(10)),
                    StateAction(State(1), Weight(1)),
                ],
                100,
                Animation(0, 100, [frame(0, 45), frame(2, 10), frame(1, 45)]),
            ),
        ],
    )
    def test(self, actions, duration, expected_anim):
        sequence = Sequence(*actions)

        animation = generator.weighted_sequence_to_animation(sequence, 0, duration)
        assert animation == expected_anim


class Test_Nested_WeightedSequenceToFrames:
    def mixed_sequence():
        return Sequence(
            StateAction(State(0), Weight(1)),
            StateAction(State(1), Duration(10)),
            StateAction(State(2), Weight(1)),
        )

    @pytest.mark.parametrize(
        "actions, expected_anim",
        [
            (
                [SequenceAction(mixed_sequence(), Duration(100))],
                Animation(0, 100, [frame(0, 45), frame(1, 10), frame(2, 45)]),
            ),
        ],
    )
    def test(self, actions, expected_anim):
        sequence = Sequence(*actions)

        animation = generator.unweighted_sequence_to_animation(sequence, 0)
        assert animation == expected_anim
