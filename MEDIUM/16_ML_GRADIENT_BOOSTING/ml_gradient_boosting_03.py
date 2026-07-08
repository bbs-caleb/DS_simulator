"""Gradient boosting regressor built on top of sklearn decision trees."""

import numpy as np
from sklearn.tree import DecisionTreeRegressor


class GradientBoostingRegressor:  # pylint: disable=too-many-instance-attributes
    """Gradient boosting regressor."""

    def __init__(
        self,
        n_estimators=100,
        learning_rate=0.1,
        max_depth=3,
        min_samples_split=2,
        loss="mse",
        verbose=False,
    ):  # pylint: disable=too-many-arguments,too-many-positional-arguments
        """Initialize hyperparameters and internal state.

        Args:
            n_estimators: number of trees in the ensemble.
            learning_rate: gradient descent step size.
            max_depth: maximum depth of every tree.
            min_samples_split: minimum samples required to split a node.
            loss: "mse" or a custom callable(y_true, y_pred) -> (loss, grad).
            verbose: if True, print the loss value on every iteration.
        """
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.loss = loss
        self.verbose = verbose
        self.base_pred_ = None  # constant baseline, set in fit()
        self.trees_ = []  # ensemble of trees, filled in fit()

        if callable(loss):
            self._loss_fn = loss
        elif loss == "mse":
            self._loss_fn = self._mse
        else:
            raise ValueError(f"Unsupported loss: {loss!r}")

    def _mse(self, y_true, y_pred):
        """Mean squared error loss function and gradient."""
        diff = y_pred - y_true  # residuals: prediction minus true value
        loss = np.mean(diff ** 2)  # average of squared residuals
        grad = diff  # gradient d(diff^2)/d(y_pred) = 2 * diff, 2 dropped
        return loss, grad

    def fit(self, X, y):  # pylint: disable=invalid-name
        """Fit the model to the data.

        Args:
            X: array-like of shape (n_samples, n_features)
            y: array-like of shape (n_samples,)

        Returns:
            GradientBoostingRegressor: The fitted model.
        """
        y = np.asarray(y, dtype=float)
        self.base_pred_ = np.mean(y)
        predictions = np.full(shape=len(y), fill_value=self.base_pred_)
        self.trees_ = []

        for i in range(self.n_estimators):
            loss, grad = self._loss_fn(y, predictions)
            antigradient = -grad  # direction that decreases the loss

            tree = DecisionTreeRegressor(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
            )
            tree.fit(X, antigradient)

            predictions = predictions + self.learning_rate * tree.predict(X)
            self.trees_.append(tree)

            if self.verbose:
                print(f"Iteration {i + 1}/{self.n_estimators}, loss: {loss:.4f}")

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
        for tree in self.trees_:
            predictions = predictions + self.learning_rate * tree.predict(X)
        return predictions
