import math

import pytest
from hypothesis import given, settings
from hypothesis.strategies import floats

from mcanitexgen import utils


class Test_PartitionByWeights:
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
