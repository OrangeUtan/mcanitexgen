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
    animations = {}
    for texture, anim_json in json.items():
        ta = TextureAnimation.from_json(texture, anim_json)
        animations[ta.name] = ta

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

        if self.name != "main":
            for action in self.actions:
                if isinstance(action.time, Timeframe):
                    raise ParserError(
                        f"Illegal action '{action}' in sequence '{self.name}'. Only 'main' sequence can contain actions with timeframes."
                    )

    @property
    def is_weighted(self):
        return self.total_weight > 0

    def weights(self):
        """ Returns the weights of the weighted actions in this sequence """
        return map(lambda a: a.time, filter(lambda a: a.is_weighted, self.actions))


class Time(abc.ABC):
    pass


class Weight(int, Time):
    pass


class Duration(str, Time):
    pass


@dataclass
class Timeframe(Time):
    start: Optional[str] = None
    end: Optional[str] = None
    duration: Optional[str] = None

    def __post_init__(self):
        if self.start is None and self.end is None and self.duration is None:
            raise ParserError(f"At least one of start/end/duration must not be None")
        elif self.end and self.duration:
            raise ParserError(f"Actions defining an end can't define a duration")
        elif self.start and self.duration is None and self.end is None:
            self.duration = "1"


class Action(abc.ABC):
    def __init__(self, time: Optional[Time], mark: Optional[str] = None):
        self.time = time
        self.mark = mark

    @classmethod
    def from_json(cls, json: Union[dict, str]):
        ref, args = cls._get_ref_and_duration_from_json(json)

        mark = args.pop("mark") if "mark" in args else None
        weight = args.pop("weight") if "weight" in args else None
        start = str(args.pop("start")) if "start" in args else None
        end = str(args.pop("end")) if "end" in args else None
        duration = str(args.pop("duration")) if "duration" in args else None

        if weight:
            if start or end or duration:
                raise ParserError(f"Weighted actions can't define start/end/duration")
            time = Weight(int(weight))
        elif start or end:
            time = Timeframe(start, end, duration)
        elif duration:
            time = Duration(duration)
        else:
            time = None

        if len(args):
            raise ParserError(f"Unknown action arguments: '{args}'")

        if cls._is_sequence_ref(ref):
            sequence_ref, repeat = cls._parse_sequence_ref(ref)
            return SequenceAction(sequence_ref, time, repeat, mark)
        else:
            return StateAction(ref, time or Duration("1"), mark)

    @property
    def is_weighted(self):
        return isinstance(self.time, Weight)

    @classmethod
    def _is_sequence_ref(cls, reference: str):
        return "()" in reference

    @classmethod
    def _get_ref_and_duration_from_json(cls, json: Union[dict, str]):
        if isinstance(json, str):
            reference, duration = json, {}
        elif isinstance(json, dict):
            reference, duration = json.popitem()
            if not duration:
                duration = {}
        else:
            raise ParserError(f"'{json}' is not a valid action. Must either be str or dict")

        return (reference.replace(" ", ""), duration)

    @classmethod
    def _parse_sequence_ref(cls, reference: str):
        reference = reference.replace(" ", "").removesuffix("()")
        if "*" in reference:
            repeat, reference = reference.split("*")
        else:
            repeat = 1

        return (reference, int(repeat))


@dataclass(init=False)
class SequenceAction(Action):
    sequence_ref: str
    repeat: int
    time: Optional[Time]
    mark: Optional[str]

    def __init__(
        self,
        seq_ref: str,
        time: Optional[Time] = None,
        repeat: int = 1,
        mark: Optional[str] = None,
    ):
        super().__init__(time, mark)

        self.sequence_ref = seq_ref
        self.repeat = repeat

        assert self.repeat >= 1


@dataclass(init=False)
class StateAction(Action):
    state_ref: str
    time: Time
    mark: Optional[str]

    def __init__(
        self,
        state_ref: str,
        time: Time = Duration("1"),
        mark: Optional[str] = None,
    ):
        super().__init__(time, mark)
        self.state_ref = state_ref
