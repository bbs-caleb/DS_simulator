"""Sequential Forward Selection for the T-Tested Features task."""
from typing import Tuple

import numpy as np
from sklearn.datasets import make_regression
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold


class SequentialForwardSelector:
    """
    Sequential forward selection.

    The algorithm starts with an empty feature subset. At every iteration it
    tries each not-yet-selected feature, measures the model's mean cross-
    validated R2 score, and permanently adds the best candidate.

    Parameters
    ----------
    model: estimator
        Machine-learning model, for example ``LinearRegression``.
    cv: cross-validation generator
        Cross-validation scheme, for example ``RepeatedKFold``.
    max_features: int
        Maximum number of features to select.
    verbose: int
        If greater than zero, print progress after every selected feature.

    Attributes
    ----------
    n_features_: int
        Number of features in the dataset passed to ``fit``.
    selected_features_: list[int]
        Selected column indices, sorted in ascending order.
    n_selected_features_: int
        Number of selected features.
    """

    def __init__(
        self,
        model,
        cv,
        max_features: int = 10,
        verbose: int = 0,
    ) -> None:
        """Initialize SequentialForwardSelector."""
        self.model = model
        self.cv = cv
        self.max_features = max_features
        self.verbose = verbose

        self.n_features_ = 0
        self.selected_features_ = []

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Select features using greedy forward search.

        Parameters
        ----------
        X: np.ndarray
            Two-dimensional feature matrix.
        y: np.ndarray
            Target values.
        """
        self.n_features_ = X.shape[1]
        self.selected_features_ = []

        excluded_features = list(range(self.n_features_))
        features_to_select = min(self.max_features, self.n_features_)
        current_score = float("-inf")

        for step in range(features_to_select):
            candidate_scores = {}

            for candidate in excluded_features:
                feature_subset = self.selected_features_ + [candidate]
                scores = cross_val_score(
                    self.model,
                    X[:, feature_subset],
                    y,
                    scoring="r2",
                    cv=self.cv,
                    n_jobs=-1,
                )
                candidate_scores[candidate] = scores.mean()

            best_feature = max(
                candidate_scores,
                key=lambda feature: candidate_scores[feature],
            )
            best_score = candidate_scores[best_feature]

            if self.selected_features_ and best_score <= current_score:
                if self.verbose > 0:
                    print("No feature improves the score. Selection stopped.")
                break

            self.selected_features_.append(best_feature)
            excluded_features.remove(best_feature)
            current_score = best_score

            if self.verbose > 0:
                print(
                    f"Selected {step + 1}/{features_to_select}: "
                    f"feature {best_feature}, mean R2 = {best_score:.4f}"
                )

        self.selected_features_.sort()

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Keep only the columns selected by ``fit``.

        Parameters
        ----------
        X: np.ndarray
            Feature matrix with the original columns.

        Returns
        -------
        np.ndarray
            Matrix containing only selected columns.
        """
        return X[:, self.selected_features_]

    @property
    def n_selected_features_(self) -> int:
        """Return the number of selected features."""
        return len(self.selected_features_)


def generate_dataset(
    n_samples: int = 10_000,
    n_features: int = 50,
    n_informative: int = 10,
    random_state: int = 42,
) -> Tuple:
    """
    Generate a synthetic regression dataset.

    Parameters
    ----------
    n_samples: int
        Number of observations.
    n_features: int
        Total number of features.
    n_informative: int
        Number of useful features; all other features are noise.
    random_state: int
        Random seed for reproducibility.

    Returns
    -------
    Tuple
        Feature matrix ``X`` and target vector ``y``.
    """
    X, y = make_regression(
        n_samples=n_samples,
        n_features=n_features,
        noise=100,
        random_state=random_state,
        n_informative=n_informative,
        bias=100,
        shuffle=True,
    )
    return X, y


def run() -> None:
    """Run the demonstration from the task template."""
    random_state = 42
    n_samples = 10_000
    n_features = 50
    n_informative = 5
    max_features = 10
    n_splits = 3
    n_repeats = 10

    X, y = generate_dataset(
        n_samples,
        n_features,
        n_informative,
        random_state,
    )

    model = LinearRegression()
    cv = RepeatedKFold(
        n_splits=n_splits,
        n_repeats=n_repeats,
        random_state=random_state,
    )

    scores = cross_val_score(
        model,
        X,
        y,
        scoring="r2",
        cv=cv,
        n_jobs=-1,
    )
    print(f"Baseline features count: {X.shape[1]}")
    print(f"Baseline R2 score: {scores.mean():.4f}")

    selector = SequentialForwardSelector(
        model,
        cv,
        max_features,
        verbose=1,
    )
    selector.fit(X, y)
    X_transformed = selector.transform(X)

    scores = cross_val_score(
        model,
        X_transformed,
        y,
        scoring="r2",
        cv=cv,
        n_jobs=-1,
    )

    print(f"Features: {selector.selected_features_}")
    print(f"Features count: {selector.n_selected_features_}")
    print(f"Mean R2 score: {scores.mean():.4f}")


if __name__ == "__main__":
    run()
