import pytest
import ruamel.yaml as yaml

from mcanitexgen import generator
from mcanitexgen.generator import AnimationContext, GeneratorError
from mcanitexgen.parser import Sequence, SequenceAction, StateAction, TextureAnimation


def frame(index: int, time: int):
    return {"index": index, "time": time}


def state(r, s=None, e=None, m=None, w=0, d=None):
    return StateAction(state=r, start=s, end=e, mark=m, weight=w, duration=d)


def sequence(seq, rep=1, s=None, e=None, m=None, w=0, d=None):
    return SequenceAction(ref=seq, repeat=rep, start=s, end=e, mark=m, weight=w, duration=d)


class Test_SequenceToFrames:
    @pytest.fixture
    def context(self):
        return AnimationContext(
            TextureAnimation("anim", None, ["A", "B", "C"], {"main": Sequence("main", [])})
        )

    @pytest.mark.parametrize(
        "actions, duration, expected_frames",
        [
            ("[A: {weight: 1}, B: {duration: 10}]", 100, [frame(0, 100), frame(1, 10)]),
            (
                "[A: {weight: 1}, C: {duration: 10}, B: {weight: 1}]",
                100,
                [frame(0, 50), frame(2, 10), frame(1, 50)],
            ),
        ],
    )
    def test(self, actions, duration, expected_frames, context: AnimationContext):
        seq = Sequence.from_json("a", yaml.safe_load(actions), context.anim.sequences)

        generator.sequence_to_frames(seq, context, duration)
        assert context.frames == expected_frames


class Test_SequenceToFrames:
    @pytest.fixture
    def context(self):
        sequences = {
            "main": Sequence("main", []),
            "mixed": Sequence("z", [state("A", w=1), state("B", d=10), state("C", w=1)]),
        }
        return AnimationContext(TextureAnimation("a", None, ["A", "B", "C"], sequences))

    @pytest.mark.parametrize(
        "actions, expected_frames, expected_duration",
        [
            ("[mixed(): {duration: 100}]", [frame(0, 45), frame(1, 10), frame(2, 45)], 100),
        ],
    )
    def test(self, actions, expected_frames, expected_duration, context: AnimationContext):
        seq = Sequence.from_json("a", yaml.safe_load(actions))

        generator.sequence_to_frames(seq, context)

        assert context.frames == expected_frames
        assert context.end == expected_duration
