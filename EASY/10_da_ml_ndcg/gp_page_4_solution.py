"""Calculate the Normalized Discounted Cumulative Gain metric."""

from typing import List

import numpy as np


def normalized_dcg(
    relevance: List[float],
    k: int,
    method: str = "standard",
) -> float:
    """Calculate Normalized Discounted Cumulative Gain at k.

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
        Normalized Discounted Cumulative Gain score.

    Raises
    ------
    ValueError
        If method is neither "standard" nor "industry".
    """
    if method not in ("standard", "industry"):
        raise ValueError

    relevance_array = np.asarray(relevance, dtype=float)
    actual_relevance = relevance_array[:k]
    ideal_relevance = np.sort(relevance_array)[::-1][:k]

    positions = np.arange(1, actual_relevance.size + 1)
    discounts = np.log2(positions + 1)

    if method == "industry":
        actual_gain = np.power(2, actual_relevance) - 1
        ideal_gain = np.power(2, ideal_relevance) - 1
    else:
        actual_gain = actual_relevance
        ideal_gain = ideal_relevance

    actual_dcg = np.sum(actual_gain / discounts)
    ideal_dcg = np.sum(ideal_gain / discounts)

    if ideal_dcg == 0:
        return 0.0

    score = actual_dcg / ideal_dcg
    return float(score)
