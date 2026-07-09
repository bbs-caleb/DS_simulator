"""Gradient boosting regressor with stochastic subsampling (SGD-style)."""

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
        subsample_size=0.5,
        replace=False,
    ):  # pylint: disable=too-many-arguments,too-many-positional-arguments
        """Initialize hyperparameters and internal state.

        Args:
            n_estimators: number of trees in the ensemble.
            learning_rate: gradient descent step size.
            max_depth: maximum depth of every tree.
            min_samples_split: minimum samples required to split a node.
            loss: "mse" or a custom callable(y_true, y_pred) -> (loss, grad).
            verbose: if True, print the loss value on every iteration.
            subsample_size: fraction of the dataset sampled for every tree.
            replace: if True, sample with replacement (bootstrap).
        """
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.loss = loss
        self.verbose = verbose
        self.subsample_size = subsample_size
        self.replace = replace
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

    def _subsample(self, X, y):  # pylint: disable=invalid-name
        """Draw a random subsample of the dataset.

        Args:
            X: array-like of shape (n_samples, n_features)
            y: array-like of shape (n_samples,)

        Returns:
            tuple: (sub_X, sub_y) with sample_size = subsample_size * n_samples
        """
        X = np.asarray(X)  # ensure positional indexing works for any input type
        y = np.asarray(y)
        n_samples = X.shape[0]
        sample_size = int(self.subsample_size * n_samples)
        indices = np.random.choice(n_samples, size=sample_size, replace=self.replace)
        sub_x = X[indices]
        sub_y = y[indices]
        return sub_x, sub_y

    def fit(self, X, y):  # pylint: disable=invalid-name
        """Fit the model to the data.

        Args:
            X: array-like of shape (n_samples, n_features)
            y: array-like of shape (n_samples,)

        Returns:
            GradientBoostingRegressor: The fitted model.
        """
        X = np.asarray(X)
        y = np.asarray(y, dtype=float)
        self.base_pred_ = np.mean(y)
        self.trees_ = []
        predictions = np.full(shape=len(y), fill_value=self.base_pred_)

        for i in range(self.n_estimators):
            loss, grad = self._loss_fn(y, predictions)  # gradient on full data
            antigradient = -np.asarray(grad)  # direction that decreases the loss

            sub_x, sub_antigrad = self._subsample(X, antigradient)

            tree = DecisionTreeRegressor(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
            )
            tree.fit(sub_x, sub_antigrad)

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
        X = np.asarray(X)
        predictions = np.full(shape=X.shape[0], fill_value=self.base_pred_)
        for tree in self.trees_:
            predictions = predictions + self.learning_rate * tree.predict(X)
        return predictions
