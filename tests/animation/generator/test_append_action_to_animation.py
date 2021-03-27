import pytest

from mcanitexgen.animation import generator
from mcanitexgen.animation.parser import Action, Duration


class InvalidCustomAction(Action):
    pass


@pytest.mark.parametrize("action", [None, InvalidCustomAction(Duration(10))])
def test_unknown_action_type(action):
    with pytest.raises(TypeError, match="Unknown Action type.*"):
        generator.append_action_to_animation(action, 0, 0, None)
