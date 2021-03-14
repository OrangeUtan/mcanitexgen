from __future__ import annotations

import importlib
import importlib.util
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Iterator, Optional, Type, Union

from mcanitexgen import utils

from .parser import (
    Action,
    Duration,
    Sequence,
    SequenceAction,
    State,
    StateAction,
    Timeframe,
    Weight,
)


class GeneratorError(Exception):
    pass


def load_animations_from_file(path: Path):
    spec = importlib.util.spec_from_file_location(path.name, path)
    if spec is None or spec.loader is None:
        raise GeneratorError(f"Couldn't load animations from '{path}'")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore

    return get_texture_animations_from_module(module)


def get_texture_animations_from_module(module: ModuleType):
    return {
        k: v
        for k, v in module.__dict__.items()
        if isinstance(v, type) and issubclass(v, TextureAnimation) and v != TextureAnimation
    }


def animation(
    texture: Union[str, Path], main_sequence: str = "main", interpolate=False, frametime=1
):
    def wrapper(cls: Type[TextureAnimation]):
        cls.sequences = {}
        cls.states = {}
        for name, val in cls.__dict__.items():
            if isinstance(val, State):
                cls.states[val.index] = val
            elif isinstance(val, Sequence):
                val.name = name
                cls.sequences[name] = val
        cls.root = cls.sequences[main_sequence]

        cls.texture = texture if isinstance(texture, Path) else Path(texture)
        cls.interpolate = interpolate
        cls.frametime = frametime

        cls.animation = unweighted_sequence_to_animation(cls.root, 0)
        return cls

    return wrapper


class TextureAnimationMeta(type):
    @property
    def start(self):
        return self.animation.start

    @property
    def end(self):
        return self.animation.end

    @property
    def frames(self):
        return self.animation.frames

    @property
    def marks(self):
        return self.animation.marks


class TextureAnimation(metaclass=TextureAnimationMeta):
    texture: Path
    interpolate: bool
    frametime: int

    sequences: dict[str, Sequence]
    states: dict[int, State]
    root: Sequence

    animation: Animation

    @classmethod
    def combine_consecutive_frames(cls, frames: Iterator[dict]):
        prev_frame = None
        for frame in frames:
            if prev_frame:
                if prev_frame["index"] == frame["index"]:
                    prev_frame["time"] += frame["time"]
                else:
                    yield prev_frame
                    prev_frame = frame.copy()
            else:
                prev_frame = frame.copy()

        if prev_frame:
            yield prev_frame

    @classmethod
    def to_mcmeta(cls):
        return {
            "animation": {
                "interpolate": cls.interpolate,
                "frametime": cls.frametime,
                "frames": list(cls.combine_consecutive_frames(cls.animation.frames)),
            }
        }


@dataclass
class Animation:
    start: int
    end: int
    frames: list[dict] = field(default_factory=list)
    marks: dict[str, Mark] = field(default_factory=dict)

    def append(self, other: Animation):
        # Fill time gap between animations
        time_gap = other.start - self.end
        if time_gap > 0 and self.frames:
            self.frames[-1]["time"] += time_gap
        elif time_gap < 0:
            raise GeneratorError(
                f"Can't append to animation that starts before the other ends"
            )

        self.end = other.end
        self.frames += other.frames
        self.marks.update(other.marks)

    def add_frame(self, index: int, start: int, end: int):
        if start < 0 or end < 0 or end - start <= 0:
            raise GeneratorError(f"Illegal start and end for frame: '{start}' '{end}'")

        if len(self.frames) == 0:
            # Animation starts at start of first frame
            self.start = start
        elif start - self.end > 0:
            # Extend time of the last frame to fill the gap to the new frame
            self.frames[-1]["time"] += start - self.end

        self.end = end
        self.frames.append({"index": index, "time": end - start})


@dataclass
class Mark:
    start: int
    end: int


def unweighted_sequence_to_animation(sequence: Sequence, start: int):
    assert not sequence.is_weighted
    animation = Animation(start, start)

    for action in sequence.actions:
        action_start, action_duration = get_unweighted_action_timeframe(action, animation.end)
        append_action_to_animation(action, action_start, action_duration, animation)

    return animation


def weighted_sequence_to_animation(sequence: Sequence, start: int, duration: int):
    assert sequence.is_weighted
    animation = Animation(start, start)

    distributable_duration = duration - sequence.constant_duration

    if distributable_duration <= 0:
        raise GeneratorError(
            f"Duration '{duration}' is not enough for the weighted sequence '{sequence.name}' with constant duration '{sequence.constant_duration}'"
        )

    duration_distributor = utils.DurationDistributor(
        distributable_duration, sequence.total_weight
    )

    for action in sequence.actions:
        if isinstance(action.time, Weight):
            action_start = animation.end
            action_duration = duration_distributor.take(int(action.time))
        else:
            action_start, action_duration = get_unweighted_action_timeframe(
                action, animation.end
            )

        append_action_to_animation(action, action_start, action_duration, animation)

    if not duration_distributor.is_empty():
        raise GeneratorError(f"Couldn't distribute duration over weights")

    return animation


def get_unweighted_action_timeframe(
    action: Action, action_start: int
) -> tuple[int, Optional[int]]:
    if isinstance(action.time, Duration):
        return (action_start, int(action.time))
    elif isinstance(action.time, Timeframe):
        start, end, duration = action.time.start, action.time.end, action.time.duration
        if start and end and duration:
            action_start = start
            return (action_start, duration)
        elif not start and end and not duration:
            return (action_start, end - action_start)
        else:
            raise GeneratorError(
                f"Unexpected combination of start, end, duration: '{start}', '{end}', '{duration}'"
            )
    else:
        return (action_start, None)


def append_action_to_animation(
    action: Action, start: int, duration: Optional[int], anim: Animation
):
    if isinstance(action, SequenceAction):
        anim.append(sequence_action_to_animation(action, start, duration))
    elif isinstance(action, StateAction):
        assert duration is not None
        anim.add_frame(action.state.index, start, start + duration)
    else:
        raise TypeError(f"Unknown Action type: {action}")

    # Add mark
    if action.mark:
        anim.marks[action.mark] = Mark(start, anim.end)


def sequence_action_to_animation(action: SequenceAction, start: int, duration: Optional[int]):
    anim = Animation(start, start)

    if action.sequence.is_weighted:
        if not duration:
            raise GeneratorError(
                f"Didn't pass duration to weighted sequence '{action.sequence.name}'"
            )

        if action.is_weighted:
            duration_distributor = utils.DurationDistributor(duration, action.repeat)
            for _ in range(action.repeat):
                anim.append(
                    weighted_sequence_to_animation(
                        action.sequence, anim.end, duration_distributor.take(1)
                    )
                )

            if not duration_distributor.is_empty():
                raise GeneratorError(f"Couldn't distribute duration over weights")
        else:
            for _ in range(action.repeat):
                anim.append(
                    weighted_sequence_to_animation(action.sequence, anim.end, duration)
                )
    else:
        if duration:
            raise GeneratorError(
                f"Passing duration to unweighted sequence '{action.sequence.name}'"
            )

        for _ in range(action.repeat):
            anim.append(unweighted_sequence_to_animation(action.sequence, anim.end))

    return anim
