import pytest

from mcanitexgen.parser import Duration, ParserError, Time, Timeframe, Weight


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


class Test_Time_from_args:
    @pytest.mark.parametrize(
        "start, end, duration, weight, expected_time",
        [
            (None, None, None, None, None),
            # Weight
            (None, None, None, 12, Weight(12)),
            # Duration
            (None, None, 10, None, Duration(10)),
            # Timeframe
            (0, None, None, None, Timeframe(0, 1, 1)),
            (1, 20, None, None, Timeframe(1, 20, 19)),
            (1, 20, 19, None, Timeframe(1, 20, 19)),
            (1, None, 19, None, Timeframe(1, 20, 19)),
            (None, 10, None, None, Timeframe(None, 10, None)),
        ],
    )
    def test_args(self, start, end, duration, weight, expected_time):
        assert Time.from_args(start, end, duration, weight) == expected_time

    @pytest.mark.parametrize(
        "start, end, duration, weight, match",
        [
            # Weight
            (None, None, None, 0, "Weight of time must be at least 1"),
            (None, None, 1, 1, "Weighted time can't have start, end or duration"),
            (None, 1, None, 1, "Weighted time can't have start, end or duration"),
            (1, None, None, 1, "Weighted time can't have start, end or duration"),
            # Duration
            (None, None, 0, None, "Duration must be at least 1"),
            (None, None, -10, None, "Duration must be at least 1"),
        ],
    )
    def test_illegal_args(self, start, end, duration, weight, match):
        with pytest.raises(ParserError, match=match):
            Time.from_args(start, end, duration, weight)
