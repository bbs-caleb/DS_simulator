"""FastAPI service with an epsilon-greedy offer sampler."""

import numpy as np
import uvicorn
from fastapi import FastAPI

app = FastAPI()

OFFER_CLICKS = {}
CLICK_TO_OFFER = {}
OFFER_REWARDS = {}
OFFER_CONVERSIONS = {}

EPSILON = 0.1


@app.on_event("startup")
def reset_statistics() -> None:
    """Reset all in-memory statistics before every application startup."""
    OFFER_CLICKS.clear()
    CLICK_TO_OFFER.clear()
    OFFER_REWARDS.clear()
    OFFER_CONVERSIONS.clear()


def get_rpc(offer_id: int) -> float:
    """Return revenue per click for an offer."""
    clicks = OFFER_CLICKS.get(offer_id, 0)
    if clicks == 0:
        return 0.0
    return OFFER_REWARDS.get(offer_id, 0.0) / clicks


@app.get("/sample/")
def sample(click_id: int, offer_ids: str) -> dict:
    """Choose an offer using the epsilon-greedy strategy."""
    offers_ids = [int(offer) for offer in offer_ids.split(",")]

    if np.random.random() < EPSILON:
        offer_id = int(np.random.choice(offers_ids))
        sampler = "random"
    else:
        offer_id = max(offers_ids, key=get_rpc)
        sampler = "greedy"

    OFFER_CLICKS[offer_id] = OFFER_CLICKS.get(offer_id, 0) + 1
    CLICK_TO_OFFER[click_id] = offer_id

    return {
        "click_id": click_id,
        "offer_id": offer_id,
        "sampler": sampler,
    }


@app.put("/feedback/")
def feedback(click_id: int, reward: float) -> dict:
    """Save feedback for a previously sampled click."""
    offer_id = CLICK_TO_OFFER[click_id]
    reward = float(reward)
    is_conversion = reward > 0

    OFFER_REWARDS[offer_id] = OFFER_REWARDS.get(offer_id, 0.0) + reward

    if is_conversion:
        OFFER_CONVERSIONS[offer_id] = (
            OFFER_CONVERSIONS.get(offer_id, 0) + 1
        )

    return {
        "click_id": click_id,
        "offer_id": offer_id,
        "is_conversion": is_conversion,
        "reward": reward,
    }


@app.get("/offer_ids/{offer_id}/stats/")
def stats(offer_id: int) -> dict:
    """Return accumulated statistics for an offer."""
    clicks = OFFER_CLICKS.get(offer_id, 0)
    conversions = OFFER_CONVERSIONS.get(offer_id, 0)
    reward = OFFER_REWARDS.get(offer_id, 0.0)

    if clicks == 0:
        cr = 0.0
        rpc = 0.0
    else:
        cr = conversions / clicks
        rpc = reward / clicks

    return {
        "offer_id": offer_id,
        "clicks": clicks,
        "conversions": conversions,
        "reward": reward,
        "cr": cr,
        "rpc": rpc,
    }


def main() -> None:
    """Run the application."""
    uvicorn.run("app:app", host="localhost")


if __name__ == "__main__":
    main()
