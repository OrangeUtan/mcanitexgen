import pytest
import ruamel.yaml as yaml

from mcanitexgen import parser
from mcanitexgen.parser import (
    Action,
    Duration,
    ParserError,
    SequenceAction,
    StateAction,
    Timeframe,
)


class Test_ParseSequenceRef:
    @pytest.mark.parametrize(
        "ref, expected_repeat, expected_ref",
        [
            ("a()", 1, "a"),
            ("1*abc()", 1, "abc"),
            ("7   *   b()", 7, "b"),
            ("7 2  *   b()", 72, "b"),
        ],
    )
    def test_parse_repeat(self, ref, expected_repeat, expected_ref):
        reference, repeat = parser.Action._parse_sequence_ref(ref)
        assert reference == expected_ref
        assert repeat == expected_repeat


class Test_FromJson:
    @pytest.mark.parametrize(
        "string,expected",
        [
            ("A_STATE", StateAction("A_STATE")),
            ("A_STATE:", StateAction("A_STATE")),
            ("pop()", SequenceAction("pop")),
            ("pop():", SequenceAction("pop")),
            ("3 * pop()", SequenceAction("pop", repeat=3)),
            ("3 * pop():", SequenceAction("pop", repeat=3)),
            ("b()", SequenceAction("b", repeat=1)),
            ("  b  (  )  ", SequenceAction("b", repeat=1)),
        ],
    )
    def test_no_args(self, string, expected):
        json = yaml.safe_load(string)
        action = parser.Action.from_json(json)
        assert type(action) == type(expected)
        assert action == expected

    @pytest.mark.parametrize(
        "string,expected",
        [
            ("a: {duration : 10}", StateAction("a", Duration("10"))),
            (" abc  : {duration: 10}", StateAction("abc", Duration("10"))),
            ("b(): {end: 10}", SequenceAction("b", Timeframe(end="10"))),
        ],
    )
    def test_with_args(self, string, expected):
        json = yaml.safe_load(string)
        action = parser.Action.from_json(json)
        assert type(action) == type(expected)
        assert action == expected

    def test_forget_space_after_colon_in_args(self):
        json = yaml.safe_load("a: {duration:100}")
        # -> parses to {'duration:100': None} instead of {duration: 100}

        with pytest.raises(parser.ParserError, match=".*action arguments.*"):
            parser.Action.from_json(json)


class Test_FromJson_Time:
    @pytest.mark.parametrize(
        "action_json, expected_time",
        [
            # Duration
            ("a", Duration(1)),
            ("a: {duration: 1}", Duration("1")),
            ("a: {duration: 2342}", Duration("2342")),
            ("a: {duration: 'abc'}", Duration("abc")),
            # Start
            ("a: {start: 1}", Timeframe(start="1", duration="1")),
            ("a: {start: 5, duration: 10}", Timeframe(start="5", duration="10")),
            # End
            ("a: {end: 1}", Timeframe(end="1")),
            ("a: {start: 1, end: 20}", Timeframe(start="1", end="20")),
        ],
    )
    def test_allowed_combinations(self, action_json, expected_time):
        json = yaml.safe_load(action_json)
        action = parser.Action.from_json(json)

        assert action.time == expected_time

    @pytest.mark.parametrize(
        "action_json",
        [
            "a: {end: 10, duration: 10}",
            "a: {weight: 1, duration: 10}",
            "a: {weight: 1, start: 1}",
            "a: {weight: 1, end: 1}",
        ],
    )
    def test_forbidden_combinations(self, action_json):
        json = yaml.safe_load(action_json)

        with pytest.raises(ParserError):
            Action.from_json(json)
