"""FastAPI service with a payout-aware Upper Confidence Bound sampler."""

import math

import uvicorn
from fastapi import FastAPI

app = FastAPI()

OFFER_CLICKS = {}
CLICK_TO_OFFER = {}
OFFER_REWARDS = {}
OFFER_CONVERSIONS = {}

UCB_COEFFICIENT = 0.30


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


def get_global_payout() -> float:
    """Return the average observed reward per conversion."""
    total_conversions = sum(OFFER_CONVERSIONS.values())

    if total_conversions == 0:
        return 1.0

    return sum(OFFER_REWARDS.values()) / total_conversions


def get_offer_payout(offer_id: int, global_payout: float) -> float:
    """Return an offer payout estimate or a global prior."""
    conversions = OFFER_CONVERSIONS.get(offer_id, 0)

    if conversions == 0:
        return global_payout

    return OFFER_REWARDS.get(offer_id, 0.0) / conversions


def get_ucb_score(
    offer_id: int,
    total_clicks: int,
    global_payout: float,
) -> float:
    """Return a payout-aware Upper Confidence Bound score."""
    clicks = OFFER_CLICKS.get(offer_id, 0)

    if clicks == 0:
        return float("inf")

    offer_payout = get_offer_payout(offer_id, global_payout)
    exploration_bonus = (
        UCB_COEFFICIENT
        * offer_payout
        * math.sqrt(math.log(total_clicks + 1) / clicks)
    )

    return get_rpc(offer_id) + exploration_bonus


@app.get("/sample/")
def sample(click_id: int, offer_ids: str) -> dict:
    """Choose the candidate offer with the largest UCB score."""
    offers_ids = [int(offer) for offer in offer_ids.split(",")]
    total_clicks = sum(OFFER_CLICKS.values())
    global_payout = get_global_payout()

    offer_id = max(
        offers_ids,
        key=lambda candidate: get_ucb_score(
            candidate,
            total_clicks,
            global_payout,
        ),
    )

    OFFER_CLICKS[offer_id] = OFFER_CLICKS.get(offer_id, 0) + 1
    CLICK_TO_OFFER[click_id] = offer_id

    return {
        "click_id": click_id,
        "offer_id": offer_id,
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
