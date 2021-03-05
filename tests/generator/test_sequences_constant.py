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

    def test_actions_with_duration(self, context: AnimationContext):
        seq = Sequence("a", [state("A", d=5), state("B", d=10)])
        expected_frames = [frame(0, 5), frame(1, 10)]
        expected_time = 15

        generator.sequence_to_frames(seq, context)

        assert context.frames == expected_frames
        assert context.end == expected_time

    @pytest.mark.parametrize(
        "actions, expected_frames, expected_time",
        [
            ([state("A", e=12), state("B", d=10)], [frame(0, 12), frame(1, 10)], 22),
            ([state("A", d=14), state("B", e=100)], [frame(0, 14), frame(1, 86)], 100),
        ],
    )
    def test_actions_with_end(
        self,
        actions,
        expected_frames,
        expected_time,
        context: AnimationContext,
    ):
        seq = Sequence("a", actions)

        generator.sequence_to_frames(seq, context)

        assert context.frames == expected_frames
        assert context.end == expected_time

    @pytest.mark.parametrize(
        "actions, expected_frames, expected_time",
        [
            ([state("A", d=14), state("B", s=20, d=10)], [frame(0, 20), frame(1, 10)], 30),
            ([state("A", d=14), state("B", s=20)], [frame(0, 20), frame(1, 1)], 21),
        ],
    )
    def test_actions_with_start(
        self, actions, expected_frames, expected_time, context: AnimationContext
    ):
        seq = Sequence("a", actions)

        generator.sequence_to_frames(seq, context)

        assert context.frames == expected_frames
        assert context.end == expected_time

    def test_pass_duration_to_constant_sequence(self, context: AnimationContext):
        seq = Sequence("a", [state("A", d=100)])

        with pytest.raises(GeneratorError, match=".*duration.*"):
            generator.sequence_to_frames(seq, context, 100)


class Test_Nested_SequenceToFrames:
    @pytest.fixture
    def context(self):
        sequences = {
            "main": Sequence("main", []),
            "y": Sequence("y", [state("A", d=10)]),
            "z": Sequence("z", [state("A", d=10), state("B", d=5)]),
        }

        return AnimationContext(TextureAnimation("a", None, ["A", "B", "C"], sequences))

    @pytest.mark.parametrize(
        "actions, expected_frames, expected_time",
        [
            ("[z()]", [frame(0, 10), frame(1, 5)], 15),
            ("[z(), A: {duration: 15}]", [frame(0, 10), frame(1, 5), frame(0, 15)], 30),
        ],
    )
    def test_nesting_without_args(
        self, actions, expected_frames, expected_time, context: AnimationContext
    ):
        seq = Sequence.from_json("b", yaml.safe_load(actions))

        generator.sequence_to_frames(seq, context)

        assert context.frames == expected_frames
        assert context.end == expected_time

    def test_deeply_nested(self, context: AnimationContext):
        context.anim.sequences = context.anim.sequences | {
            "deep1": Sequence("deep1", [sequence("deep2"), state("A", d=10)]),
            "deep2": Sequence("deep2", [sequence("deep3"), state("A", d=20)]),
            "deep3": Sequence("deep3", [sequence("deep4"), state("A", d=30)]),
            "deep4": Sequence("deep4", [sequence("deep5"), state("A", d=40)]),
            "deep5": Sequence("deep5", [sequence("deep6"), state("A", d=50)]),
            "deep6": Sequence("deep6", [state("A", d=60)]),
        }

        seq = Sequence("a", [sequence("deep1")])
        expected_frames = [
            frame(0, 60),
            frame(0, 50),
            frame(0, 40),
            frame(0, 30),
            frame(0, 20),
            frame(0, 10),
        ]

        generator.sequence_to_frames(seq, context)

        assert context.frames == expected_frames
        assert context.end == 210

    def test_pass_duration_to_constant_sequence(self, context: AnimationContext):
        seq = Sequence("a", [sequence("z", d=100)])

        with pytest.raises(GeneratorError, match=".*duration.*"):
            generator.sequence_to_frames(seq, context)
