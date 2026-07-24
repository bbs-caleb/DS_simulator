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
    personal: List


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
        DataFrame with user, streamer, and session information.
    sparse_user_item : scipy.sparse.csr_matrix
        User-streamer matrix containing viewing duration.
    """
    data = pd.read_csv(
        path_from,
        names=[
            "uid",
            "session",
            "streamer_name",
            "time_start",
            "time_end",
        ],
    )

    data["total_time_stream"] = (
        data["time_end"] - data["time_start"]
    )

    data["uid"] = data["uid"].astype("category")
    data["streamer_name"] = data["streamer_name"].astype(
        "category"
    )

    data["user_id"] = data["uid"].cat.codes
    data["streamer_id"] = data["streamer_name"].cat.codes

    sparse_user_item = sparse.csr_matrix(
        (
            data["total_time_stream"].astype(float),
            (
                data["user_id"],
                data["streamer_id"],
            ),
        )
    )

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
    """Fit ALS and save the trained model.

    Parameters
    ----------
    sparse_user_item : scipy.sparse.csr_matrix
        User-streamer interaction matrix.
    model_path : str
        Path used to save the trained model.
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

    data_conf = (sparse_user_item * alpha).astype(
        "double"
    )

    model.fit(
        data_conf,
        show_progress=False,
    )

    with open(model_path, "wb") as file:
        pickle.dump(model, file)

    return model


def load_model(
    model_path: str,
) -> implicit.als.AlternatingLeastSquares:
    """Load the trained model from a pickle file."""
    with open(model_path, "rb") as file:
        model = pickle.load(file)

    return model


def personal_recomendations(
    user_id: int,
    n_similar: int,
    model: implicit.als.AlternatingLeastSquares,
    data: pd.DataFrame,
) -> List[str]:
    """Return streamers associated with the most similar users.

    Parameters
    ----------
    user_id : int
        Internal user identifier.
    n_similar : int
        Number of similar users to use.
    model : implicit.als.AlternatingLeastSquares
        Trained ALS model.
    data : pandas.DataFrame
        DataFrame containing users and streamers.

    Returns
    -------
    List[str]
        Streamer names ordered by user-factor similarity.
    """
    user_vecs = model.user_factors

    if user_id < 0 or user_id >= len(user_vecs):
        return []

    user_norms = np.sqrt(
        (user_vecs * user_vecs).sum(axis=1)
    )

    if user_norms[user_id] == 0:
        return []

    scores = (
        user_vecs.dot(user_vecs[user_id])
        / user_norms
    )

    limit = min(
        n_similar,
        len(scores),
    )

    if limit == 0:
        return []

    top_idx = np.argpartition(
        scores,
        -limit,
    )[-limit:]

    similar = sorted(
        zip(
            top_idx,
            scores[top_idx] / user_norms[user_id],
        ),
        key=lambda item: -item[1],
    )

    similar_items = []

    for similar_user_id, _ in similar:
        streamer_rows = data.loc[
            data["user_id"] == similar_user_id,
            "streamer_name",
        ]

        if not streamer_rows.empty:
            similar_items.append(
                str(streamer_rows.iloc[0])
            )

    return similar_items


@app.get("/recomendations/user/{user_id}")
async def get_recomendation(user_id: int):
    """Return personal streamer recommendations."""
    data_path = os.path.join(
        sys.path[0],
        os.environ["data_path"],
    )
    model_path = os.path.join(
        sys.path[0],
        os.environ["model_path"],
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
    uvicorn.run(
        "solution:app",
        host="localhost",
    )


if __name__ == "__main__":
    main()
