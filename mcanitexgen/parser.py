from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Optional


class ParserError(Exception):
    pass


@dataclass(init=False)
class Sequence:
    actions: list[Action]
    name: Optional[str]

    def __init__(self, *actions: Action):
        self.actions = []
        for entry in actions:
            if isinstance(entry, Action):
                self.actions.append(entry)
            else:
                self.actions += entry

        self.total_weight = sum(map(lambda a: int(a.time), self.weighted_actions()))
        self.is_weighted = self.total_weight > 0

        self.constant_duration = 0
        for action in self.actions:
            if isinstance(action.time, Duration):
                self.constant_duration += action.time
            elif not action.is_weighted and isinstance(action, SequenceAction):
                self.constant_duration += action.sequence.constant_duration

    def weighted_actions(self):
        return filter(lambda a: a.is_weighted, self.actions)


class Time:
    pass


class Duration(int, Time):
    pass


class Weight(int, Time):
    pass


@dataclass
class Timeframe(Time):
    start: Optional[int] = None
    end: Optional[int] = None
    duration: Optional[int] = None

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

    @property
    def is_weighted(self):
        return isinstance(self.time, Weight)


@dataclass(init=False)
class StateAction(Action):
    index: int
    time: Time
    mark: Optional[str] = None

    def __init__(self, index: int, time: Optional[Time], mark: Optional[str]):
        super().__init__(time, mark)
        self.index = index


@dataclass(init=False)
class SequenceAction(Action):
    sequence: Sequence
    time: Optional[Time]
    repeat: int
    mark: Optional[str]

    def __init__(
        self,
        sequence: Sequence,
        time: Optional[Time] = None,
        repeat=1,
        mark: Optional[str] = None,
    ):
        super().__init__(time, mark)
        self.sequence = sequence
        self.repeat = repeat

    def __mul__(self, other):
        if isinstance(other, int):
            self.repeat = other
        else:
            raise NotImplementedError()
        return self

    def __rmul__(self, other):
        if isinstance(other, int):
            self.repeat = other
        else:
            raise NotImplementedError()
        return self


def state(index: int, time: Time, mark: Optional[str] = None):
    return StateAction(index, time, mark)


def sequence(
    sequence: Sequence, time: Optional[Time] = None, repeat=1, mark: Optional[str] = None
):
    return SequenceAction(sequence, time, repeat, mark)
