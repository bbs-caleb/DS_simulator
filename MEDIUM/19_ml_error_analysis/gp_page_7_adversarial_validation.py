"""Adversarial validation for residual error analysis."""

from typing import Optional

import numpy as np
import pandas as pd

import residuals
from sklearn.base import ClassifierMixin
from sklearn.metrics import roc_auc_score


def _absolute_residuals(
    y_test: pd.Series,
    y_pred: pd.Series,
    func: Optional[str],
) -> pd.Series:
    """Calculate absolute residuals using the residuals module."""
    function_name = "residuals" if func is None else func
    residual_function = getattr(residuals, function_name)
    values = residual_function(y_test, y_pred)

    return pd.Series(
        np.abs(values),
        index=y_test.index,
        dtype=float,
    )


def adversarial_validation(
    classifier: ClassifierMixin,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    y_pred: pd.Series,
    quantile: float = 0.1,
    func: Optional[str] = None,
) -> dict:
    """Adversarial validation residual analysis."""
    resid = _absolute_residuals(
        y_test=y_test,
        y_pred=y_pred,
        func=func,
    )

    top_k = int(np.floor(len(X_test) * quantile))
    worst_indices = resid.nlargest(top_k).index

    is_error = pd.Series(
        0,
        index=X_test.index,
        dtype=int,
    )
    is_error.loc[worst_indices] = 1

    classifier.fit(X_test, is_error)

    error_probability = classifier.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(
        is_error,
        error_probability,
    )

    if hasattr(classifier, "feature_importances_"):
        feature_importances = pd.Series(
            np.abs(classifier.feature_importances_),
            index=X_test.columns,
        )
    elif hasattr(classifier, "coef_"):
        feature_importances = pd.Series(
            np.abs(classifier.coef_[0]),
            index=X_test.columns,
        )
    else:
        feature_importances = None

    result = {
        "ROC-AUC": roc_auc,
        "feature_importances": feature_importances,
    }
    return result
