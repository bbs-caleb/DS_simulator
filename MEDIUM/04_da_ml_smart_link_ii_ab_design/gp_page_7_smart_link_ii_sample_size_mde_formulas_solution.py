"""Analytical sample-size and MDE calculations for an A/B test."""

import numpy as np
from scipy import stats


def calculate_sample_size(
    reward_avg: float,
    reward_std: float,
    mde: float,
    alpha: float,
    beta: float,
) -> int:
    """Calculate the required sample size for each experiment group.

    Parameters
    ----------
    reward_avg:
        Average value of the metric.
    reward_std:
        Standard deviation of the metric.
    mde:
        Relative minimum detectable effect.
    alpha:
        Statistical significance level.
    beta:
        Type II error probability.

    Returns
    -------
    int
        Required sample size for each group.
    """
    assert mde > 0, "mde should be greater than 0"

    absolute_mde = reward_avg * mde
    alpha_quantile = stats.norm.ppf(1.0 - alpha / 2.0)
    beta_quantile = stats.norm.ppf(1.0 - beta)

    sample_size = (
        2.0
        * reward_std**2
        * (alpha_quantile + beta_quantile) ** 2
        / absolute_mde**2
    )

    return int(np.ceil(sample_size))


def calculate_mde(
    reward_std: float,
    sample_size: int,
    alpha: float,
    beta: float,
) -> float:
    """Calculate the absolute minimum detectable effect.

    Parameters
    ----------
    reward_std:
        Standard deviation of the metric.
    sample_size:
        Number of observations in each experiment group.
    alpha:
        Statistical significance level.
    beta:
        Type II error probability.

    Returns
    -------
    float
        Absolute minimum detectable effect.
    """
    alpha_quantile = stats.norm.ppf(1.0 - alpha / 2.0)
    beta_quantile = stats.norm.ppf(1.0 - beta)

    mde = (
        (alpha_quantile + beta_quantile)
        * np.sqrt(2.0)
        * reward_std
        / np.sqrt(sample_size)
    )

    return float(mde)
