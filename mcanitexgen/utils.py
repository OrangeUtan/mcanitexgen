import math
from typing import Generator, Iterable


def round_half_away_from_zero(num) -> int:
    """ y = sign(x) * floor(|x|+0.5) """

    if num >= 0:
        return math.floor(num + 0.5)
    else:
        return math.floor(num - 0.5)


def partition_by_weights(
    number: int, total_weight: int, weights: Iterable[int]
) -> Generator[int, None, None]:
    """ Partitions a number into a series of integers proportianal to a series of weights """

    remaining = number
    remaining_weight = total_weight

    for weight in weights:
        weighted_amount = int(
            round_half_away_from_zero((weight * remaining) / remaining_weight)
        )
        remaining -= weighted_amount
        remaining_weight -= weight

        if remaining_weight < 0:
            raise ValueError(f"Weights exceed passed total weight of '{total_weight}'")

        yield weighted_amount


class DurationDistributor:
    def __init__(self, num: int, total_weight: int):
        self.num = num
        self.total_weight = total_weight
        self.remaining = num
        self.remaining_weight = total_weight

    def take(self, weight: int):
        weighted_amount = int(
            round_half_away_from_zero((weight * self.remaining) / self.remaining_weight)
        )
        self.remaining -= weighted_amount
        self.remaining_weight -= weight

        if self.remaining_weight < 0:
            raise ValueError(f"Weights exceed passed total weight of '{self.total_weight}'")

        return weighted_amount

    def is_empty(self):
        return self.remaining <= 0
