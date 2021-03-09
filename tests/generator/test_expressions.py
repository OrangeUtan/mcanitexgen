from os import stat

import pytest
import ruamel.yaml as yaml

from mcanitexgen import generator
from mcanitexgen.generator import Animation, Mark
from mcanitexgen.parser import Sequence, TextureAnimation, Timeframe


def frame(index: int, time: int):
    return {"index": index, "time": time}


@pytest.fixture
def texture_anim():
    return TextureAnimation("a", None, ["A", "B", "C"], {"main": Sequence("main", [])})


@pytest.fixture
def marked_anim():
    marks = {
        "a": Mark(0, 1),
        "b": Mark(1, 10),
        "c": Mark(10, 100),
    }

    return Animation(0, 100, [frame(0, 100)], marks)


class Test_EvaluateTimeframe:
    @pytest.mark.parametrize(
        "timeframe, expected",
        [
            (Timeframe(start="ceil(12.1123574687456)"), (13, 14, 1)),
            (Timeframe(start="sqrt(16)", duration="mod(230,100)"), (4, 34, 30)),
            (Timeframe(end="pow(3,3)"), (None, 27, None)),
            (Timeframe(start="sqrt(16)", end="12"), (4, 12, 8)),
        ],
    )
    def test_only_arithmetic(self, timeframe: Timeframe, expected):
        assert generator.evaluate_timeframe(timeframe, {}) == expected

    @pytest.mark.parametrize(
        "timeframe, expected",
        [
            (Timeframe(start="m.mark('a').start + 10"), (10, 11, 1)),
            (Timeframe(start="m.mark('a').end + 10"), (11, 12, 1)),
            (Timeframe(start="m.mark('b').end + 10", duration="20"), (20, 40, 20)),
        ],
    )
    def test_reference_marks(self, timeframe: Timeframe, expected, marked_anim: Animation):
        expr_locals = {"m": marked_anim}
        assert generator.evaluate_timeframe(timeframe, expr_locals) == expected

    @pytest.mark.parametrize(
        "timeframe, expected",
        [
            (Timeframe(start="m.end"), (100, 101, 1)),
            (Timeframe(start="m.end / 2"), (50, 51, 1)),
        ],
    )
    def test_reference_animation(elf, timeframe: Timeframe, expected, marked_anim: Animation):
        expr_locals = {"m": marked_anim}
        assert generator.evaluate_timeframe(timeframe, expr_locals) == expected


class Test_GeneratedAnimation:
    @pytest.mark.parametrize(
        "actions_json, expected_anim",
        [
            # int literal
            (
                "[A, B: {start: 10, duration: 10}]",
                Animation(0, 20, [frame(0, 10), frame(1, 10)]),
            ),
            ("[A: {end: 3342}]", Animation(0, 3342, [frame(0, 3342)])),
            ("[A: {duration: 3342}]", Animation(0, 3342, [frame(0, 3342)])),
            # Simple arithmetic
            (
                "[A, B: {start: 3*3, duration: 10}]",
                Animation(0, 19, [frame(0, 9), frame(1, 10)]),
            ),
            ("[A: {end: 3*3}]", Animation(0, 9, [frame(0, 9)])),
            ("[A: {duration: 3*3}]", Animation(0, 9, [frame(0, 9)])),
        ],
    )
    def test_start_end_duration_are_parsed(
        self, actions_json, expected_anim, texture_anim: TextureAnimation
    ):
        sequence = Sequence.from_json("main", yaml.safe_load(actions_json))

        animation = generator.unweighted_sequence_to_animation(sequence, 0, texture_anim)
        assert animation == expected_anim
