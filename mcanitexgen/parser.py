from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Optional, Union


class ParserError(Exception):
    pass


@dataclass(init=False)
class State:
    index: int = None
    name: str = None

    def __call__(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        duration: Optional[int] = None,
        weight: Optional[int] = None,
        mark: Optional[str] = None,
    ):
        time = Time.from_args(start, end, duration, weight)
        return StateAction(self, time, mark)


@dataclass(init=False)
class Sequence:
    actions: list[Action]
    name: Optional[str]

    def __init__(self, *actions: Union[Action, Sequence]):
        self.actions = []
        for entry in actions:
            if isinstance(entry, Action):
                self.actions.append(entry)
            elif isinstance(entry, Sequence):
                self.actions.append(entry())

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

    def __call__(
        self,
        repeat=1,
        start: Optional[int] = None,
        end: Optional[int] = None,
        duration: Optional[int] = None,
        weight: Optional[int] = None,
        mark: Optional[str] = None,
    ):
        time = Time.from_args(start, end, duration, weight)
        return SequenceAction(self, time, repeat, mark)

    def __mul__(self, other):
        if isinstance(other, int):
            return self(repeat=other)
        else:
            raise NotImplementedError()

    def __rmul__(self, other):
        if isinstance(other, int):
            return self(repeat=other)
        else:
            raise NotImplementedError()


class Time:
    def from_args(
        start: Optional[int] = None,
        end: Optional[int] = None,
        duration: Optional[int] = None,
        weight: Optional[int] = None,
    ):
        if weight:
            return Weight(weight)
        elif start or end:
            return Timeframe(start, end, duration)
        elif duration:
            return Duration(duration)
        elif not start and not end and not duration and not weight:
            return None
        else:
            raise ParserError(
                f"Illegal combination of start, end, duration and weight: {start}, {end}, {duration}, {weight}"
            )


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
    state: State
    time: Time
    mark: Optional[str] = None

    def __init__(self, state: State, time: Optional[Time], mark: Optional[str]):
        super().__init__(time, mark)
        self.state = state


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
