"""Contrastive loss implementation using pytorch."""

import torch


def contrastive_loss(
    x1: torch.Tensor, x2: torch.Tensor, y: torch.Tensor, margin: float = 5.0
) -> torch.Tensor:
    """
    Computes the contrastive loss using pytorch.
    Using Euclidean distance as metric function.

    Args:
        x1 (torch.Tensor): Embedding vectors of the
            first objects in the pair (shape: (N, M))
        x2 (torch.Tensor): Embedding vectors of the
            second objects in the pair (shape: (N, M))
        y (torch.Tensor): Ground truth labels (1 for similar, 0 for dissimilar)
            (shape: (N,))
        margin (float): Margin to enforce dissimilar samples to be farther apart than

    Returns:
        torch.Tensor: The contrastive loss
    """
    # pylint: disable-next=not-callable
    distance = torch.linalg.norm(x1 - x2, dim=1)
    gap = torch.clamp(margin - distance, min=0.0)
    loss = y * distance * distance + (1 - y) * gap * gap
    return loss.mean()
