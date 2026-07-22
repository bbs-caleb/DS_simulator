"""Deterministic traffic splitting for an A/B experiment."""

from bisect import bisect_right
from hashlib import sha256
from math import isclose
from typing import List, Tuple


class Experiment:
    """Contains the logic for assigning clicks to experiment groups."""

    def __init__(
        self,
        experiment_id: int,
        groups: Tuple[str, ...] = ("A", "B"),
        group_weights: List[float] = None,
    ):
        if not groups:
            raise ValueError("At least one group must be provided.")

        self.experiment_id = experiment_id
        self.groups = tuple(groups)

        self.salt = sha256(
            f"experiment:{self.experiment_id}".encode("utf-8")
        ).hexdigest()

        if group_weights is None:
            equal_weight = 1.0 / len(self.groups)
            self.group_weights = [equal_weight] * len(self.groups)
        else:
            if len(group_weights) != len(self.groups):
                raise ValueError(
                    "The number of group weights must match the number of groups."
                )

            if any(weight < 0 for weight in group_weights):
                raise ValueError("Group weights must be non-negative.")

            if not isclose(
                sum(group_weights),
                1.0,
                rel_tol=1e-9,
                abs_tol=1e-9,
            ):
                raise ValueError("Group weights must sum to 1.")

            self.group_weights = list(group_weights)

        cumulative_weight = 0.0
        self._cumulative_weights = []

        for weight in self.group_weights:
            cumulative_weight += weight
            self._cumulative_weights.append(cumulative_weight)

        self._cumulative_weights[-1] = 1.0

    def group(self, click_id: int) -> Tuple[int, str]:
        """Assign a click to a deterministic experiment group.

        Parameters
        ----------
        click_id: int
            Identifier of the click.

        Returns
        -------
        Tuple[int, str]
            Group index and group name.
        """
        click_key = f"{self.salt}:{click_id}".encode("utf-8")
        digest = sha256(click_key).digest()

        hash_value = int.from_bytes(digest[:8], byteorder="big")
        random_value = hash_value / 2**64

        group_id = bisect_right(
            self._cumulative_weights,
            random_value,
        )

        if group_id == len(self.groups):
            group_id -= 1

        return group_id, self.groups[group_id]
