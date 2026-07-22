"""Simulation-based selection of sample size and MDE."""

# The function signatures are fixed by the educational task.
# pylint: disable=too-many-arguments,too-many-positional-arguments

from typing import List, Tuple

import numpy as np
from scipy import stats


def cpc_sample(
    n_samples: int,
    conversion_rate: float,
    reward_avg: float,
    reward_std: float,
) -> np.ndarray:
    """Generate a sample of cost-per-click values."""
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
    """Compare two independent CPC samples using a t-test."""
    test_result = stats.ttest_ind(cpc_a, cpc_b)
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
    """Estimate the type I error rate using simulated A/A tests."""
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

        is_significant, _ = t_test(cpc_a, cpc_b, alpha)
        type_1_errors[simulation_index] = is_significant

    type_1_errors_rate = float(type_1_errors.mean())

    return type_1_errors_rate


def ab_test(
    n_simulations: int,
    n_samples: int,
    conversion_rate: float,
    mde: float,
    reward_avg: float,
    reward_std: float,
    alpha: float = 0.05,
) -> float:
    """Estimate the type II error rate using simulated A/B tests."""
    type_2_errors = np.zeros(n_simulations)
    test_conversion_rate = conversion_rate * (1.0 + mde)

    for simulation_index in range(n_simulations):
        cpc_a = cpc_sample(
            n_samples,
            conversion_rate,
            reward_avg,
            reward_std,
        )
        cpc_b = cpc_sample(
            n_samples,
            test_conversion_rate,
            reward_avg,
            reward_std,
        )

        is_significant, _ = t_test(cpc_a, cpc_b, alpha)
        type_2_errors[simulation_index] = not is_significant

    type_2_errors_rate = float(type_2_errors.mean())

    return type_2_errors_rate


def select_sample_size(
    n_samples_grid: List[int],
    n_simulations: int,
    conversion_rate: float,
    mde: float,
    reward_avg: float,
    reward_std: float,
    alpha: float = 0.05,
    beta: float = 0.2,
) -> Tuple[int, float, float]:
    """Select the first sample size satisfying error-rate limits."""
    last_n_samples = None
    last_type_1_error = float("nan")
    last_type_2_error = float("nan")

    for n_samples in n_samples_grid:
        type_1_error = aa_test(
            n_simulations,
            n_samples,
            conversion_rate,
            reward_avg,
            reward_std,
            alpha,
        )
        type_2_error = ab_test(
            n_simulations,
            n_samples,
            conversion_rate,
            mde,
            reward_avg,
            reward_std,
            alpha,
        )

        last_n_samples = n_samples
        last_type_1_error = type_1_error
        last_type_2_error = type_2_error

        if type_1_error <= alpha and type_2_error <= beta:
            return n_samples, type_1_error, type_2_error

    raise RuntimeError(
        "Can't find sample size. "
        f"Last sample size: {last_n_samples}, "
        f"last type 1 error: {last_type_1_error}, "
        f"last type 2 error: {last_type_2_error}. "
        "Make sure that the grid is big enough."
    )


def select_mde(
    n_samples: int,
    n_simulations: int,
    conversion_rate: float,
    mde_grid: List[float],
    reward_avg: float,
    reward_std: float,
    alpha: float = 0.05,
    beta: float = 0.2,
) -> Tuple[float, float]:
    """Select the first MDE satisfying the type II error limit."""
    last_mde = None
    last_type_2_error = float("nan")

    for mde in mde_grid:
        type_2_error = ab_test(
            n_simulations,
            n_samples,
            conversion_rate,
            mde,
            reward_avg,
            reward_std,
            alpha,
        )

        last_mde = mde
        last_type_2_error = type_2_error

        if type_2_error <= beta:
            return mde, type_2_error

    raise RuntimeError(
        "Can't find MDE. "
        f"Last MDE: {last_mde}, "
        f"last type 2 error: {last_type_2_error}. "
        "Make sure that the grid is big enough."
    )
