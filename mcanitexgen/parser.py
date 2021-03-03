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
        self._total_actions_weight = sum(map(lambda a: a.weight, self.actions))

    @property
    def is_weighted(self):
        return self._total_actions_weight > 0

    def __len__(self):
        return len(self.actions)

    def __contains__(self, o: object):
        return o in self.actions

    def __iter__(self):
        return iter(self.actions)


class Action(abc.ABC):
    def __init__(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        mark: Optional[str] = None,
        weight: int = 0,
        duration: Optional[int] = None,
    ):
        self.start = start
        self.end = end
        self.mark = mark
        self.weight = weight
        self.duration = duration

        if self.weight and (self.start or self.end or self.duration):
            raise ParserError(f"Actions defining a weight can't define start/end/duration")

        if self.end and self.duration:
            raise ParserError(f"Actions defining an end can't define a duration")

    @classmethod
    def from_json(cls, json: Union[dict, str]):
        if isinstance(json, str):
            reference, args = json, {}
        else:
            reference, args = json.popitem()
            if not args:
                args = {}
        reference = reference.replace(" ", "")

        start = int(args["start"]) if "start" in args else None
        end = int(args["end"]) if "end" in args else None
        mark = args.get("mark")
        weight = int(args.get("weight", 0))
        duration = int(args["duration"]) if "duration" in args else None

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
    ref: str
    start: Optional[int]
    end: Optional[int]
    mark: Optional[str]
    weight: int
    duration: Optional[int]

    def __init__(
        self,
        ref: str,
        start: Optional[int] = None,
        end: Optional[int] = None,
        mark: Optional[str] = None,
        weight: int = 0,
        duration: Optional[int] = None,
    ):
        super().__init__(start, end, mark, weight, duration)
        self.ref = ref


@dataclass(init=False)
class SequenceAction(Action):
    ref: str
    repeat: int
    start: Optional[int]
    end: Optional[int]
    mark: Optional[str]
    weight: int
    duration: Optional[int]

    def __init__(
        self,
        ref: str,
        repeat: int = 1,
        start: Optional[int] = None,
        end: Optional[int] = None,
        mark: Optional[str] = None,
        weight: int = 0,
        duration: Optional[int] = None,
    ):
        super().__init__(start, end, mark, weight, duration)
        self.ref = ref
        self.repeat = repeat

        assert self.repeat >= 1
