from os import stat

import pytest
import ruamel.yaml as yaml

from mcanitexgen import generator
from mcanitexgen.generator import AnimationContext, GeneratorError, Mark
from mcanitexgen.parser import Sequence, SequenceAction, StateAction, TextureAnimation


def state(r, s=None, e=None, m=None, w=0, d=None):
    return StateAction(state=r, start=s, end=e, mark=m, weight=w, duration=d)


def sequence(ref, rep=1, s=None, e=None, m=None, w=0, d=None):
    return SequenceAction(ref=ref, repeat=rep, start=s, end=e, mark=m, weight=w, duration=d)


@pytest.fixture
def basic_context():
    return AnimationContext(
        TextureAnimation("a", None, ["A", "B", "C"], {"main": Sequence("main", [])})
    )


class Test_Constant:
    def test(self, basic_context: AnimationContext):
        seq = Sequence("a", [state("A", m="a"), state("A", d=10, m="b")])
        expected_marks = {"a": Mark("a", 0, 1), "b": Mark("b", 1, 11)}

        generator.sequence_to_frames(seq, basic_context)
        for name, mark in expected_marks.items():
            assert name in basic_context.marks
            assert mark == basic_context.marks[name]


class Test_Weighted:
    def test(self, basic_context: AnimationContext):
        seq = Sequence(
            "a", [state("A", w=1, m="a"), state("A", d=10, m="b"), state("C", w=1, m="c")]
        )
        expected_marks = {
            "a": Mark("a", 0, 50),
            "b": Mark("b", 50, 60),
            "c": Mark("c", 60, 110),
        }

        generator.sequence_to_frames(seq, basic_context, 100)
        for name, mark in expected_marks.items():
            assert name in basic_context.marks
            assert basic_context.marks[name] == mark


class Test_Nested_Constant:
    def test_deeply_nested(self, basic_context: AnimationContext):
        basic_context.anim.sequences = basic_context.anim.sequences | {
            "deep1": Sequence(
                "deep1", [sequence("deep2", m="seq1"), state("A", d=10, m="stat1")]
            ),
            "deep2": Sequence("deep2", [sequence("deep3"), state("A", d=20)]),
            "deep3": Sequence(
                "deep3", [sequence("deep4", m="seq3"), state("A", d=30, m="stat3")]
            ),
            "deep4": Sequence("deep4", [sequence("deep5"), state("A", d=40)]),
            "deep5": Sequence(
                "deep5", [sequence("deep6", m="seq5"), state("A", d=50, m="stat5")]
            ),
            "deep6": Sequence("deep6", [state("A", d=60, m="stat6")]),
        }

        seq = Sequence("a", [sequence("deep1")])
        expected_marks = {
            "stat6": Mark("stat6", 0, 60),
            "seq5": Mark("seq5", 0, 60),
            "stat5": Mark("stat5", 60, 110),
            "seq3": Mark("seq3", 0, 150),
            "stat3": Mark("stat3", 150, 180),
            "seq1": Mark("seq1", 0, 200),
            "stat1": Mark("stat1", 200, 210),
        }

        generator.sequence_to_frames(seq, basic_context)
        for name, mark in expected_marks.items():
            assert name in basic_context.marks
            assert mark == basic_context.marks[name]
