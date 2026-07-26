"""Solution for Lasso feature selection."""
from typing import Tuple

import numpy as np
from sklearn.datasets import make_regression
from sklearn.linear_model import LassoCV
from sklearn.model_selection import RepeatedKFold


class LassoSelector:
    """
    Lasso selector.
    Select features using Linear Regression with Lasso regularization.

    Parameters
    ----------
    cv: cross-validation generator :
        cross-validation
    alphas: List[float] :
        list of alphas for Lasso
    random_state: int :
        random state for reproducibility

    Attributes
    ----------
    n_features_: int :
        number of features
    selected_features_: List[int] :
        list of selected features
    n_selected_features_: int :
        number of selected features
    """

    def __init__(self, cv, alphas, random_state=42):
        """Initialize LassoSelector."""
        self.cv = cv
        self.alphas = alphas
        self.random_state = random_state

        self.n_features_ = None
        self.selected_features_ = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Fit model.

        Parameters
        ----------
        X: np.ndarray :
            features
        y: np.ndarray :
            target

        Returns
        -------
        None

        """
        self.n_features_ = X.shape[1]

        model = LassoCV(
            cv=self.cv,
            alphas=self.alphas,
            random_state=self.random_state,
            n_jobs=-1,
        )
        model.fit(X, y)

        self.selected_features_ = np.where(
            model.coef_ != 0
        )[0].tolist()

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Reduce features to selected features.

        Parameters
        ----------
        X: np.ndarray :
            features

        Returns
        -------
        X: np.ndarray :
            reduced features

        """
        assert self.selected_features_ is not None, "Fit the model first"
        return X[:, self.selected_features_]

    @property
    def n_selected_features_(self):
        """Return the number of selected features."""
        assert self.selected_features_ is not None, "Fit the model first"
        return len(self.selected_features_)


def generate_dataset(
    n_samples: int = 10_000,
    n_features: int = 50,
    n_informative: int = 10,
    random_state: int = 42,
) -> Tuple:
    """
    Generate datasets.

    Parameters
    ----------
    n_samples: int :
        (Default value = 10_000)
        number of samples
    n_features: int :
        (Default value = 50)
        number of features
    n_informative: int :
        (Default value = 10)
        number of informative features, other features are noise
    random_state: int :
        (Default value = 42)
        random state for reproducibility

    Returns
    -------
    X: np.ndarray :
        features
    y: np.ndarray :
        target

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
    """Run."""
    random_state = 42
    n_samples = 10_000
    n_features = 50
    n_informative = 5
    n_splits = 3
    n_repeats = 10
    alphas = [2, 10]

    X, y = generate_dataset(
        n_samples,
        n_features,
        n_informative,
        random_state,
    )

    cv = RepeatedKFold(
        n_splits=n_splits,
        n_repeats=n_repeats,
        random_state=random_state,
    )
    print(f"Baseline features count: {X.shape[1]}")

    selector = LassoSelector(cv, alphas, random_state)
    selector.fit(X, y)

    print(f"Features count: {selector.n_features_}")
    print(f"Selected features: {selector.selected_features_}")
    print(
        "Selected features count: "
        f"{selector.n_selected_features_}"
    )


if __name__ == "__main__":
    run()
