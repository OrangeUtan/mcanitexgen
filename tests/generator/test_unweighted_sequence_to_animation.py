import pytest

from mcanitexgen import generator
from mcanitexgen.generator import Animation, GeneratorError
from mcanitexgen.parser import (
    Duration,
    Sequence,
    SequenceAction,
    State,
    StateAction,
    Timeframe,
)


def frame(index: int, time: int):
    return {"index": index, "time": time}


class Test_unweighted_sequence_to_animation:
    def test_actions_with_duration(self):
        sequence = Sequence(
            StateAction(State(0), Duration(5)), StateAction(State(1), Duration(10))
        )

        animation = generator.unweighted_sequence_to_animation(sequence, 0)
        assert animation == Animation(0, 15, [frame(0, 5), frame(1, 10)])

    @pytest.mark.parametrize(
        "actions, expected_animation",
        [
            # End
            (
                [
                    StateAction(State(0), Timeframe(end=12)),
                    StateAction(State(1), Duration(10)),
                ],
                Animation(0, 22, [frame(0, 12), frame(1, 10)]),
            ),
            (
                [
                    StateAction(State(0), Duration(14)),
                    StateAction(State(1), Timeframe(end=100)),
                ],
                Animation(0, 100, [frame(0, 14), frame(1, 86)]),
            ),
            # Start
            (
                [
                    StateAction(State(0), Duration(14)),
                    StateAction(State(1), Timeframe(start=20, duration=10)),
                ],
                Animation(0, 30, [frame(0, 20), frame(1, 10)]),
            ),
            (
                [
                    StateAction(State(0), Duration(14)),
                    StateAction(State(1), Timeframe(start=20)),
                ],
                Animation(0, 21, [frame(0, 20), frame(1, 1)]),
            ),
        ],
    )
    def test_actions_with_timeframe(self, actions, expected_animation):
        sequence = Sequence(*actions)

        animation = generator.unweighted_sequence_to_animation(sequence, 0)
        assert animation == expected_animation


def unweighted_sequence():
    s = Sequence(StateAction(State(0), Duration(10)), StateAction(State(1), Duration(5)))
    s.name = "unweighted"
    return s


class Test_Nested_unweighted_sequence_to_animation:
    @pytest.mark.parametrize(
        "actions, expected_anim",
        [
            ([unweighted_sequence()], Animation(0, 15, [frame(0, 10), frame(1, 5)])),
            (
                [unweighted_sequence(), StateAction(State(0), Duration(15))],
                Animation(0, 30, [frame(0, 10), frame(1, 5), frame(0, 15)]),
            ),
        ],
    )
    def test_nesting_without_args(self, actions, expected_anim):
        sequence = Sequence(*actions)

        animation = generator.unweighted_sequence_to_animation(sequence, 0)
        assert animation == expected_anim

    def test_deeply_nested(self):
        deep6 = Sequence(StateAction(State(0), Duration(60)))
        deep5 = Sequence(deep6, StateAction(State(0), Duration(50)))
        deep4 = Sequence(deep5, StateAction(State(0), Duration(40)))
        deep3 = Sequence(deep4, StateAction(State(0), Duration(30)))
        deep2 = Sequence(deep3, StateAction(State(0), Duration(20)))
        deep1 = Sequence(deep2, StateAction(State(0), Duration(10)))

        sequence = Sequence(deep1)
        expected_animation = Animation(
            0,
            210,
            [
                frame(0, 60),
                frame(0, 50),
                frame(0, 40),
                frame(0, 30),
                frame(0, 20),
                frame(0, 10),
            ],
        )

        animation = generator.unweighted_sequence_to_animation(sequence, 0)
        assert animation == expected_animation

    def test_pass_duration_to_unweighted_sequence(self):
        sequence = Sequence(
            SequenceAction(
                unweighted_sequence(),
                Duration("100"),
            ),
        )

        with pytest.raises(
            GeneratorError, match="Passing duration to unweighted sequence 'unweighted'"
        ):
            generator.unweighted_sequence_to_animation(sequence, 0)
