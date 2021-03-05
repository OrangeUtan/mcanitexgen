import pytest
import ruamel.yaml as yaml

from mcanitexgen import generator
from mcanitexgen.generator import AnimationContext, GeneratorError
from mcanitexgen.parser import Sequence, SequenceAction, StateAction, TextureAnimation


def frame(index: int, time: int):
    return {"index": index, "time": time}


def state(r, s=None, e=None, m=None, w=0, d=None):
    return StateAction(state=r, start=s, end=e, mark=m, weight=w, duration=d)


def sequence(ref, rep=1, s=None, e=None, m=None, w=0, d=None):
    return SequenceAction(ref=ref, repeat=rep, start=s, end=e, mark=m, weight=w, duration=d)


class Test_SequenceToFrames:
    @pytest.fixture
    def context(self):
        return AnimationContext(
            TextureAnimation("a", None, ["A", "B", "C"], {"main": Sequence("main", [])})
        )

    @pytest.mark.parametrize(
        "actions, duration, expected_frames",
        [
            ([state("A", w=1), state("B", w=1)], 100, [frame(0, 50), frame(1, 50)]),
            ([state("A", w=1), state("B", w=2)], 100, [frame(0, 33), frame(1, 67)]),
        ],
    )
    def test_actions_with_duration(
        self, actions, duration, expected_frames, context: AnimationContext
    ):
        seq = Sequence("a", actions)

        generator.sequence_to_frames(seq, context, duration)

        assert context.frames == expected_frames
        assert context.end == duration

    def test_dont_pass_duration_to_weighted_sequence(self, context: AnimationContext):
        seq = Sequence("a", [state("A", w=1)])

        with pytest.raises(GeneratorError, match=".*duration.*"):
            generator.sequence_to_frames(seq, context, None)


class Test_Nested_SequenceToFrames:
    @pytest.fixture
    def context(self):
        sequences = {
            "main": Sequence("main", []),
            "y": Sequence("z", [state("A", w=1), state("B", w=1), state("C", w=1)]),
            "z": Sequence("z", [state("A", w=1), state("B", w=1)]),
        }
        return AnimationContext(TextureAnimation("a", None, ["A", "B", "C"], sequences))

    @pytest.mark.parametrize(
        "actions, expected_frames, expected_time",
        [
            ("[z(): {duration: 100}]", [frame(0, 50), frame(1, 50)], 100),
            ("[y(): {duration: 99}]", [frame(0, 33), frame(1, 33), frame(2, 33)], 99),
            (
                "[z(): {duration: 100}, A: {duration: 2}]",
                [frame(0, 50), frame(1, 50), frame(0, 2)],
                102,
            ),
        ],
    )
    def test_pass_duration(
        self, actions, expected_frames, expected_time, context: AnimationContext
    ):
        seq = Sequence.from_json("a", yaml.safe_load(actions))

        generator.sequence_to_frames(seq, context)

        assert context.frames == expected_frames
        assert context.end == expected_time

    def test_deeply_nested(self, context: AnimationContext):
        context.anim.sequences = context.anim.sequences | {
            "deep1": Sequence("deep1", [sequence("deep2", w=1)]),
            "deep2": Sequence("deep2", [sequence("deep3", w=1)]),
            "deep3": Sequence("deep3", [sequence("deep4", w=1)]),
            "deep4": Sequence("deep4", [sequence("deep5", w=1)]),
            "deep5": Sequence("deep5", [sequence("deep6", w=1)]),
            "deep6": Sequence("deep6", [state("A", w=2)]),
        }

        seq = Sequence("a", [sequence("deep1", d=100)])
        expected_frames = [frame(0, 100)]

        generator.sequence_to_frames(seq, context)

        assert context.frames == expected_frames
        assert context.end == 100
