from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, Optional, Union

from mcanitexgen import utils
from mcanitexgen.expressions import evaluate_int
from mcanitexgen.parser import (
    Action,
    Duration,
    ParserError,
    Sequence,
    SequenceAction,
    StateAction,
    TextureAnimation,
    Timeframe,
    Weight,
)


class GeneratorError(Exception):
    pass


@dataclass
class Mark:
    start: int
    end: int


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

    def mark(self, name: str):
        return self.marks[name]


def create_animation(texture_anim: TextureAnimation, expr_locals=dict()):
    return unweighted_sequence_to_animation(
        texture_anim.sequences["main"], 0, texture_anim, expr_locals
    )


def unweighted_sequence_to_animation(
    sequence: Sequence, start: int, texture_anim: TextureAnimation, expr_locals={}
):
    assert not sequence.is_weighted
    animation = Animation(start, start)

    for action in sequence.actions:
        action_start, action_duration = get_unweighted_action_timeframe(
            action, animation.end, expr_locals
        )
        append_action_to_animation(
            action, action_start, action_duration, animation, texture_anim, expr_locals
        )

    return animation


def weighted_sequence_to_animation(
    sequence: Sequence,
    start: int,
    duration: int,
    texture_anim: TextureAnimation,
    expr_locals={},
):
    assert sequence.is_weighted
    animation = Animation(start, start)

    constant_dur = get_constant_duration(sequence, texture_anim, expr_locals)
    distributable_duration = duration - constant_dur

    if distributable_duration <= 0:
        raise GeneratorError(
            f"Duration '{duration}' is not enough for the weighted sequence '{sequence.name}' with constant duration '{constant_dur}'"
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
                action, animation.end, expr_locals
            )

        append_action_to_animation(
            action, action_start, action_duration, animation, texture_anim, expr_locals
        )

    if not duration_distributor.is_empty():
        raise GeneratorError(f"Couldn't distribute duration over weights")

    return animation


def get_unweighted_action_timeframe(action: Action, action_start: int, expr_locals={}):
    if isinstance(action.time, Duration):
        action_duration = evaluate_duration(action.time, expr_locals)
    elif isinstance(action.time, Timeframe):
        start, end, duration = evaluate_timeframe(action.time, expr_locals)
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
    action: Action,
    start: int,
    duration: Optional[int],
    anim: Animation,
    texture_anim,
    expr_locals,
):
    if isinstance(action, SequenceAction):
        anim.append(
            sequence_action_to_animation(action, start, duration, texture_anim, expr_locals)
        )
    else:
        assert duration is not None
        index = texture_anim.states.index(action.state_ref)
        anim.add_frame(index, start, start + duration)

    # Add mark
    if action.mark:
        anim.marks[action.mark] = Mark(start, anim.end)


def sequence_action_to_animation(
    action: SequenceAction,
    start: int,
    duration: Optional[int],
    texture_anim: TextureAnimation,
    expr_locals: dict,
):
    sequence = texture_anim.sequences[action.sequence_ref]
    anim = Animation(start, start)

    if sequence.is_weighted:
        if not duration:
            raise GeneratorError(
                f"Didn't pass duration to weighted sequence '{sequence.name}'"
            )

        if action.is_weighted:
            duration_distributor = utils.DurationDistributor(duration, action.repeat)
            for _ in range(action.repeat):
                anim.append(
                    weighted_sequence_to_animation(
                        sequence,
                        anim.end,
                        duration_distributor.take(1),
                        texture_anim,
                        expr_locals,
                    )
                )

            if not duration_distributor.is_empty():
                raise GeneratorError(f"Couldn't distribute duration over weights")
        else:
            for _ in range(action.repeat):
                anim.append(
                    weighted_sequence_to_animation(
                        sequence, anim.end, duration, texture_anim, expr_locals
                    )
                )
    else:
        if duration:
            raise GeneratorError(f"Passing duration to unweighted sequence '{sequence.name}'")

        for _ in range(action.repeat):
            anim.append(
                unweighted_sequence_to_animation(sequence, anim.end, texture_anim, expr_locals)
            )

    return anim


def get_constant_duration(sequence: Sequence, texture_anim: TextureAnimation, expr_locals={}):
    constant_duration = 0
    for action in sequence.actions:
        if isinstance(action.time, Duration):
            constant_duration += evaluate_duration(action.time, expr_locals)
        elif not action.is_weighted and isinstance(action, SequenceAction):
            seq = texture_anim.sequences[action.sequence_ref]
            constant_duration += get_constant_duration(seq, texture_anim, expr_locals)

    return constant_duration


def evaluate_timeframe(
    timeframe: Timeframe, expr_locals: dict
) -> Union[tuple[int, int, int], tuple[None, int, None]]:
    """Evaluates the expressions in a timeframe and returns its start, end and duration.

    Returns a tuple '(start, end, duration)', where either all values != None or only end != None.
    """

    start = evaluate_int(timeframe.start, expr_locals) if timeframe.start else None
    end = evaluate_int(timeframe.end, expr_locals) if timeframe.end else None
    duration = evaluate_int(timeframe.duration, expr_locals) if timeframe.duration else None

    if start and duration:
        end = start + duration
    elif start and end and not duration:
        duration = end - start

    return (start, end, duration)  # end is always != None


def evaluate_duration(duration: Duration, expr_locals: dict):
    return evaluate_int(duration, expr_locals)
