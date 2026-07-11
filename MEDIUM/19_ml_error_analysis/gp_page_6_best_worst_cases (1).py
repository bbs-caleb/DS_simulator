"""Best-case, worst-case, and corner-case residual analysis."""

from typing import Optional

import numpy as np
import pandas as pd

import residuals


def _absolute_residuals(
    y_test: pd.Series,
    y_pred: pd.Series,
    func: Optional[str],
) -> pd.Series:
    """Calculate absolute residuals with a function from residuals."""
    function_name = "residuals" if func is None else func
    residual_function = getattr(residuals, function_name)
    values = residual_function(y_test, y_pred)

    return pd.Series(
        np.abs(values),
        index=y_test.index,
        dtype=float,
    )


def _select_cases(
    X_test: pd.DataFrame,
    y_test: pd.Series,
    y_pred: pd.Series,
    top_k: int,
    mask: Optional[pd.Series],
    func: Optional[str],
    largest: bool,
) -> dict:
    """Select rows with the smallest or largest absolute residuals."""
    if mask is not None:
        X_test = X_test.loc[mask]
        y_test = y_test.loc[mask]
        y_pred = y_pred.loc[mask]

    resid = _absolute_residuals(y_test, y_pred, func)

    if largest:
        selected_index = resid.nlargest(top_k).index
    else:
        selected_index = resid.nsmallest(top_k).index

    result = {
        "X_test": X_test.loc[selected_index],
        "y_test": y_test.loc[selected_index],
        "y_pred": y_pred.loc[selected_index],
        "resid": resid.loc[selected_index],
    }
    return result


def best_cases(
    X_test: pd.DataFrame,
    y_test: pd.Series,
    y_pred: pd.Series,
    top_k: int = 10,
    mask: Optional[pd.Series] = None,
    func: Optional[str] = None,
) -> dict:
    """Return top-k best cases according to the given function."""
    return _select_cases(
        X_test=X_test,
        y_test=y_test,
        y_pred=y_pred,
        top_k=top_k,
        mask=mask,
        func=func,
        largest=False,
    )


def worst_cases(
    X_test: pd.DataFrame,
    y_test: pd.Series,
    y_pred: pd.Series,
    top_k: int = 10,
    mask: Optional[pd.Series] = None,
    func: Optional[str] = None,
) -> dict:
    """Return top-k worst cases according to the given function."""
    return _select_cases(
        X_test=X_test,
        y_test=y_test,
        y_pred=y_pred,
        top_k=top_k,
        mask=mask,
        func=func,
        largest=True,
    )
