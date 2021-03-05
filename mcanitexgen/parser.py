from __future__ import annotations

import abc
import keyword
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from .utils import load_yaml_file


class ParserError(Exception):
    pass


def parse_animation_file(path: Path):
    return parse_animations(load_yaml_file(path))


def parse_animations(json: dict):
    animations = [TextureAnimation.from_json(texture, j) for texture, j in json.items()]
    return animations


@dataclass
class TextureAnimation:
    name: str
    texture: Path
    states: list[str]
    sequences: dict[str, Sequence]

    @classmethod
    def from_json(cls, texture_path: str, json: dict):
        if not "states" in json:
            raise ParserError(f"Animation '{texture_path}' does not define any states")
        states = json.pop("states")

        sequences = dict()
        for k, v in json.items():
            assert k.endswith("()")
            k = k.removesuffix("()")
            sequences[k] = Sequence.from_json(k, v)

        texture = Path(texture_path)
        return cls(texture.name.removesuffix(texture.suffix), texture, states, sequences)

    def __post_init__(self):
        if not "main" in self.sequences:
            raise ParserError(
                f"Animation for '{self.texture.name}' does not define a main sequence"
            )

        if not self.name.isidentifier() or keyword.iskeyword(self.name):
            raise ParserError(f"Invalid animation name: '{self.name}'")


@dataclass
class Sequence:
    name: str
    actions: list[Action]

    @classmethod
    def from_json(cls, name, json_actions: list[dict]):
        return cls(name, [Action.from_json(a) for a in json_actions])

    def __post_init__(self):
        self.total_weight = sum(self.weights())

    @property
    def is_weighted(self):
        return self.total_weight > 0

    def weights(self):
        """ Returns the weights of the weighted actions in this sequence """
        return map(lambda a: a.weight, filter(lambda a: a.has_weight, self.actions))


class Action(abc.ABC):
    def __init__(
        self,
        start: Union[str, int, None] = None,
        end: Union[str, int, None] = None,
        mark: Optional[str] = None,
        weight: int = 0,
        duration: Union[str, int, None] = None,
    ):
        if weight and (start or end or duration):
            raise ParserError(f"Actions defining a weight can't define start/end/duration")

        if end and duration:
            raise ParserError(f"Actions defining an end can't define a duration")

        self.start = start
        self.end = end
        self.mark = mark
        self.weight = weight
        self.duration = duration

    @classmethod
    def from_json(cls, json: Union[dict, str]):
        if isinstance(json, str):
            reference, args = json, {}
        else:
            reference, args = json.popitem()
            if not args:
                args = {}
        reference = reference.replace(" ", "")

        start = args["start"] if "start" in args else None
        end = args["end"] if "end" in args else None
        mark = args.get("mark")
        weight = int(args.get("weight", 0))
        duration = args["duration"] if "duration" in args else None

        if cls.is_sequence_ref(reference):
            reference, repeat = cls.parse_sequence_ref(reference)

            return SequenceAction(reference, repeat, start, end, mark, weight, duration)
        else:
            return StateAction(reference, start, end, mark, weight, duration)

    @classmethod
    def is_sequence_ref(cls, reference: str):
        return "()" in reference

    @classmethod
    def parse_sequence_ref(cls, reference: str):
        reference = reference.replace(" ", "").removesuffix("()")
        if "*" in reference:
            repeat, reference = reference.split("*")
        else:
            repeat = 1

        return (reference, int(repeat))

    @property
    def has_weight(self):
        return self.weight > 0


@dataclass(init=False)
class StateAction(Action):
    state: str
    start: Union[str, int, None]
    end: Union[str, int, None]
    mark: Optional[str]
    weight: int
    duration: Union[str, int, None]

    def __init__(
        self,
        state: str,
        start: Union[str, int, None] = None,
        end: Union[str, int, None] = None,
        mark: Optional[str] = None,
        weight: int = 0,
        duration: Union[str, int, None] = None,
    ):
        super().__init__(start, end, mark, weight, duration)
        self.state = state


@dataclass(init=False)
class SequenceAction(Action):
    ref: str
    repeat: int
    start: Union[str, int, None]
    end: Union[str, int, None]
    mark: Optional[str]
    weight: int
    duration: Union[str, int, None]

    def __init__(
        self,
        ref: str,
        repeat: int = 1,
        start: Union[str, int, None] = None,
        end: Union[str, int, None] = None,
        mark: Optional[str] = None,
        weight: int = 0,
        duration: Union[str, int, None] = None,
    ):
        super().__init__(start, end, mark, weight, duration)
        self.ref = ref
        self.repeat = repeat

        assert self.repeat >= 1
