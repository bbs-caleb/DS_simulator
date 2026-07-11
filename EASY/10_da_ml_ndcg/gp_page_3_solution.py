"""Calculate the Discounted Cumulative Gain ranking metric."""

from typing import List

import numpy as np


def discounted_cumulative_gain(
    relevance: List[float],
    k: int,
    method: str = "standard",
) -> float:
    """Calculate Discounted Cumulative Gain at k.

    Parameters
    ----------
    relevance : List[float]
        Video relevance list.
    k : int
        Number of relevance values to include.
    method : str, optional
        Metric implementation method:
        "standard" uses relevance as gain;
        "industry" uses 2 ** relevance - 1 as gain.

    Returns
    -------
    float
        Discounted Cumulative Gain score.

    Raises
    ------
    ValueError
        If method is neither "standard" nor "industry".
    """
    if method not in ("standard", "industry"):
        raise ValueError

    relevance_array = np.asarray(relevance[:k], dtype=float)
    positions = np.arange(1, relevance_array.size + 1)
    discounts = np.log2(positions + 1)

    if method == "industry":
        relevance_array = np.power(2, relevance_array) - 1

    score = np.sum(relevance_array / discounts)
    return float(score)
