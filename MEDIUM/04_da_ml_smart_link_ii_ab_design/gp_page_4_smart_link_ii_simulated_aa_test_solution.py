"""CPC sampling, statistical testing, and simulated A/A testing."""

# The function signatures are fixed by the educational task.
# pylint: disable=too-many-arguments,too-many-positional-arguments

from typing import Tuple

import numpy as np
from scipy.stats import ttest_ind


def cpc_sample(
    n_samples: int,
    conversion_rate: float,
    reward_avg: float,
    reward_std: float,
) -> np.ndarray:
    """Generate a sample of cost-per-click values.

    Parameters
    ----------
    n_samples:
        Number of clicks in the sample.
    conversion_rate:
        Probability that a click leads to an action.
    reward_avg:
        Mean reward for an action.
    reward_std:
        Standard deviation of the reward.

    Returns
    -------
    np.ndarray
        Simulated CPC values.
    """
    actions = np.random.binomial(
        n=1,
        p=conversion_rate,
        size=n_samples,
    )
    rewards = np.random.normal(
        loc=reward_avg,
        scale=reward_std,
        size=n_samples,
    )

    cpc = actions * rewards

    return cpc


def t_test(
    cpc_a: np.ndarray,
    cpc_b: np.ndarray,
    alpha: float = 0.05,
) -> Tuple[bool, float]:
    """Compare two independent CPC samples using Welch's t-test.

    Parameters
    ----------
    cpc_a:
        CPC sample from the first group.
    cpc_b:
        CPC sample from the second group.
    alpha:
        Statistical significance level.

    Returns
    -------
    Tuple[bool, float]
        Significance flag and p-value.
    """
    test_result = ttest_ind(
        cpc_a,
        cpc_b,
        equal_var=False,
    )
    p_value = float(test_result.pvalue)
    is_significant = bool(p_value < alpha)

    return is_significant, p_value


def aa_test(
    n_simulations: int,
    n_samples: int,
    conversion_rate: float,
    reward_avg: float,
    reward_std: float,
    alpha: float = 0.05,
) -> float:
    """Estimate the type I error rate using simulated A/A tests.

    Parameters
    ----------
    n_simulations:
        Number of simulated A/A experiments.
    n_samples:
        Number of CPC observations in each group.
    conversion_rate:
        Conversion rate shared by both groups.
    reward_avg:
        Mean action reward shared by both groups.
    reward_std:
        Standard deviation of the action reward.
    alpha:
        Statistical significance level.

    Returns
    -------
    float
        Share of simulations with a false-positive result.
    """
    type_1_errors = np.zeros(n_simulations)

    for simulation_index in range(n_simulations):
        cpc_a = cpc_sample(
            n_samples,
            conversion_rate,
            reward_avg,
            reward_std,
        )
        cpc_b = cpc_sample(
            n_samples,
            conversion_rate,
            reward_avg,
            reward_std,
        )

        is_significant, _ = t_test(
            cpc_a,
            cpc_b,
            alpha,
        )
        type_1_errors[simulation_index] = is_significant

    type_1_errors_rate = float(type_1_errors.mean())

    return type_1_errors_rate
