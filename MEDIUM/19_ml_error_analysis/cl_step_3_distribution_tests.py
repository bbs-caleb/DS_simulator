"""Step 02: Statistical tests for residual distribution analysis."""

import math
from typing import Optional, Tuple

import numpy as np
from scipy import stats


def test_normality(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    alpha: float = 0.05,
) -> Tuple[float, bool]:
    """Normality test

    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Ground truth (correct) target values.

    y_pred : array-like of shape (n_samples,)
        Estimated target values.

    alpha : float, optional (default=0.05)
        Significance level for the test

    Returns
    -------
    p_value : float
        p-value of the normality test

    is_rejected : bool
        True if the normality hypothesis is rejected, False otherwise
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    resid = y_true - y_pred

    _, p_value = stats.shapiro(resid)
    p_value = float(p_value)
    is_rejected = bool(p_value < alpha)
    return p_value, is_rejected


def test_unbiased(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    prefer: Optional[str] = None,
    alpha: float = 0.05,
) -> Tuple[float, bool]:
    """Unbiasedness test

    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Ground truth (correct) target values.

    y_pred : array-like of shape (n_samples,)
        Estimated target values.

    prefer : str, optional (default=None)
        If None or "two-sided", test whether the residuals are unbiased.
        If "positive", test whether the residuals are unbiased or positive.
        If "negative", test whether the residuals are unbiased or negative.

    alpha : float, optional (default=0.05)
        Significance level for the test

    Returns
    -------
    p_value : float
        p-value of the test

    is_rejected : bool
        True if the unbiasedness hypothesis is rejected, False otherwise
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    resid = y_true - y_pred

    if prefer is None or prefer == "two-sided":
        alternative = "two-sided"
    elif prefer == "positive":
        alternative = "greater"
    elif prefer == "negative":
        alternative = "less"
    else:
        raise ValueError(
            "prefer must be one of: None, 'two-sided', 'positive', "
            "'negative'"
        )

    _, p_value = stats.ttest_1samp(
        resid, popmean=0.0, alternative=alternative
    )
    p_value = float(p_value)
    is_rejected = bool(p_value < alpha)
    return p_value, is_rejected


def _split_ordered_residuals(sorted_resid: np.ndarray, bins: int) -> list:
    """Split residuals (already sorted by target) into contiguous bins.

    All bins have the same size, except the last one, which absorbs
    the remainder of samples when ``n_samples`` is not evenly
    divisible by ``bins``.
    """
    n_samples = len(sorted_resid)
    bin_size = math.ceil(n_samples / bins)
    groups = []
    start = 0
    for _ in range(bins):
        end = min(start + bin_size, n_samples)
        if start < end:
            groups.append(sorted_resid[start:end])
        start = end
    return groups


def test_homoscedasticity(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    bins: int = 10,
    test: Optional[str] = None,
    alpha: float = 0.05,
) -> Tuple[float, bool]:
    """Homoscedasticity test

    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Ground truth (correct) target values.

    y_pred : array-like of shape (n_samples,)
        Estimated target values.

    bins : int, optional (default=10)
        Number of bins to use for the test.
        All bins are equal-width and have the same number of samples, except
        the last bin, which will include the remainder of the samples
        if n_samples is not divisible by bins parameter.

    test : str, optional (default=None)
        If None or "bartlett", perform Bartlett's test for equal variances.
        If "levene", perform Levene's test.
        If "fligner", perform Fligner-Killeen's test.

    alpha : float, optional (default=0.05)
        Significance level for the test

    Returns
    -------
    p_value : float
        p-value of the test

    is_rejected : bool
        True if the homoscedasticity hypothesis is rejected, False otherwise
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    resid = y_true - y_pred

    order = np.argsort(y_true)
    sorted_resid = resid[order]
    groups = _split_ordered_residuals(sorted_resid, bins)

    test_funcs = {
        "bartlett": stats.bartlett,
        "levene": stats.levene,
        "fligner": stats.fligner,
    }
    test_name = test or "bartlett"
    if test_name not in test_funcs:
        raise ValueError(
            "test must be one of: None, 'bartlett', 'levene', 'fligner'"
        )

    _, p_value = test_funcs[test_name](*groups)
    p_value = float(p_value)
    is_rejected = bool(p_value < alpha)
    return p_value, is_rejected
