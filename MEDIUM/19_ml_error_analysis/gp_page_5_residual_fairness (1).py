"""Residual fairness and fair model selection."""

from typing import List

import numpy as np
from sklearn.metrics import log_loss


def fairness(residuals: np.ndarray) -> float:
    """Compute fairness as one minus the Gini index."""
    absolute_residuals = np.abs(
        np.asarray(residuals, dtype=float)
    )

    if absolute_residuals.size == 0:
        raise ValueError("residuals must not be empty")

    mean_residual = np.mean(absolute_residuals)

    if mean_residual == 0:
        return 1.0

    pairwise_differences = np.abs(
        absolute_residuals[:, None]
        - absolute_residuals[None, :]
    )

    n_samples = len(absolute_residuals)
    gini = np.sum(pairwise_differences) / (
        2 * n_samples**2 * mean_residual
    )

    return float(1 - gini)


def best_prediction(
    y_true: np.ndarray,
    y_preds: List[np.ndarray],
    fairness_drop: float = 0.05,
) -> int:
    """Return the index of the best fair prediction vector."""
    y_true = np.asarray(y_true)
    baseline_prediction = np.asarray(y_preds[0], dtype=float)

    baseline_residuals = (
        y_true * np.log(baseline_prediction)
        + (1 - y_true) * np.log(1 - baseline_prediction)
    )
    baseline_fairness = fairness(baseline_residuals)

    best_index = 0
    best_loss = log_loss(
        y_true,
        baseline_prediction,
        labels=[0, 1],
    )

    minimum_fairness = baseline_fairness * (
        1 - fairness_drop
    )

    for index, prediction in enumerate(y_preds[1:], start=1):
        prediction = np.asarray(prediction, dtype=float)

        current_residuals = (
            y_true * np.log(prediction)
            + (1 - y_true) * np.log(1 - prediction)
        )
        current_fairness = fairness(current_residuals)
        current_loss = log_loss(
            y_true,
            prediction,
            labels=[0, 1],
        )

        if (
            current_loss < best_loss
            and current_fairness >= minimum_fairness
        ):
            best_index = index
            best_loss = current_loss

    return best_index
