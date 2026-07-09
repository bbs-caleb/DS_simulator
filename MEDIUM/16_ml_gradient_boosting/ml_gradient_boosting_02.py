"""Loss functions for gradient boosting: MSE and MAE with their gradients."""

from typing import Tuple

import numpy as np


def mse(y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[float, np.ndarray]:
    """Mean squared error loss function and gradient."""
    diff = y_pred - y_true  # residuals: prediction minus true value
    loss = np.mean(diff ** 2)  # average of squared residuals
    grad = diff  # gradient d(diff^2)/d(y_pred) = 2 * diff, constant 2 dropped
    return loss, grad


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[float, np.ndarray]:
    """Mean absolute error loss function and gradient."""
    diff = y_pred - y_true  # residuals: prediction minus true value
    loss = np.mean(np.abs(diff))  # average of absolute residuals
    grad = np.sign(diff)  # gradient is +1, -1, or 0 depending on diff's sign
    return loss, grad
