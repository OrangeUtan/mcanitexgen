import pytest

from mcanitexgen.parser import ParserError, State, Time, Timeframe


class Test_Timeframe_init:
    @pytest.mark.parametrize(
        "start, end, duration, expected_timeframe",
        [
            # Deduce end and duration
            (0, None, None, Timeframe(0, 1, 1)),
            (10, None, None, Timeframe(10, 11, 1)),
            # Deduce duration
            (0, 20, None, Timeframe(0, 20, 20)),
            (11, 22, None, Timeframe(11, 22, 11)),
            # Deduce end
            (0, None, 5, Timeframe(0, 5, 5)),
            (15, None, 5, Timeframe(15, 20, 5)),
            # All set
            (0, 10, 10, Timeframe(0, 10, 10)),
        ],
    )
    def test_args(self, start, end, duration, expected_timeframe):
        assert Timeframe(start, end, duration) == expected_timeframe

    @pytest.mark.parametrize(
        "start, end, duration, match",
        [
            (None, None, None, "Timeframe must have at least one of start, end, duration set"),
            (None, 2, 20, "Timeframes without start can't have end and duration"),
            (0, 5, 20, "Start, end and duration of timeframe don't match: 0, 5, 20"),
        ],
    )
    def test_illegal_args(self, start, end, duration, match):
        with pytest.raises(ParserError, match=match):
            Timeframe(start, end, duration)
