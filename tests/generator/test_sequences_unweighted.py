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
    Timeframe,
)


def frame(index: int, time: int):
    return {"index": index, "time": time}


@pytest.fixture
def texture_anim():
    return TextureAnimation("a", None, ["A", "B", "C"], {"main": Sequence("main", [])})


class Test_unweighted_sequence_to_animation:
    def test_actions_with_duration(self, texture_anim: TextureAnimation):
        sequence = Sequence(
            "a", [StateAction("A", Duration("5")), StateAction("B", Duration("10"))]
        )

        animation = generator.unweighted_sequence_to_animation(sequence, 0, texture_anim)
        assert animation == Animation(0, 15, [frame(0, 5), frame(1, 10)])

    @pytest.mark.parametrize(
        "actions, expected_animation",
        [
            # End
            (
                [StateAction("A", Timeframe(end="12")), StateAction("B", Duration(10))],
                Animation(0, 22, [frame(0, 12), frame(1, 10)]),
            ),
            (
                [StateAction("A", Duration(14)), StateAction("B", Timeframe(end="100"))],
                Animation(0, 100, [frame(0, 14), frame(1, 86)]),
            ),
            # Start
            (
                [
                    StateAction("A", Duration("14")),
                    StateAction("B", Timeframe(start="20", duration="10")),
                ],
                Animation(0, 30, [frame(0, 20), frame(1, 10)]),
            ),
            (
                [StateAction("A", Duration("14")), StateAction("B", Timeframe(start="20"))],
                Animation(0, 21, [frame(0, 20), frame(1, 1)]),
            ),
        ],
    )
    def test_actions_timeframe(
        self, actions, expected_animation, texture_anim: TextureAnimation
    ):
        sequence = Sequence("main", actions)

        animation = generator.unweighted_sequence_to_animation(sequence, 0, texture_anim)
        assert animation == expected_animation


class Test_nested_unweighted_sequence_to_animation:
    @pytest.fixture
    def texture_anim(self):
        sequences = {
            "main": Sequence("main", []),
            "y": Sequence("y", [StateAction("A", Duration("10"))]),
            "z": Sequence(
                "z", [StateAction("A", Duration("10")), StateAction("B", Duration("5"))]
            ),
        }

        return TextureAnimation("a", None, ["A", "B", "C"], sequences)

    @pytest.mark.parametrize(
        "actions, expected_anim",
        [
            ("[z()]", Animation(0, 15, [frame(0, 10), frame(1, 5)])),
            (
                "[z(), A: {duration: 15}]",
                Animation(0, 30, [frame(0, 10), frame(1, 5), frame(0, 15)]),
            ),
        ],
    )
    def test_nesting_without_args(
        self, actions, expected_anim, texture_anim: TextureAnimation
    ):
        sequence = Sequence.from_json("a", yaml.safe_load(actions))

        animation = generator.unweighted_sequence_to_animation(sequence, 0, texture_anim)
        assert animation == expected_anim

    def test_deeply_nested(self, texture_anim: TextureAnimation):
        texture_anim.sequences |= {
            "deep1": Sequence(
                "deep1", [SequenceAction("deep2"), StateAction("A", Duration("10"))]
            ),
            "deep2": Sequence(
                "deep2", [SequenceAction("deep3"), StateAction("A", Duration("20"))]
            ),
            "deep3": Sequence(
                "deep3", [SequenceAction("deep4"), StateAction("A", Duration("30"))]
            ),
            "deep4": Sequence(
                "deep4", [SequenceAction("deep5"), StateAction("A", Duration("40"))]
            ),
            "deep5": Sequence(
                "deep5", [SequenceAction("deep6"), StateAction("A", Duration("50"))]
            ),
            "deep6": Sequence("deep6", [StateAction("A", Duration("60"))]),
        }

        sequence = Sequence("a", [SequenceAction("deep1")])
        expected_animation = Animation(
            0,
            210,
            [
                frame(0, 60),
                frame(0, 50),
                frame(0, 40),
                frame(0, 30),
                frame(0, 20),
                frame(0, 10),
            ],
        )

        animation = generator.unweighted_sequence_to_animation(sequence, 0, texture_anim)
        assert animation == expected_animation

    def test_pass_duration_to_unweighted_sequence(self, texture_anim: TextureAnimation):
        sequence = Sequence("a", [SequenceAction("z", Duration("100"))])

        with pytest.raises(GeneratorError, match=".*duration.*"):
            generator.unweighted_sequence_to_animation(sequence, 0, texture_anim)


class Test_sequence_action_to_animation:
    def test_pass_duration_to_unweighted_sequence(self, texture_anim: TextureAnimation):
        texture_anim.sequences["a"] = Sequence("a", [])

        with pytest.raises(GeneratorError):
            generator.sequence_action_to_animation(
                SequenceAction("a", Duration("100")), 0, 100, texture_anim, {}
            )
