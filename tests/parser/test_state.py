import pytest

from mcanitexgen.parser import Duration, State, StateAction, Timeframe, Weight


class Test_call:
    @pytest.mark.parametrize(
        "args, expected_action",
        [
            ({}, StateAction(State(0), Duration(1))),
            ({"weight": 2}, StateAction(State(0), Weight(2))),
            ({"duration": 10}, StateAction(State(0), Duration(10))),
            ({"start": 2}, StateAction(State(0), Timeframe(start=2, end=3, duration=1))),
            ({"end": 2}, StateAction(State(0), Timeframe(end=2))),
            ({"mark": "test"}, StateAction(State(0), Duration(1), mark="test")),
        ],
    )
    def test_create_state_action(self, args, expected_action):
        state = State(0)
        assert state(**args) == expected_action
