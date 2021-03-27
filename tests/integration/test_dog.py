from pathlib import Path

from mcanitexgen.animation.generator import Mark, load_animations_from_file


def frame(index: int, time: int):
    return {"index": index, "time": time}


def test():
    texture_animations = load_animations_from_file(
        Path("tests/integration/res/dog.animation.py")
    )

    expected_head_start = 0
    expected_head_end = 2074
    expected_head_frames = [
        # bored: 840
        *[frame(2, 116), frame(3, 4)] * 7,
        # fall_asleep: 75
        frame(2, 50),
        frame(5, 25),
        # asleep: 600
        frame(3, 288),
        frame(5, 25),
        frame(3, 287),
        # wake_up: 75
        frame(5, 25),
        frame(2, 50),
        # happy: 64
        *[*[frame(4, 1), frame(2, 5)] * 2, frame(3, 4)] * 4,
        # curious: 400
        frame(0, 22),
        frame(1, 22),
        frame(0, 22),
        frame(1, 334),
        # NEUTRAL: 20
        frame(0, 20),
    ]
    expected_head_marks = {"asleep": Mark(915, 1515), "peek_while_sleeping": Mark(1203, 1228)}

    head = texture_animations["Head"]
    assert head.start == expected_head_start
    assert head.end == expected_head_end
    assert head.frames == expected_head_frames
    assert head.marks == expected_head_marks

    assert sum(map(lambda f: f["time"], head.frames)) == expected_head_end

    expected_tail_n_hindlegs_start = 0
    expected_tail_n_hindlegs_end = 2074
    expected_tail_n_hindlegs_frames = [
        # bored: 800
        *[
            *[frame(3, 12), frame(4, 12)] * 5,
            frame(2, 80),
        ]
        * 4,
        # TAIL_LOW: 650
        frame(2, 650),
        # wagging_with_pause: 600
        *[
            *[
                frame(1, 5),
                frame(0, 5),
            ]
            * 9,
            *[
                frame(1, 8),
                frame(0, 7),
            ]
            * 4,
            frame(1, 10),
            frame(2, 40),
        ]
        * 3,
        frame(2, 24),
    ]

    tail_n_hindlegs = texture_animations["TailAndHindlegs"]
    assert tail_n_hindlegs.start == expected_tail_n_hindlegs_start
    assert tail_n_hindlegs.end == expected_tail_n_hindlegs_end
    assert tail_n_hindlegs.frames == expected_tail_n_hindlegs_frames

    assert (
        sum(map(lambda f: f["time"], tail_n_hindlegs.frames)) == expected_tail_n_hindlegs_end
    )

    expected_dream_start = 0
    expected_dream_end = 2074
    expected_dream_frames = [
        # NONE: 1090
        frame(0, 1090),
        # appear: 45
        frame(1, 15),
        frame(2, 15),
        frame(3, 15),
        # jumping steak: 60
        *[frame(4, 5), frame(5, 5)] * 6,
        # STEAK_GROUND: 5
        frame(4, 5),
        # STEAK_JUMPING: 3
        frame(5, 3),
        # pop: 4
        frame(6, 2),
        frame(7, 2),
        # NONE: 840
        frame(0, 867),
    ]

    dream = texture_animations["Dream"]

    assert dream.start == expected_dream_start
    assert dream.end == expected_dream_end
    assert dream.frames == expected_dream_frames
