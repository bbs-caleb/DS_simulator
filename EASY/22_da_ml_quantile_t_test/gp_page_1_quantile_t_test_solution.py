from typing import List, Tuple

from scipy.stats import ttest_ind


def ttest(
    control: List[float],
    experiment: List[float],
    alpha: float = 0.05,
) -> Tuple[float, bool]:
    """Two-sample t-test for the means of two independent samples."""
    _, p_value = ttest_ind(control, experiment)
    result = bool(p_value < alpha)

    return float(p_value), result
