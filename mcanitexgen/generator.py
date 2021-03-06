from dataclasses import dataclass
from typing import Iterator, Optional

from mcanitexgen import utils
from mcanitexgen.expressions import evaluate_int
from mcanitexgen.parser import (
    IntExpression,
    Sequence,
    SequenceAction,
    StateAction,
    TextureAnimation,
)


class GeneratorError(Exception):
    pass


class AnimationContext:
    def __init__(
        self, anim: TextureAnimation, contexts: dict[str, "AnimationContext"] = dict()
    ):
        self.anim = anim
        self.end = 0
        self.state_to_index_map = {state: idx for idx, state in enumerate(self.anim.states)}
        self.frames = []
        self.marks: dict[str, Mark] = {}

        self._constant_sequence_durations: dict[str, int] = {}
        self._eval_locals = contexts

    def advance_time_by(self, amount: int):
        """ Advances the time of the animation by some amount """
        self.end += amount

    def advance_time_to(self, target_time: int):
        assert self.end <= target_time
        assert self.frames

        if self.frames:
            self.frames[-1]["time"] += self.elapsed_time(target_time)

        self.end = target_time

    def elapsed_time(self, current_time: int):
        """ Returns how much time elapsed from the last animation frame until the current time """
        return current_time - self.end

    def index_of_state(self, state: str):
        return self.state_to_index_map[state]

    def get_constant_duration(self, seq: Sequence):
        if seq.name in self._constant_sequence_durations:
            return self._constant_sequence_durations[seq.name]

        constant_duration = 0
        for action in seq.actions:
            if isinstance(action, StateAction) and action.duration:
                constant_duration += action.duration
            elif isinstance(action, SequenceAction):
                if action.duration:
                    constant_duration += action.repeat * action.duration

        return constant_duration

    def mark(self, name: str):
        return self.marks[name]

    def get_sequence_by_ref(self, ref: str):
        if not ref in self.anim.sequences:
            raise GeneratorError(f"Sequence '{ref}' doesn't exist")
        return self.anim.sequences[ref]

    def evaluate_int_expr(self, expr: IntExpression):
        return evaluate_int(expr, self._eval_locals)


@dataclass
class Mark:
    name: str
    start: int
    end: int


def animation_to_frames(
    anim: TextureAnimation, contexts: dict[str, AnimationContext] = dict()
):
    context = AnimationContext(anim, contexts)
    sequence_to_frames(anim.sequences["main"], context)

    return context.frames


def sequence_to_frames(seq: Sequence, ctx: AnimationContext, duration: Optional[int] = None):
    for action, action_duration in zip(seq.actions, get_action_durations(seq, duration)):
        start_time = ctx.end

        if action.start:
            try:
                start = ctx.evaluate_int_expr(action.start)
            except Exception as e:
                raise GeneratorError(f"Error while parsing start: '{action.start}'") from e
            ctx.advance_time_to(start)

        if action.end:
            try:
                end = ctx.evaluate_int_expr(action.end)
            except Exception as e:
                raise GeneratorError(f"Error while parsing end: '{action.end}'") from e
            action_duration = ctx.elapsed_time(end)

        if action_duration and not isinstance(action_duration, int):
            try:
                action_duration = ctx.evaluate_int_expr(action.duration)
            except Exception as e:
                raise GeneratorError(f"Error while parsing duration: '{action.end}'") from e

        if isinstance(action, StateAction):
            if action_duration == None:
                action_duration = 1

            ctx.frames.append(state_action_to_frames(action, action_duration, ctx))
        elif isinstance(action, SequenceAction):
            sequence_action_to_frames(action, action_duration, ctx)

        if action.mark:
            ctx.marks[action.mark] = Mark(action.mark, start_time, ctx.end)


def get_action_durations(seq: Sequence, duration: int) -> Iterator[Optional[int]]:
    if seq.is_weighted:
        if not duration:
            raise GeneratorError(f"Didn't pass duration to weighted sequence '{seq.name}'")

        weighted_action_durations = utils.partition_by_weights(
            duration, seq.total_weight, seq.weights()
        )
        return map(
            lambda a: next(weighted_action_durations) if a.has_weight else a.duration,
            seq.actions,
        )
    else:
        if duration:
            raise GeneratorError(f"Passed duration to constant sequence '{seq.name}'")

        return map(lambda a: a.duration, seq.actions)


def state_action_to_frames(action: StateAction, duration: int, ctx: AnimationContext):
    index = ctx.index_of_state(action.state)
    ctx.advance_time_by(duration)
    return {"index": index, "time": duration}


def sequence_action_to_frames(action: SequenceAction, duration: int, ctx: AnimationContext):
    seq = ctx.get_sequence_by_ref(action.ref)

    if action.weight:
        if duration:
            duration -= action.repeat * ctx.get_constant_duration(seq)

        for d in utils.partition_by_weights(duration, action.repeat, [1] * action.repeat):
            sequence_to_frames(seq, ctx, d)
    else:
        if duration:
            duration -= ctx.get_constant_duration(seq)

        for i in range(action.repeat):
            sequence_to_frames(seq, ctx, duration)
