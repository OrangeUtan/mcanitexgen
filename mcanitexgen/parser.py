from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Optional, Union


class ParserError(Exception):
    pass


@dataclass(init=False)
class State:
    index: int

    def __init__(self, index):
        self.index = index

    def __call__(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        duration: Optional[int] = None,
        weight: Optional[int] = None,
        mark: Optional[str] = None,
    ):
        time = Time.from_args(start, end, duration, weight)
        if time is None:
            time = Duration(1)

        return StateAction(self, time, mark)


@dataclass(init=False)
class Sequence:
    actions: list[Action]
    name: Optional[str] = None

    def __init__(self, *actions: Union[Action, Sequence]):
        self.actions = list(
            map(
                lambda a: a() if (isinstance(a, Sequence) or isinstance(a, State)) else a,
                actions,
            )
        )

        self.total_weight = sum(map(lambda a: int(a.time), self.weighted_actions()))
        self.is_weighted = self.total_weight > 0

        self.constant_duration = sum(map(lambda a: a.constant_duration(), self.actions))

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
        return self.__mul__(other)


class Time:
    @staticmethod
    def from_args(
        start: Optional[int] = None,
        end: Optional[int] = None,
        duration: Optional[int] = None,
        weight: Optional[int] = None,
    ):
        if weight is not None:
            if weight <= 0:
                raise ParserError(f"Weight of time must be at least 1")
            if start or end or duration:
                raise ParserError(f"Weighted time can't have start, end or duration")
            return Weight(weight)
        elif start is not None or end is not None:
            return Timeframe(start, end, duration)
        elif duration is not None:
            if duration <= 0:
                raise ParserError(f"Duration must be at least 1")
            return Duration(duration)
        else:
            return None


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
        # Check for illegal inputs
        if self.start is None and self.end is None and self.duration is None:
            raise ParserError(f"Timeframe must have at least one of start, end, duration set")
        elif self.start is None and self.end != None and self.duration != None:
            raise ParserError(f"Timeframes without start can't have end and duration")

        if self.start != None:
            # Make sure start, end and duration are set
            if self.end is None or self.duration is None:
                self._deduce_unset_attributes()

            if self.end - self.start != self.duration:
                raise ParserError(
                    f"Start, end and duration of timeframe don't match: {self.start}, {self.end}, {self.duration}"
                )

    def _deduce_unset_attributes(self):
        if self.start != None:
            if self.end != None:
                self.duration = self.end - self.start
            elif self.duration != None:
                self.end = self.start + self.duration
            else:
                self.end = self.start + 1
                self.duration = 1


class Action(abc.ABC):
    def __init__(self, time: Optional[Time], mark: Optional[str] = None):
        self.time = time
        self.mark = mark

    @property
    def is_weighted(self):
        return isinstance(self.time, Weight)

    def constant_duration(self):
        if isinstance(self.time, Duration):
            return self.time
        elif isinstance(self, SequenceAction) and not self.is_weighted:
            return self.sequence.constant_duration
        else:
            return 0


@dataclass(init=False)
class StateAction(Action):
    state: State
    time: Time
    mark: Optional[str] = None

    def __init__(self, state: State, time: Time, mark: Optional[str] = None):
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

        if self.repeat <= 0:
            raise ParserError(f"Sequence cannot be repeated '{self.repeat}' times")

    def __mul__(self, other):
        if isinstance(other, int):
            if other <= 0:
                raise ParserError(f"Sequence cannot be repeated '{other}' times")

            self.repeat = other
        else:
            raise NotImplementedError()
        return self

    def __rmul__(self, other):
        return self.__mul__(other)
