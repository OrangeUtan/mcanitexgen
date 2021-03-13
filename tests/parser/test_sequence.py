import pytest

from mcanitexgen.parser import (
    Duration,
    ParserError,
    Sequence,
    SequenceAction,
    State,
    StateAction,
    Timeframe,
    Weight,
)


class Test_init:
    @pytest.mark.parametrize(
        "actions, expected_total_weight, expected_is_weighted",
        [
            # No weighted
            ([StateAction(None, Duration(1))], 0, False),
            ([StateAction(None, Timeframe(0, 1, 1))], 0, False),
            ([SequenceAction(None, Duration(1))], 0, False),
            # Only weighted
            ([StateAction(None, Weight(1))], 1, True),
            ([StateAction(None, Weight(10))], 10, True),
            (
                [
                    StateAction(None, Weight(4)),
                    SequenceAction(None, Weight(1)),
                    StateAction(None, Weight(3)),
                ],
                8,
                True,
            ),
            # Mixed
            (
                [
                    StateAction(None, Weight(5)),
                    StateAction(None, Duration(1)),
                    StateAction(None, Weight(2)),
                ],
                7,
                True,
            ),
            (
                [
                    StateAction(None, Duration(1)),
                    SequenceAction(None, Duration(1)),
                    StateAction(None, Weight(4)),
                ],
                4,
                True,
            ),
        ],
    )
    def test_weight(self, actions, expected_total_weight, expected_is_weighted):
        sequence = Sequence(*actions)

        assert sequence.is_weighted == expected_is_weighted
        assert sequence.total_weight == expected_total_weight

    @pytest.mark.parametrize(
        "actions",
        [
            [Sequence(StateAction(None, Duration(1)))],
            [
                Sequence(StateAction(None, Duration(1))),
                StateAction(None, Weight(1)),
                Sequence(StateAction(None, Duration(1))),
                StateAction(None, Duration(1)),
            ],
        ],
    )
    def test_convert_sequences_to_sequence_actions(self, actions):
        sequence = Sequence(*actions)

        assert len(actions) == len(sequence.actions)
        for action, flattened_action in zip(actions, sequence.actions):
            if isinstance(action, Sequence):
                assert action != flattened_action
                assert isinstance(flattened_action, SequenceAction)
                assert flattened_action.sequence == action
            else:
                assert action == flattened_action

    @pytest.mark.parametrize(
        "actions, expected_constant_duration",
        [
            # Weight
            ([StateAction(None, Weight(1))], 0),
            ([SequenceAction(None, Weight(1))], 0),
            # States with constant duration
            ([StateAction(None, Duration(22))], 22),
            ([StateAction(None, Duration(22)), StateAction(None, Duration(12))], 34),
            ([StateAction(None, Weight(1)), StateAction(None, Duration(12))], 12),
            # Weighted sequence
            ([SequenceAction(Sequence(StateAction(None, Weight(1))), None)], 0),
            ([SequenceAction(Sequence(StateAction(None, Weight(1))), Duration(10))], 10),
            # Sequence with constant duration
            ([SequenceAction(Sequence(StateAction(None, Duration(11))), None)], 11),
        ],
    )
    def test_constant_duration(self, actions, expected_constant_duration):
        sequence = Sequence(*actions)
        assert sequence.constant_duration == expected_constant_duration


class Test_call:
    @pytest.mark.parametrize(
        "args, expected_action",
        [
            ({}, SequenceAction(Sequence())),
            ({"weight": 2}, SequenceAction(Sequence(), Weight(2))),
            ({"duration": 10}, SequenceAction(Sequence(), Duration(10))),
            ({"start": 2}, SequenceAction(Sequence(), Timeframe(start=2, end=3, duration=1))),
            ({"end": 2}, SequenceAction(Sequence(), Timeframe(end=2))),
            ({"mark": "test"}, SequenceAction(Sequence(), mark="test")),
            ({"repeat": 2}, SequenceAction(Sequence(), repeat=2)),
        ],
    )
    def test_create_sequence_action(self, args, expected_action):
        sequence = Sequence()
        assert sequence(**args) == expected_action


class Test_mul_and_rmul:
    @pytest.mark.parametrize("repeat", [1, 5, 7])
    def test_create_repeated_sequence_action(self, repeat):
        sequence = Sequence(StateAction(State(0), Duration(1)))

        action = repeat * sequence
        assert repeat * sequence == sequence * repeat
        assert isinstance(action, SequenceAction)
        assert action.repeat == repeat

    @pytest.mark.parametrize("repeat", [0, -1, -23423])
    def test_invalid_repeat(self, repeat):
        sequence = Sequence(StateAction(State(0), Duration(1)))

        with pytest.raises(ParserError, match=f"Sequence cannot be repeated '{repeat}' times"):
            repeat * sequence

        with pytest.raises(ParserError, match=f"Sequence cannot be repeated '{repeat}' times"):
            sequence * repeat

    @pytest.mark.parametrize("repeat", [None, "a string", "1", Sequence()])
    def test_repeat_with_invalid_type(self, repeat):
        sequence = Sequence(StateAction(State(0), Duration(1)))

        with pytest.raises(NotImplementedError):
            repeat * sequence

        with pytest.raises(NotImplementedError):
            sequence * repeat
