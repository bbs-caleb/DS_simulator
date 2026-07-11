"""Step 03: Diagnostic plots coordinates for residual analysis."""

from typing import Tuple

import numpy as np
from scipy import stats


def xy_fitted_residuals(
    y_true: np.ndarray, y_pred: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Coordinates (x, y) for fitted residuals against true values."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    residuals = y_true - y_pred
    return y_pred, residuals


def xy_normal_qq(
    y_true: np.ndarray, y_pred: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Coordinates (x, y) for normal Q-Q plot."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    residuals = y_true - y_pred
    std_residuals = (
        residuals - residuals.mean()
    ) / residuals.std()

    theoretical, ordered = stats.probplot(
        std_residuals,
        dist="norm",
        fit=False,
    )
    return theoretical, ordered


def xy_scale_location(
    y_true: np.ndarray, y_pred: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Coordinates (x, y) for scale-location plot."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    residuals = y_true - y_pred
    std_residuals = (
        residuals - residuals.mean()
    ) / residuals.std()
    return y_pred, np.sqrt(np.abs(std_residuals))
