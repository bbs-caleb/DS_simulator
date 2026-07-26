"""Sequential Forward Selection with a Bonferroni correction."""
from typing import Tuple

import numpy as np
from scipy.stats import ttest_rel
from sklearn.datasets import make_regression
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import RepeatedKFold
from sklearn.model_selection import cross_val_score


class SequentialForwardSelector:
    """
    Select features with SFS, a paired t-test, and Bonferroni correction.

    Parameters
    ----------
    model: estimator
        Machine-learning model, for example ``LinearRegression``.
    cv: cross-validation generator
        Cross-validation scheme, for example ``RepeatedKFold``.
    max_features: int
        Maximum number of features to select.
    verbose: int
        Print progress when greater than zero.
    alpha: float
        Significance level for the one-sided paired t-test.
    bonferroni: bool
        Apply the Bonferroni correction when ``True``.

    Attributes
    ----------
    n_features_: int or None
        Number of features in the dataset passed to ``fit``.
    selected_features_: list[int] or None
        Selected feature indices, sorted in ascending order.
    n_selected_features_: int
        Number of selected features.
    """

    def __init__(
        self,
        model,
        cv,
        max_features: int = 10,
        verbose: int = 0,
        alpha: float = 0.05,
        bonferroni: bool = True,
    ) -> None:
        """Initialize SequentialForwardSelector."""
        self.model = model
        self.cv = cv
        self.max_features = max_features
        self.verbose = verbose
        self.alpha = alpha
        self.bonferroni = bonferroni

        self.n_features_ = None
        self.selected_features_ = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Select statistically significant features."""
        self.n_features_ = X.shape[1]

        included_features = []
        excluded_features = list(range(self.n_features_))

        current_scores = cross_val_score(
            DummyRegressor(),
            X,
            y,
            scoring="r2",
            cv=self.cv,
            n_jobs=-1,
        )

        features_to_select = min(self.max_features, self.n_features_)

        for step in range(features_to_select):
            significant_candidates = []

            if self.bonferroni:
                corrected_alpha = self.alpha / len(excluded_features)
            else:
                corrected_alpha = self.alpha

            for candidate in excluded_features:
                subset = included_features + [candidate]
                candidate_scores = cross_val_score(
                    self.model,
                    X[:, subset],
                    y,
                    scoring="r2",
                    cv=self.cv,
                    n_jobs=-1,
                )

                _, p_value = ttest_rel(
                    candidate_scores,
                    current_scores,
                    alternative="greater",
                )

                if p_value < corrected_alpha:
                    significant_candidates.append(
                        (candidate, candidate_scores)
                    )

            if not significant_candidates:
                break

            best_feature, best_scores = max(
                significant_candidates,
                key=lambda result: result[1].mean(),
            )

            included_features.append(best_feature)
            excluded_features.remove(best_feature)
            current_scores = best_scores

            if self.verbose > 0:
                print(
                    f"Selected {step + 1}/{features_to_select}: "
                    f"feature {best_feature}, "
                    f"mean R2 = {best_scores.mean():.4f}"
                )

        self.selected_features_ = sorted(included_features)

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Return only the columns selected during ``fit``."""
        assert self.selected_features_ is not None, "Fit the model first"
        return X[:, self.selected_features_]

    @property
    def n_selected_features_(self) -> int:
        """Return the number of selected features."""
        assert self.selected_features_ is not None, "Fit the model first"
        return len(self.selected_features_)


def generate_dataset(
    n_samples: int = 10_000,
    n_features: int = 50,
    n_informative: int = 10,
    random_state: int = 42,
) -> Tuple:
    """Generate a synthetic regression dataset."""
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
    """Run the example from the task."""
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
        max_features=max_features,
        verbose=1,
        alpha=0.05,
        bonferroni=True,
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
