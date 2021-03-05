from os import stat

import pytest
import ruamel.yaml as yaml

from mcanitexgen import generator
from mcanitexgen.generator import AnimationContext, GeneratorError, Mark
from mcanitexgen.parser import Sequence, SequenceAction, StateAction, TextureAnimation
from tests.generator.test_sequences_constant import frame


def state(r, s=None, e=None, m=None, w=0, d=None):
    return StateAction(state=r, start=s, end=e, mark=m, weight=w, duration=d)


def sequence(ref, rep=1, s=None, e=None, m=None, w=0, d=None):
    return SequenceAction(ref=ref, repeat=rep, start=s, end=e, mark=m, weight=w, duration=d)


@pytest.fixture
def basic_context():
    return AnimationContext(
        TextureAnimation("a", None, ["A", "B", "C"], {"main": Sequence("main", [])})
    )


@pytest.fixture
def marked_context():
    ctx = AnimationContext(
        TextureAnimation("m", None, ["A", "B", "C"], {"main": Sequence("main", [])})
    )
    ctx.marks = {
        "a": Mark("a", 0, 1),
        "b": Mark("b", 1, 10),
        "c": Mark("c", 10, 100),
    }
    ctx.frames = [frame(0, 1)]
    ctx.advance_time_to(100)
    return ctx


def parsed_context():
    ctx = AnimationContext(
        TextureAnimation("a", None, ["A", "B", "C"], {"main": Sequence("main", [])})
    )

    generator.sequence_to_frames()


@pytest.mark.parametrize(
    "actions, expected_frames",
    [
        # int literal
        ("[A, B: {start: 10, duration: 10}]", [frame(0, 10), frame(1, 10)]),
        ("[A: {end: 3342}]", [frame(0, 3342)]),
        ("[A: {duration: 3342}]", [frame(0, 3342)]),
        # Simple arithmetic
        ("[A, B: {start: 3*3, duration: 10}]", [frame(0, 9), frame(1, 10)]),
        ("[A: {end: 3*3}]", [frame(0, 9)]),
        ("[A: {duration: 3*3}]", [frame(0, 9)]),
    ],
)
def test_start_end_duration_are_parsed(
    actions, expected_frames, basic_context: AnimationContext
):
    seq = Sequence.from_json("a", yaml.safe_load(actions))

    generator.sequence_to_frames(seq, basic_context)
    assert basic_context.frames == expected_frames


@pytest.mark.parametrize(
    "actions, expected_frames",
    [
        ("[A: {end: 'pow(3,3)'}]", [frame(0, 27)]),
        ("[A: {duration: 'mod(230,100)'}]", [frame(0, 30)]),
        (
            "[A, B: {start: 'ceil(12.1123574687456)', duration: 10}]",
            [frame(0, 13), frame(1, 10)],
        ),
    ],
)
def test_arithmetic_functions(actions, expected_frames, basic_context: AnimationContext):
    seq = Sequence.from_json("a", yaml.safe_load(actions))

    generator.sequence_to_frames(seq, basic_context)
    assert basic_context.frames == expected_frames


def test_reference_animation_end(
    basic_context: AnimationContext, marked_context: AnimationContext
):
    basic_context._eval_locals = {marked_context.anim.name: marked_context}

    seq = Sequence("a", [state("A"), state("B", s="m.end / 2")])
    generator.sequence_to_frames(seq, basic_context)

    assert basic_context.frames == [frame(0, 50), frame(1, 1)]


def test_reference_animation_mark(
    basic_context: AnimationContext, marked_context: AnimationContext
):
    basic_context._eval_locals = {marked_context.anim.name: marked_context}

    seq = Sequence("a", [state("A"), state("B", s="m.mark('c').start + 5")])
    generator.sequence_to_frames(seq, basic_context)

    assert basic_context.frames == [frame(0, 15), frame(1, 1)]
