import pytest

from mcanitexgen import generator
from mcanitexgen.generator import Animation
from mcanitexgen.parser import Duration, Sequence, SequenceAction, State, StateAction, Weight


def frame(index: int, time: int):
    return {"index": index, "time": time}


class Test_Weighted:
    @pytest.mark.parametrize(
        "actions, duration, expected_anim",
        [
            (
                [StateAction(State(0), Weight(1)), StateAction(State(1), Weight(1))],
                100,
                Animation(0, 100, [frame(0, 50), frame(1, 50)]),
            ),
            (
                [StateAction(State(0), Weight(1)), StateAction(State(1), Weight(2))],
                100,
                Animation(0, 100, [frame(0, 33), frame(1, 67)]),
            ),
            (
                [
                    StateAction(State(0), Weight(3)),
                    StateAction(State(1), Weight(1)),
                    StateAction(State(2), Weight(2)),
                ],
                73,
                Animation(0, 73, [frame(0, 37), frame(1, 12), frame(2, 24)]),
            ),
        ],
    )
    def test_actions_with_duration(self, actions, duration, expected_anim):
        sequence = Sequence(*actions)

        animation = generator.weighted_sequence_to_animation(sequence, 0, duration)
        assert animation == expected_anim
        assert sum(map(lambda f: f["time"], animation.frames)) == duration


def weighted_sequence_z():
    s = Sequence(StateAction(State(0), Weight(1)), StateAction(State(1), Weight(1)))
    s.name = "weighted_z"
    return s


def weighted_sequence_y():
    s = Sequence(
        StateAction(State(0), Weight(1)),
        StateAction(State(1), Weight(1)),
        StateAction(State(2), Weight(1)),
    )
    s.name = "weighted_y"
    return s


class Test_Nested_Weighted:
    @pytest.mark.parametrize(
        "actions, expected_anim",
        [
            (
                [SequenceAction(weighted_sequence_z(), Duration(100))],
                Animation(0, 100, [frame(0, 50), frame(1, 50)]),
            ),
            (
                [SequenceAction(weighted_sequence_y(), Duration(99))],
                Animation(0, 99, [frame(0, 33), frame(1, 33), frame(2, 33)]),
            ),
            (
                [
                    SequenceAction(weighted_sequence_z(), Duration(100)),
                    StateAction(State(0), Duration(2)),
                ],
                Animation(0, 102, [frame(0, 50), frame(1, 50), frame(0, 2)]),
            ),
        ],
    )
    def test_pass_duration(self, actions, expected_anim):
        animation = generator.unweighted_sequence_to_animation(Sequence(*actions), 0)
        assert animation == expected_anim

    def test_deeply_nested(self):
        deep6 = Sequence(StateAction(State(0), Weight(2)))
        deep5 = Sequence(SequenceAction(deep6, Weight(1)))
        deep4 = Sequence(SequenceAction(deep5, Weight(1)))
        deep3 = Sequence(SequenceAction(deep4, Weight(1)))
        deep2 = Sequence(SequenceAction(deep3, Weight(1)))
        deep1 = Sequence(SequenceAction(deep2, Weight(1)))

        sequence = Sequence(SequenceAction(deep1, Duration(100)))

        animation = generator.unweighted_sequence_to_animation(sequence, 0)
        assert animation == Animation(0, 100, [frame(0, 100)])


class Test_Mixed:
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


def mixed_sequence():
    return Sequence(
        StateAction(State(0), Weight(1)),
        StateAction(State(1), Duration(10)),
        StateAction(State(2), Weight(1)),
    )


class Test_Nested_Mixed:
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
