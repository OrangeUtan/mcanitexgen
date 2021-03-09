import pytest
import ruamel.yaml as yaml

from mcanitexgen import generator
from mcanitexgen.generator import Animation, GeneratorError
from mcanitexgen.parser import (
    Duration,
    Sequence,
    SequenceAction,
    StateAction,
    TextureAnimation,
    Weight,
)


def frame(index: int, time: int):
    return {"index": index, "time": time}


@pytest.fixture
def texture_anim():
    return TextureAnimation("a", None, ["A", "B", "C"], {"main": Sequence("main", [])})


class Test_WeightedSequenceToAnimation:
    @pytest.mark.parametrize(
        "actions, duration, expected_anim",
        [
            (
                [StateAction("A", Weight(1)), StateAction("B", Weight(1))],
                100,
                Animation(0, 100, [frame(0, 50), frame(1, 50)]),
            ),
            (
                [StateAction("A", Weight(1)), StateAction("B", Weight(2))],
                100,
                Animation(0, 100, [frame(0, 33), frame(1, 67)]),
            ),
            (
                [
                    StateAction("A", Weight(3)),
                    StateAction("B", Weight(1)),
                    StateAction("C", Weight(2)),
                ],
                73,
                Animation(0, 73, [frame(0, 37), frame(1, 12), frame(2, 24)]),
            ),
        ],
    )
    def test_actions_with_duration(
        self, actions, duration, expected_anim, texture_anim: TextureAnimation
    ):
        sequence = Sequence("a", actions)

        animation = generator.weighted_sequence_to_animation(
            sequence, 0, duration, texture_anim
        )
        assert animation == expected_anim
        assert sum(map(lambda f: f["time"], animation.frames)) == duration


class Test_Nested_WeightedSequenceToAnimation:
    @pytest.fixture
    def texture_anim(self):
        sequences = {
            "main": Sequence("main", []),
            "y": Sequence(
                "z",
                [
                    StateAction("A", Weight(1)),
                    StateAction("B", Weight(1)),
                    StateAction("C", Weight(1)),
                ],
            ),
            "z": Sequence("z", [StateAction("A", Weight(1)), StateAction("B", Weight(1))]),
        }
        return TextureAnimation("a", None, ["A", "B", "C"], sequences)

    @pytest.mark.parametrize(
        "actions, expected_anim",
        [
            ("[z(): {duration: 100}]", Animation(0, 100, [frame(0, 50), frame(1, 50)])),
            (
                "[y(): {duration: 99}]",
                Animation(0, 99, [frame(0, 33), frame(1, 33), frame(2, 33)]),
            ),
            (
                "[z(): {duration: 100}, A: {duration: 2}]",
                Animation(0, 102, [frame(0, 50), frame(1, 50), frame(0, 2)]),
            ),
        ],
    )
    def test_pass_duration(self, actions, expected_anim, texture_anim: TextureAnimation):
        sequence = Sequence.from_json("a", yaml.safe_load(actions))
        animation = generator.unweighted_sequence_to_animation(sequence, 0, texture_anim)
        assert animation == expected_anim

    def test_deeply_nested(self, texture_anim: TextureAnimation):
        texture_anim.sequences |= {
            "deep1": Sequence("deep1", [SequenceAction("deep2", Weight(1))]),
            "deep2": Sequence("deep2", [SequenceAction("deep3", Weight(1))]),
            "deep3": Sequence("deep3", [SequenceAction("deep4", Weight(1))]),
            "deep4": Sequence("deep4", [SequenceAction("deep5", Weight(1))]),
            "deep5": Sequence("deep5", [SequenceAction("deep6", Weight(1))]),
            "deep6": Sequence("deep6", [StateAction("A", Weight(2))]),
        }

        sequence = Sequence("a", [SequenceAction("deep1", Duration(100))])
        animation = generator.unweighted_sequence_to_animation(sequence, 0, texture_anim)
        assert animation == Animation(0, 100, [frame(0, 100)])


class Test_sequence_action_to_animation:
    def test_dont_pass_duration_to_weighted_sequence(self, texture_anim: TextureAnimation):
        texture_anim.sequences["a"] = Sequence("a", [StateAction("A", Weight(1))])

        with pytest.raises(GeneratorError, match=".*'a'.*"):
            generator.sequence_action_to_animation(
                SequenceAction("a", None), 0, None, texture_anim, {}
            )
