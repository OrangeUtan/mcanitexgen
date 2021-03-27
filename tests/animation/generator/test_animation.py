import pytest

from mcanitexgen.animation.generator import Animation, GeneratorError


def frame(index: int, time: int):
    return {"index": index, "time": time}


class Test_append:
    def test(self):
        anim1 = Animation(0, 10, [frame(0, 10)])
        anim2 = Animation(10, 20, [frame(0, 10)])

        anim1.append(anim2)
        assert anim1 == Animation(0, 20, [frame(0, 10), frame(0, 10)])

    @pytest.mark.parametrize(
        "anim1, anim2, result",
        [
            (
                Animation(0, 10, [frame(0, 10)]),
                Animation(11, 20, [frame(0, 9)]),
                Animation(0, 20, [frame(0, 11), frame(0, 9)]),
            ),
            (
                Animation(0, 10, [frame(0, 10)]),
                Animation(30, 40, [frame(0, 10)]),
                Animation(0, 40, [frame(0, 30), frame(0, 10)]),
            ),
        ],
    )
    def test_fill_time_gap_between_animations(
        self, anim1: Animation, anim2: Animation, result: Animation
    ):
        anim1.append(anim2)
        assert anim1 == result

    def test_time_ranges_overlap(self):
        anim1 = Animation(0, 10, [frame(0, 10)])
        anim2 = Animation(5, 15, [frame(0, 10)])

        with pytest.raises(GeneratorError, match=".*starts before the other.*"):
            anim1.append(anim2)


class Test_add_frame:
    @pytest.mark.parametrize(
        "anim, index, start, end, result",
        [
            (Animation(0, 0), 0, 0, 10, Animation(0, 10, [frame(0, 10)])),
        ],
    )
    def test(self, anim: Animation, index, start, end, result):
        anim.add_frame(index, start, end)
        assert anim == result

    @pytest.mark.parametrize(
        "anim, index, start, end, result",
        [
            (Animation(0, 0), 0, 10, 25, Animation(10, 25, [frame(0, 15)])),
            (Animation(10, 10), 0, 20, 30, Animation(20, 30, [frame(0, 10)])),
        ],
    )
    def test_add_frame_with_start_to_empty_animation(
        self, anim: Animation, index, start, end, result
    ):
        anim.add_frame(index, start, end)
        assert anim == result

    @pytest.mark.parametrize(
        "anim, index, start, end, result",
        [
            (
                Animation(0, 10, [frame(0, 10)]),
                0,
                20,
                30,
                Animation(0, 30, [frame(0, 20), frame(0, 10)]),
            ),
            (
                Animation(20, 40, [frame(0, 5), frame(0, 5)]),
                0,
                60,
                70,
                Animation(20, 70, [frame(0, 5), frame(0, 25), frame(0, 10)]),
            ),
        ],
    )
    def test_fill_time_gap(self, anim: Animation, index, start, end, result):
        anim.add_frame(index, start, end)
        assert anim == result

    @pytest.mark.parametrize(
        "start, end",
        [
            (0, 0),
            (10, 10),
            (12, 11),
            (-4, -5),
            (-6, -5),
        ],
    )
    def test_invalid_start_and_end(self, start, end):
        anim = Animation(0, 0)

        with pytest.raises(
            GeneratorError, match=f"Illegal start and end for frame: '{start}' '{end}'"
        ):
            anim.add_frame(0, start, end)
