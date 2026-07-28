import pytest
import numpy as np
import pandas as pd

from src.features import add_features


@pytest.fixture(scope="module")
def test_df() -> pd.DataFrame:
    data = np.random.normal(0.0, 1.0, (5, 30))
    target = [0, 1, 0, 0, 1]
    dataset = pd.DataFrame(data=data, columns=[f"f{i + 1}" for i in range(30)])
    dataset["target"] = target
    return dataset


def test_add_features(test_df):
    test_df_copy = test_df.copy()
    test_df_shape = test_df.shape
    test_df_cols = set(test_df.columns)
    df_with_features = add_features(test_df)

    msg = "Initial dataset should not be modified"
    assert test_df.equals(test_df_copy), msg

    msg = "Number of rows should not change"
    assert df_with_features.shape[0] == test_df_shape[0], msg

    msg = "Number of columns should increase with new features"
    assert df_with_features.shape[1] >= test_df_shape[1], msg

    msg = "New columns should be added"
    cols = set(df_with_features.columns)
    assert cols.intersection(test_df_cols) == test_df_cols, msg
