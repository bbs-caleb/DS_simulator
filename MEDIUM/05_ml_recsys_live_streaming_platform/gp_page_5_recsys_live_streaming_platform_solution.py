"""Popularity-based recommendations for a live-streaming platform."""

import os
import sys
from typing import List

import pandas as pd
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


class User(BaseModel):
    """Response model for the popularity endpoint."""

    user_id: int
    time: int
    popular_streamers: List


def process_data(path_from: str, time_now: int = 6147):
    """Read data and keep sessions active at the requested time."""
    column_names = [
        "uid",
        "session_id",
        "streamer_name",
        "time_start",
        "time_end",
    ]
    data = pd.read_csv(path_from, names=column_names)

    data = data[
        (data["time_start"] < time_now)
        & (data["time_end"] > time_now)
    ]

    return data


def recomend_popularity(data: pd.DataFrame):
    """Rank active streamers by their number of viewers."""
    popular_streamers = (
        data.groupby("streamer_name")["uid"]
        .count()
        .sort_values(ascending=False)
        .index
        .to_list()
    )

    return popular_streamers


@app.get("/popular/user/{user_id}")
async def get_popularity(user_id: int, time: int = 6147):
    """Return popular online streamers for a user."""
    data_path = os.path.join(sys.path[0], os.environ["data_path"])
    data = process_data(data_path, time)
    popular_streamers = recomend_popularity(data)

    user = User(
        user_id=user_id,
        time=time,
        popular_streamers=popular_streamers,
    )
    return user


def main() -> None:
    """Run application."""
    uvicorn.run("solution:app", host="localhost")


if __name__ == "__main__":
    main()
