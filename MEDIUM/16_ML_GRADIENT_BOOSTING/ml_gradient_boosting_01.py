"""Gradient boosting regressor: mean-value baseline (first weak learner)."""

import numpy as np
import pandas as pd  # pylint: disable=unused-import


class GradientBoostingRegressor:
    """Gradient boosting regressor."""

    def __init__(self):
        """Initialize the model attributes."""
        self.base_pred_ = None  # constant baseline prediction, set in fit()

    def fit(self, X, y):  # pylint: disable=invalid-name,unused-argument
        """Fit the model to the data.

        Args:
            X: array-like of shape (n_samples, n_features)
            y: array-like of shape (n_samples,)

        Returns:
            GradientBoostingRegressor: The fitted model.
        """
        self.base_pred_ = np.mean(y)  # constant baseline prediction
        return self

    def predict(self, X):  # pylint: disable=invalid-name
        """Predict the target of new data.

        Args:
            X: array-like of shape (n_samples, n_features)

        Returns:
            y: array-like of shape (n_samples,)
            The predict values.
        """
        predictions = np.full(shape=len(X), fill_value=self.base_pred_)
        return predictions
