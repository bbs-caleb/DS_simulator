"""Calculate the cumulative gain ranking metric."""

from typing import List

import numpy as np


def cumulative_gain(relevance: List[float], k: int) -> float:
    """Score is cumulative gain at k (CG@k).

    Parameters
    ----------
    relevance : List[float]
        Relevance labels for ranked objects.
    k : int
        Number of first elements to be counted.

    Returns
    -------
    float
        Cumulative gain for the first k elements.
    """
    score = np.sum(relevance[:k])
    return float(score)
