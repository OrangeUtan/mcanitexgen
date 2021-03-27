import pytest

from mcanitexgen.animation import generator
from mcanitexgen.animation.generator import GeneratorError
from mcanitexgen.animation.parser import (
    Duration,
    Sequence,
    SequenceAction,
    State,
    StateAction,
    Weight,
)


class Test_Unweighted:
    @classmethod
    def unweighted_sequence(cls):
        s = Sequence(StateAction(State(0), Duration(10)), StateAction(State(1), Duration(5)))
        s.name = "unweighted"
        return s

    def test_pass_duration_to_unweighted_sequence(self):
        action = SequenceAction(Test_Unweighted.unweighted_sequence(), Duration(100))

        with pytest.raises(
            GeneratorError, match="Passing duration to unweighted sequence 'unweighted'"
        ):
            generator.sequence_action_to_animation(action, 0, 100)


class Test_Weighted:
    @classmethod
    def weighted_sequence(cls):
        s = Sequence(StateAction(State(0), Weight(1)), StateAction(State(1), Weight(1)))
        s.name = "weighted"
        return s

    def test_dont_pass_duration_to_weighted_sequence(self):
        action = SequenceAction(Test_Weighted.weighted_sequence())

        with pytest.raises(
            GeneratorError, match="Didn't pass duration to weighted sequence 'weighted'"
        ):
            generator.sequence_action_to_animation(action, 0, None)
