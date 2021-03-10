from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Type

from mcanitexgen import utils

from .parser import Action, Duration, Sequence, SequenceAction, Timeframe


class GeneratorError(Exception):
    pass


def animation(texture: Path, root_sequence: str = "root"):
    def wrapper(cls: Type[TextureAnimation]):
        cls.sequences = {}
        for name, sequence in filter(
            lambda i: isinstance(i[1], Sequence), cls.__dict__.items()
        ):
            cls.sequences[name] = sequence
            sequence.name = name

        cls.texture = texture
        cls.root = cls.sequences[root_sequence]

        animation = unweighted_sequence_to_animation(cls.root, 0)
        cls.start = animation.start
        cls.end = animation.end
        cls.frames = animation.frames
        cls.marks = animation.marks

        return cls

    return wrapper


class TextureAnimation:
    texture: Path
    sequences: list[Sequence]
    root: Sequence

    start: int
    end: int
    frames: list[dict]
    marks: dict[str, Mark]


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
        self.marks |= other.marks

    def add_frame(self, index: int, start: int, end: int):
        if end - start <= 0:
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
        if action.is_weighted:
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


def get_unweighted_action_timeframe(action: Action, action_start: int):
    if isinstance(action.time, Duration):
        action_duration = int(action.time)
    elif isinstance(action.time, Timeframe):
        start, end, duration = action.time.start, action.time.end, action.time.duration
        if start and end and duration:
            action_start = start
            action_duration = duration
        elif not start and end and not duration:
            action_duration = end - action_start
        else:
            raise GeneratorError(
                f"Unexpected combination of start, end, duration: '{start}', '{end}', '{duration}'"
            )
    else:
        action_duration = None

    return (action_start, action_duration)


def append_action_to_animation(
    action: Action, start: int, duration: Optional[int], anim: Animation
):
    if isinstance(action, SequenceAction):
        anim.append(sequence_action_to_animation(action, start, duration))
    else:
        assert duration is not None
        anim.add_frame(action.index, start, start + duration)

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
