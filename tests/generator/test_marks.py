import pytest

from mcanitexgen import generator
from mcanitexgen.generator import Mark
from mcanitexgen.parser import (
    Duration,
    Sequence,
    SequenceAction,
    StateAction,
    TextureAnimation,
    Weight,
)


def _state(*args, **kwargs):
    return StateAction(*args, **kwargs)


def _sequence(*args, **kwargs):
    return SequenceAction(*args, **kwargs)


@pytest.fixture
def texture_anim():
    return TextureAnimation("a", None, ["A", "B", "C"], {"main": Sequence("main", [])})


class Test_Unweighted:
    def test(self, texture_anim: TextureAnimation):
        sequence = Sequence("a", [_state("A", mark="a"), _state("A", Duration(10), mark="b")])
        expected_marks = {"a": Mark(0, 1), "b": Mark(1, 11)}

        animation = generator.unweighted_sequence_to_animation(sequence, 0, texture_anim)
        assert animation.marks == expected_marks


class Test_Weighted:
    def test(self, texture_anim: TextureAnimation):
        sequence = Sequence(
            "a",
            [
                _state("A", Weight("1"), mark="a"),
                _state("A", Duration("10"), mark="b"),
                _state("C", Weight("1"), mark="c"),
            ],
        )
        expected_marks = {
            "a": Mark(0, 45),
            "b": Mark(45, 55),
            "c": Mark(55, 100),
        }

        animation = generator.weighted_sequence_to_animation(sequence, 0, 100, texture_anim)
        assert animation.marks == expected_marks


class Test_Nested_Unweighted:
    def test_deeply_nested(self, texture_anim: TextureAnimation):
        texture_anim.sequences |= {
            "deep1": Sequence(
                "deep1",
                [
                    _sequence("deep2", mark="seq1"),
                    _state("A", Duration("10"), mark="stat1"),
                ],
            ),
            "deep2": Sequence("deep2", [_sequence("deep3"), _state("A", Duration("20"))]),
            "deep3": Sequence(
                "deep3",
                [
                    _sequence("deep4", mark="seq3"),
                    _state("A", Duration("30"), mark="stat3"),
                ],
            ),
            "deep4": Sequence("deep4", [_sequence("deep5"), _state("A", Duration("40"))]),
            "deep5": Sequence(
                "deep5",
                [
                    _sequence("deep6", mark="seq5"),
                    _state("A", Duration("50"), mark="stat5"),
                ],
            ),
            "deep6": Sequence("deep6", [_state("A", Duration("60"), mark="stat6")]),
        }

        sequence = Sequence("a", [SequenceAction("deep1")])
        expected_marks = {
            "stat6": Mark(0, 60),
            "seq5": Mark(0, 60),
            "stat5": Mark(60, 110),
            "seq3": Mark(0, 150),
            "stat3": Mark(150, 180),
            "seq1": Mark(0, 200),
            "stat1": Mark(200, 210),
        }

        animation = generator.unweighted_sequence_to_animation(sequence, 0, texture_anim)
        assert animation.marks == expected_marks
