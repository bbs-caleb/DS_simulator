"""Triplet loss implementation using pytorch."""

import torch


def triplet_loss(
    anchor: torch.Tensor,
    positive: torch.Tensor,
    negative: torch.Tensor,
    margin: float = 5.0,
) -> torch.Tensor:
    """
    Computes the triplet loss using pytorch.
    Using Euclidean distance as metric function.

    Args:
        anchor (torch.Tensor): Embedding vectors of
            the anchor objects in the triplet (shape: (N, M))
        positive (torch.Tensor): Embedding vectors of
            the positive objects in the triplet (shape: (N, M))
        negative (torch.Tensor): Embedding vectors of
            the negative objects in the triplet (shape: (N, M))
        margin (float): Margin to enforce dissimilar samples to be farther apart than

    Returns:
        torch.Tensor: The triplet loss
    """
    # pylint: disable-next=not-callable
    distance_positive = torch.linalg.norm(anchor - positive, dim=1)
    # pylint: disable-next=not-callable
    distance_negative = torch.linalg.norm(anchor - negative, dim=1)
    loss = torch.clamp(distance_positive - distance_negative + margin, min=0.0)
    return loss.mean()
