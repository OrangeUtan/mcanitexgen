import pytest

from mcanitexgen.parser import Duration, ParserError, Sequence, SequenceAction


class Test_SequenceAction_init:
    @pytest.mark.parametrize(
        "args",
        [
            (Sequence(), Duration(1), 0),
            (Sequence(), Duration(1), -1),
        ],
    )
    def test_illegal_args(self, args):
        with pytest.raises(
            ParserError, match=f"Sequence cannot be repeated '{args[2]}' times"
        ):
            SequenceAction(*args)


class Test_SequenceAction_mul_and_rmul:
    @pytest.mark.parametrize("repeat", [1, 5, 7])
    def test(self, repeat):
        action_l = SequenceAction(Sequence(), Duration(1))
        action_r = SequenceAction(Sequence(), Duration(1))

        assert repeat * action_l == action_r * repeat
        assert isinstance(action_l, SequenceAction)
        assert action_l.repeat == repeat

    @pytest.mark.parametrize("repeat", [0, -1, -23423])
    def test_invalid_repeat(self, repeat):
        action = SequenceAction(Sequence(), Duration(1))

        with pytest.raises(ParserError, match=f"Sequence cannot be repeated '{repeat}' times"):
            repeat * action

        with pytest.raises(ParserError, match=f"Sequence cannot be repeated '{repeat}' times"):
            action * repeat

    @pytest.mark.parametrize("repeat", [None, "a string", "1", Sequence()])
    def test_repeat_with_invalid_type(self, repeat):
        action = SequenceAction(Sequence(), Duration(1))

        with pytest.raises(NotImplementedError):
            repeat * action

        with pytest.raises(NotImplementedError):
            action * repeat
