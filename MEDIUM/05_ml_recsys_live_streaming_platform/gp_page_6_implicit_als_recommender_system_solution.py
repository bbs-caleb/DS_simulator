"""Implicit ALS recommendations for a live-streaming platform."""

import os
import pickle
import sys
from typing import List, Tuple

import implicit
import numpy as np
import pandas as pd
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from scipy import sparse


app = FastAPI()


class User(BaseModel):
    """Class of JSON output."""

    user_id: int
    personal: List[str]


def process_data(
    path_from: str,
) -> Tuple[pd.DataFrame, sparse.csr_matrix]:
    """Load and process user-streamer session data.

    Parameters
    ----------
    path_from : str
        Path to the CSV file.

    Returns
    -------
    data : pandas.DataFrame
        DataFrame with source columns, categorical identifiers,
        and viewing duration.
    sparse_user_item : scipy.sparse.csr_matrix
        User-streamer matrix containing total viewing duration.
    """
    column_names = [
        "uid",
        "session",
        "streamer_name",
        "time_start",
        "time_end",
    ]
    data = pd.read_csv(
        path_from,
        names=column_names,
        header=None,
    )

    data["total_time_stream"] = (
        data["time_end"] - data["time_start"]
    ).clip(lower=0)

    data["uid"] = data["uid"].astype("category")
    data["streamer_name"] = data["streamer_name"].astype("category")

    data["user_id"] = data["uid"].cat.codes
    data["streamer_id"] = data["streamer_name"].cat.codes

    interactions = (
        data.groupby(
            ["user_id", "streamer_id"],
            as_index=False,
            observed=True,
        )["total_time_stream"]
        .sum()
    )

    sparse_user_item = sparse.csr_matrix(
        (
            interactions["total_time_stream"].to_numpy(
                dtype=np.float64
            ),
            (
                interactions["user_id"].to_numpy(),
                interactions["streamer_id"].to_numpy(),
            ),
        ),
        shape=(
            len(data["uid"].cat.categories),
            len(data["streamer_name"].cat.categories),
        ),
    )
    sparse_user_item.eliminate_zeros()

    return data, sparse_user_item


def fit_model(
    sparse_user_item,
    model_path: str,
    iterations: int = 12,
    factors: int = 100,
    regularization: float = 0.2,
    alpha: float = 100,
    random_state: int = 42,
) -> implicit.als.AlternatingLeastSquares:
    """Fit an implicit ALS model and save it as a pickle file.

    Parameters
    ----------
    sparse_user_item : scipy.sparse.csr_matrix
        User-streamer matrix.
    model_path : str
        Path where the trained model must be saved.
    iterations : int, optional
        Number of ALS iterations, by default 12.
    factors : int, optional
        Number of latent factors, by default 100.
    regularization : float, optional
        Regularization strength, by default 0.2.
    alpha : float, optional
        Confidence multiplier, by default 100.
    random_state : int, optional
        Random seed, by default 42.

    Returns
    -------
    implicit.als.AlternatingLeastSquares
        Trained ALS model.
    """
    model = implicit.als.AlternatingLeastSquares(
        factors=factors,
        regularization=regularization,
        iterations=iterations,
        random_state=random_state,
    )

    confidence = (sparse_user_item * alpha).astype(
        np.float64
    )
    model.fit(confidence, show_progress=False)

    with open(model_path, "wb") as file:
        pickle.dump(
            model,
            file,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

    return model


def load_model(
    model_path: str,
) -> implicit.als.AlternatingLeastSquares:
    """Load a trained ALS model from a pickle file."""
    with open(model_path, "rb") as file:
        model = pickle.load(file)

    return model


def personal_recomendations(
    user_id: int,
    n_similar: int,
    model: implicit.als.AlternatingLeastSquares,
    data: pd.DataFrame,
) -> List[str]:
    """Generate personal streamer recommendations.

    Parameters
    ----------
    user_id : int
        Source user identifier from the CSV file.
    n_similar : int
        Maximum number of recommendations.
    model : implicit.als.AlternatingLeastSquares
        Trained ALS model.
    data : pandas.DataFrame
        Processed viewing data.

    Returns
    -------
    List[str]
        Streamer names ordered by predicted relevance.
    """
    user_rows = data.loc[
        data["uid"] == user_id,
        "user_id",
    ]

    if user_rows.empty:
        return []

    internal_user_id = int(user_rows.iloc[0])

    interactions = (
        data.groupby(
            ["user_id", "streamer_id"],
            as_index=False,
            observed=True,
        )["total_time_stream"]
        .sum()
    )

    sparse_user_item = sparse.csr_matrix(
        (
            interactions["total_time_stream"].to_numpy(
                dtype=np.float64
            ),
            (
                interactions["user_id"].to_numpy(),
                interactions["streamer_id"].to_numpy(),
            ),
        ),
        shape=(
            len(data["uid"].cat.categories),
            len(data["streamer_name"].cat.categories),
        ),
    )

    number_of_items = sparse_user_item.shape[1]
    number_to_recommend = min(n_similar, number_of_items)

    streamer_ids, _ = model.recommend(
        internal_user_id,
        sparse_user_item[internal_user_id],
        N=number_to_recommend,
        filter_already_liked_items=True,
    )

    streamer_mapping = (
        data[["streamer_id", "streamer_name"]]
        .drop_duplicates("streamer_id")
        .set_index("streamer_id")["streamer_name"]
    )

    similar_items = [
        str(streamer_mapping.loc[int(streamer_id)])
        for streamer_id in streamer_ids
        if int(streamer_id) in streamer_mapping.index
    ]

    return similar_items


@app.get("/recomendations/user/{user_id}")
async def get_recomendation(user_id: int) -> User:
    """Return personal streamer recommendations through FastAPI."""
    data_path = os.path.join(
        sys.path[0],
        os.environ["data_path"],
    )
    model_filename = os.environ.get(
        "model_path",
        "model.pkl",
    )
    model_path = os.path.join(
        sys.path[0],
        model_filename,
    )

    data, _ = process_data(data_path)
    model = load_model(model_path)

    personal = personal_recomendations(
        user_id,
        100,
        model,
        data,
    )

    user = User(
        user_id=user_id,
        personal=personal,
    )

    return user


def main() -> None:
    """Run application."""
    uvicorn.run("solution:app", host="localhost")


if __name__ == "__main__":
    main()
