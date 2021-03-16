import math

import pytest
from hypothesis import given, settings
from hypothesis.strategies import floats

from mcanitexgen import utils


class Test_round_half_away_from_zero:
    @pytest.mark.parametrize(
        "number, expected",
        [
            (0, 0),
            (1, 1),
            (5.1, 5),
            (5.9, 6),
            (5.5, 6),
            (5.4999, 5),
            (-4.1, -4),
            (-4.5, -5),
            (-4.4999, -4),
        ],
    )
    def test(self, number, expected):
        assert utils.round_half_away_from_zero(number) == expected


class Test_partition_by_weights:
    @pytest.mark.parametrize(
        "number,weights,expected",
        [
            (10, [1], [10]),
            (10, [1, 1], [5, 5]),
            (10, [3, 3], [5, 5]),
            (10, [4, 1], [8, 2]),
        ],
    )
    def test_perfect_partition(self, number, weights, expected):
        total_weight = sum(weights)
        partitions = list(utils.partition_by_weights(number, total_weight, weights))
        assert partitions == expected
        assert sum(partitions) == number

    @pytest.mark.parametrize(
        "number,weights,expected",
        [(10, [3], [10]), (10, [1, 3], [3, 7]), (10, [3, 4], [4, 6])],
    )
    def test_imperfect_partition(self, number, weights, expected):
        total_weight = sum(weights)
        partitions = list(utils.partition_by_weights(number, total_weight, weights))
        assert partitions == expected
        assert sum(partitions) == number


class Test_DurationDistributor:
    @pytest.mark.parametrize(
        "number,weights,expected",
        [
            (10, [1], [10]),
            (10, [1, 1], [5, 5]),
            (10, [3, 3], [5, 5]),
            (10, [4, 1], [8, 2]),
        ],
    )
    def test_perfect_partition(self, number, weights, expected):
        distributor = utils.DurationDistributor(number, sum(weights))
        partitions = list(map(lambda w: distributor.take(w), weights))

        assert partitions == expected
        assert sum(partitions) == number

    def test_take_more_than_is_left(self):
        distributor = utils.DurationDistributor(10, 10)
        distributor.take(9)

        with pytest.raises(ValueError, match="Weights exceed passed total weight.*"):
            distributor.take(9)

    def test_is_empty(self):
        distributor = utils.DurationDistributor(10, 10)

        assert distributor.is_empty() == False
        distributor.take(5)
        assert distributor.is_empty() == False
        distributor.take(5)
        assert distributor.is_empty() == True

    def test_take_from_empty(self):
        distributor = utils.DurationDistributor(10, 10)
        distributor.take(10)

        with pytest.raises(Exception, match="Trying to take from empty Distributor"):
            distributor.take(5)
