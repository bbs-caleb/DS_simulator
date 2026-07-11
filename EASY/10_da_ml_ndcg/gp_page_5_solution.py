"""Calculate the average Normalized Discounted Cumulative Gain."""

from typing import List

import numpy as np


def avg_ndcg(
    list_relevances: List[List[float]],
    k: int,
    method: str = "standard",
) -> float:
    """Calculate average nDCG at k for multiple queries.

    Parameters
    ----------
    list_relevances : List[List[float]]
        Video relevance lists for multiple queries.
    k : int
        Number of relevance values to include for each query.
    method : str, optional
        Metric implementation method:
        "standard" uses relevance as gain;
        "industry" uses 2 ** relevance - 1 as gain.

    Returns
    -------
    float
        Average Normalized Discounted Cumulative Gain score.

    Raises
    ------
    ValueError
        If method is neither "standard" nor "industry".
    """
    if method not in ("standard", "industry"):
        raise ValueError

    scores = []

    for relevance in list_relevances:
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
            scores.append(0.0)
        else:
            scores.append(float(actual_dcg / ideal_dcg))

    if not scores:
        return 0.0

    return float(np.mean(scores))
