from mcanitexgen import generator
from mcanitexgen.generator import Mark
from mcanitexgen.parser import Duration, Sequence, SequenceAction, State, StateAction, Weight


class Test_Unweighted:
    def test(self):
        sequence = Sequence(
            StateAction(State(0), Duration(1), mark="a"),
            StateAction(State(0), Duration(10), mark="b"),
        )
        expected_marks = {"a": Mark(0, 1), "b": Mark(1, 11)}

        animation = generator.unweighted_sequence_to_animation(sequence, 0)
        assert animation.marks == expected_marks


class Test_Weighted:
    def test(self):
        sequence = Sequence(
            StateAction(State(0), Weight("1"), mark="a"),
            StateAction(State(0), Duration("10"), mark="b"),
            StateAction(State(2), Weight("1"), mark="c"),
        )
        expected_marks = {
            "a": Mark(0, 45),
            "b": Mark(45, 55),
            "c": Mark(55, 100),
        }

        animation = generator.weighted_sequence_to_animation(sequence, 0, 100)
        assert animation.marks == expected_marks


class Test_Nested_Unweighted:
    def test_deeply_nested(self):
        deep6 = Sequence(StateAction(State(0), Duration("60"), mark="stat6"))
        deep5 = Sequence(
            SequenceAction(deep6, mark="seq5"),
            StateAction(State(0), Duration("50"), mark="stat5"),
        )
        deep4 = Sequence(SequenceAction(deep5), StateAction(State(0), Duration("40")))
        deep3 = Sequence(
            SequenceAction(deep4, mark="seq3"),
            StateAction(State(0), Duration("30"), mark="stat3"),
        )
        deep2 = Sequence(SequenceAction(deep3), StateAction(State(0), Duration("20")))
        deep1 = Sequence(
            SequenceAction(deep2, mark="seq1"),
            StateAction(State(0), Duration("10"), mark="stat1"),
        )

        expected_marks = {
            "stat6": Mark(0, 60),
            "seq5": Mark(0, 60),
            "stat5": Mark(60, 110),
            "seq3": Mark(0, 150),
            "stat3": Mark(150, 180),
            "seq1": Mark(0, 200),
            "stat1": Mark(200, 210),
        }

        animation = generator.unweighted_sequence_to_animation(Sequence(deep1), 0)
        assert animation.marks == expected_marks
