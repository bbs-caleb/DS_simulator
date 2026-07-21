"""FastAPI service with a greedy offer sampler."""

import numpy as np
import uvicorn
from fastapi import FastAPI

app = FastAPI()

OFFER_CLICKS = {}
CLICK_TO_OFFER = {}
OFFER_REWARDS = {}
OFFER_CONVERSIONS = {}

RANDOM_CLICKS = 100


def get_rpc(offer_id: int) -> float:
    """Return revenue per click for an offer."""
    clicks = OFFER_CLICKS.get(offer_id, 0)
    if clicks == 0:
        return 0.0
    return OFFER_REWARDS.get(offer_id, 0.0) / clicks


@app.get("/sample/")
def sample(click_id: int, offer_ids: str) -> dict:
    """Choose an offer randomly during initialization, then greedily."""
    offers_ids = [int(offer) for offer in offer_ids.split(",")]

    total_clicks = sum(OFFER_CLICKS.values())

    if total_clicks < RANDOM_CLICKS:
        offer_id = int(np.random.choice(offers_ids))
        sampler = "random"
    else:
        offer_id = max(offers_ids, key=get_rpc)
        sampler = "greedy"

    OFFER_CLICKS[offer_id] = OFFER_CLICKS.get(offer_id, 0) + 1
    CLICK_TO_OFFER[click_id] = offer_id

    response = {
        "click_id": click_id,
        "offer_id": offer_id,
        "sampler": sampler,
    }
    return response


@app.put("/feedback/")
def feedback(click_id: int, reward: float) -> dict:
    """Save feedback for a particular click."""
    offer_id = CLICK_TO_OFFER[click_id]
    reward = float(reward)
    is_conversion = reward > 0

    OFFER_REWARDS[offer_id] = OFFER_REWARDS.get(offer_id, 0.0) + reward

    if is_conversion:
        OFFER_CONVERSIONS[offer_id] = (
            OFFER_CONVERSIONS.get(offer_id, 0) + 1
        )

    response = {
        "click_id": click_id,
        "offer_id": offer_id,
        "is_conversion": is_conversion,
        "reward": reward,
    }
    return response


@app.get("/offer_ids/{offer_id}/stats/")
def stats(offer_id: int) -> dict:
    """Return statistics for an offer."""
    clicks = OFFER_CLICKS.get(offer_id, 0)
    conversions = OFFER_CONVERSIONS.get(offer_id, 0)
    reward = OFFER_REWARDS.get(offer_id, 0.0)

    if clicks == 0:
        cr = 0.0
        rpc = 0.0
    else:
        cr = conversions / clicks
        rpc = reward / clicks

    response = {
        "offer_id": offer_id,
        "clicks": clicks,
        "conversions": conversions,
        "reward": reward,
        "cr": cr,
        "rpc": rpc,
    }
    return response


def main() -> None:
    """Run the application."""
    uvicorn.run(app, host="localhost")


if __name__ == "__main__":
    main()
