import pytest
import ruamel.yaml as yaml

from mcanitexgen.parser import Sequence, StateAction


class Test_FromJson:
    @pytest.mark.parametrize(
        "string,expected",
        [
            (
                "[A, B, C]",
                Sequence("abc", [StateAction("A"), StateAction("B"), StateAction("C")]),
            ),
            (
                "[ABC: , B, CDEF: ]",
                Sequence("abc", [StateAction("ABC"), StateAction("B"), StateAction("CDEF")]),
            ),
        ],
    )
    def test(self, string, expected):
        json = yaml.safe_load(string)
        seq = Sequence.from_json("abc", json, {})

        assert len(seq.actions) == len(expected.actions)
        for action, expected_action in zip(seq.actions, expected.actions):
            assert action == expected_action
