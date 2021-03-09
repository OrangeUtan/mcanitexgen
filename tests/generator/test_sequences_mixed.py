import pytest
import ruamel.yaml as yaml

from mcanitexgen import generator
from mcanitexgen.generator import Animation
from mcanitexgen.parser import Duration, Sequence, StateAction, TextureAnimation, Weight


def frame(index: int, time: int):
    return {"index": index, "time": time}


@pytest.fixture
def texture_anim():
    return TextureAnimation("anim", None, ["A", "B", "C"], {"main": Sequence("main", [])})


class Test_WeightedSequenceToFrames:
    @pytest.mark.parametrize(
        "actions, duration, expected_anim",
        [
            (
                "[A: {weight: 1}, B: {duration: 10}]",
                100,
                Animation(0, 100, [frame(0, 90), frame(1, 10)]),
            ),
            (
                "[A: {weight: 1}, B: {duration: 90}]",
                100,
                Animation(0, 100, [frame(0, 10), frame(1, 90)]),
            ),
            (
                "[A: {weight: 1}, C: {duration: 10}, B: {weight: 1}]",
                100,
                Animation(0, 100, [frame(0, 45), frame(2, 10), frame(1, 45)]),
            ),
        ],
    )
    def test(self, actions, duration, expected_anim, texture_anim: TextureAnimation):
        sequence = Sequence.from_json("a", yaml.safe_load(actions))

        animation = generator.weighted_sequence_to_animation(
            sequence, 0, duration, texture_anim
        )
        assert animation == expected_anim


class Test_Nested_WeightedSequenceToFrames:
    @pytest.fixture()
    def texture_anim(self):
        sequences = {
            "main": Sequence("main", []),
            "m": Sequence(
                "z",
                [
                    StateAction("A", Weight(1)),
                    StateAction("B", Duration("10")),
                    StateAction("C", Weight(1)),
                ],
            ),
        }
        return TextureAnimation("a", None, ["A", "B", "C"], sequences)

    @pytest.mark.parametrize(
        "actions, expected_anim",
        [
            (
                "[m(): {duration: 100}]",
                Animation(0, 100, [frame(0, 45), frame(1, 10), frame(2, 45)]),
            ),
        ],
    )
    def test(self, actions, expected_anim, texture_anim: TextureAnimation):
        sequence = Sequence.from_json("a", yaml.safe_load(actions))

        animation = generator.unweighted_sequence_to_animation(sequence, 0, texture_anim)
        assert animation == expected_anim
