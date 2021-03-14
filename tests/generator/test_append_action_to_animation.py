import pytest

from mcanitexgen import generator
from mcanitexgen.generator import Animation
from mcanitexgen.parser import Action, Duration, StateAction


class InvalidCustomAction(Action):
    pass


@pytest.mark.parametrize("action", [None, InvalidCustomAction(Duration(10))])
def test_unknown_action_type(action):
    with pytest.raises(TypeError, match="Unknown Action type.*"):
        generator.append_action_to_animation(action, 0, 0, None)
