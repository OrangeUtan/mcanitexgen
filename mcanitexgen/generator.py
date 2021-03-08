from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, Optional, Union

from mcanitexgen import utils
from mcanitexgen.expressions import evaluate_int
from mcanitexgen.parser import (
    Duration,
    ParserError,
    Sequence,
    SequenceAction,
    StateAction,
    TextureAnimation,
    Timeframe,
)


class GeneratorError(Exception):
    pass


# class AnimationContext:
#     def __init__(
#         self, anim: TextureAnimation, contexts: dict[str, "AnimationContext"] = dict()
#     ):
#         self.anim = anim
#         self.end = 0
#         self.state_to_index_map = {state: idx for idx, state in enumerate(self.anim.states)}
#         self.marks: dict[str, Mark] = {}
#         self.frames = []

#         self._constant_sequence_durations: dict[str, int] = {}
#         self._eval_locals = contexts

#     def advance_time_by(self, amount: int):
#         """ Advances the time of the animation by some amount """
#         self.end += amount

#     def advance_time_to(self, target_time: int):
#         assert self.end <= target_time
#         assert self.frames

#         if self.frames:
#             self.frames[-1]["time"] += self.elapsed_time(target_time)

#         self.end = target_time

#     def elapsed_time(self, current_time: int):
#         """ Returns how much time elapsed from the last animation frame until the current time """
#         return current_time - self.end

#     def index_of_state(self, state: str):
#         return self.state_to_index_map[state]

#     def get_constant_duration(self, seq: Sequence):
#         if seq.name in self._constant_sequence_durations:
#             return self._constant_sequence_durations[seq.name]

#         constant_duration = 0
#         for action in seq.actions:
#             if isinstance(action, StateAction) and action.duration:
#                 constant_duration += action.duration
#             elif isinstance(action, SequenceAction):
#                 if action.duration:
#                     constant_duration += action.repeat * action.duration

#         return constant_duration

#     def mark(self, name: str):
#         return self.marks[name]

#     def get_sequence_by_ref(self, ref: str):
#         if not ref in self.anim.sequences:
#             raise GeneratorError(f"Sequence '{ref}' doesn't exist")
#         return self.anim.sequences[ref]

#     def evaluate_int_expr(self, expr: str):
#         try:
#             return evaluate_int(expr, self._eval_locals)
#         except Exception as e:
#             raise GeneratorError(f"Error while parsing expression: '{expr}'") from e


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


def create_animation(texture_anim: TextureAnimation, expr_locals=dict()):
    return unweighted_sequence_to_animation(
        texture_anim.sequences["main"], texture_anim, expr_locals
    )


def unweighted_sequence_to_animation(
    sequence: Sequence, sequence_start: int, texture_anim: TextureAnimation, expr_locals={}
):
    assert not sequence.is_weighted
    animation = Animation(sequence_start, sequence_start)

    for action in sequence.actions:
        action_start, action_end = animation.end, animation.end

        if isinstance(action.time, Duration):
            action_duration = evaluate_duration(action.time, expr_locals)
            action_end += action_duration
        elif isinstance(action.time, Timeframe):
            start, end, duration = evaluate_timeframe(action.time, expr_locals)
            if start and end and duration:
                action_start = start
                action_end = start + duration
                action_duration = duration
            elif not start and end and not duration:
                action_end = end
                action_duration = action_end - action_start
            else:
                raise GeneratorError(
                    f"Unexpected combination of start, end, duration: '{start}', '{end}', '{duration}'"
                )
        else:
            action_duration = None

        # Create animation
        if isinstance(action, SequenceAction):
            action_animation = sequence_action_to_animation(
                action, action_start, action_duration, texture_anim, expr_locals
            )
            animation.append(action_animation)
        elif isinstance(action, StateAction):
            assert action_start is not None and action_end is not None
            index = texture_anim.states.index(action.state_ref)
            animation.add_frame(index, action_start, action_end)

        # Add mark
        if action.mark:
            animation.marks[action.mark] == Mark(action_start, animation.end)

    return animation


# def weighted_sequence_to_animation(seq: Sequence, ctx: AnimationContext, duration: int):
#     assert seq.is_weighted
#     frames = []

#     for action in seq.actions:
#         if isinstance(action.time, Weight):
#             pass
#         elif isinstance(action.time, Duration):
#             pass
#         elif isinstance(action.time, Timeframe):
#             pass


# def get_action_durations(seq: Sequence, duration: int) -> Iterator[Optional[int]]:
#     if seq.is_weighted:
#         if not duration:
#             raise GeneratorError(f"Didn't pass duration to weighted sequence '{seq.name}'")

#         weighted_action_durations = utils.partition_by_weights(
#             duration, seq.total_weight, seq.weights()
#         )
#         return map(
#             lambda a: next(weighted_action_durations) if a.has_weight else a.duration,
#             seq.actions,
#         )
#     else:
#         if duration:
#             raise GeneratorError(f"Passed duration to constant sequence '{seq.name}'")

#         return map(lambda a: a.duration, seq.actions)


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
        pass
    else:
        if duration:
            raise GeneratorError(f"Passing duration to unweighted sequence '{sequence.name}'")

        for _ in range(action.repeat):
            anim.append(
                unweighted_sequence_to_animation(sequence, start, texture_anim, expr_locals)
            )

    return anim


# def sequence_action_to_frames(action: SequenceAction, duration: int, ctx: AnimationContext):
#     seq = ctx.get_sequence_by_ref(action.ref)

#     if action.weight:
#         if duration:
#             duration -= action.repeat * ctx.get_constant_duration(seq)

#         for d in utils.partition_by_weights(duration, action.repeat, [1] * action.repeat):
#             sequence_to_frames(seq, ctx, d)
#     else:
#         if duration:
#             duration -= ctx.get_constant_duration(seq)

#         for i in range(action.repeat):
#             sequence_to_frames(seq, ctx, duration)


def get_constant_duration(seq: Sequence, texture_anim: TextureAnimation):
    pass


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
