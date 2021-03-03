import pytest
import ruamel.yaml as yaml

from mcanitexgen import parser
from mcanitexgen.TextureAnimationOld import Sequence


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
        reference, repeat = parser.Action.parse_sequence_ref(ref)
        assert reference == expected_ref
        assert repeat == expected_repeat


class Test_FromJson:
    @pytest.fixture
    def dummy_sequences(self):
        return {"pop": Sequence("pop", [], 0), "b": Sequence("b", [], 0)}

    @pytest.mark.parametrize(
        "string,expected",
        [
            ("A_STATE", parser.StateAction("A_STATE")),
            ("A_STATE:", parser.StateAction("A_STATE")),
            ("pop()", parser.SequenceAction(Sequence("pop", [], 0))),
            ("pop():", parser.SequenceAction(Sequence("pop", [], 0))),
            ("3 * pop()", parser.SequenceAction(Sequence("pop", [], 0), 3)),
            ("3 * pop():", parser.SequenceAction(Sequence("pop", [], 0), 3)),
            ("b()", parser.SequenceAction(Sequence("b", [], 0), 1)),
            ("  b  (  )  ", parser.SequenceAction(Sequence("b", [], 0), 1)),
        ],
    )
    def test_no_args(self, string, expected, dummy_sequences):
        json = yaml.safe_load(string)
        action = parser.Action.from_json(json, dummy_sequences)
        assert type(action) == type(expected)
        assert action == expected

    @pytest.mark.parametrize(
        "string,expected",
        [
            ("a: {duration : 10}", parser.StateAction("a", duration=10)),
            (" abc  : {duration: 10}", parser.StateAction("abc", duration=10)),
            ("b(): {end: 10}", parser.SequenceAction(Sequence("b", [], 0), end=10)),
        ],
    )
    def test_with_args(self, string, expected, dummy_sequences):
        json = yaml.safe_load(string)
        action = parser.Action.from_json(json, dummy_sequences)
        assert type(action) == type(expected)
        assert action == expected


class Test_Init:
    @pytest.mark.parametrize(
        "start,end,duration,weight",
        [
            # Weight + any other
            (1, None, None, 5),
            (None, 2, None, 5),
            (None, None, 3, 5),
            (2, None, 3, 5),
            # End + duration
            (None, 4, 2, None),
            (1, 2, 2, None),
        ],
    )
    def test_invalid_arg_combinations(self, start, end, duration, weight):
        with pytest.raises(parser.ParserError, match="Actions.*can't define.*"):
            parser.Action(start, end, None, weight, duration)

    @pytest.mark.parametrize(
        "start,end,duration,weight",
        [
            (2, 5, None, None),  # Start and end
            (2, None, 5, None),  # Start and duration
            (None, None, None, 10),  # Only weight
        ],
    )
    def test_valid_arg_combinations(self, start, end, duration, weight):
        parser.Action(start, end, None, weight, duration)
