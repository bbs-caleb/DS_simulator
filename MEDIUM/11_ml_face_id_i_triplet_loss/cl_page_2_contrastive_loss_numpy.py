"""Contrastive loss implementation using numpy."""

import numpy as np


def contrastive_loss(
    x1: np.ndarray, x2: np.ndarray, y: np.ndarray, margin: float = 5.0
) -> float:
    """
    Computes the contrastive loss using numpy.
    Using Euclidean distance as metric function.

    Args:
        x1 (np.ndarray): Embedding vectors of the
            first objects in the pair (shape: (N, M))
        x2 (np.ndarray): Embedding vectors of the
            second objects in the pair (shape: (N, M))
        y (np.ndarray): Ground truthlabels (1 for similar, 0 for dissimilar)
            (shape: (N,))
        margin (float): Margin to enforce dissimilar samples to be farther apart than

    Returns:
        float: The contrastive loss
    """
    diff = x1 - x2
    squared_distance = np.einsum("ij,ij->i", diff, diff)
    distance = np.sqrt(squared_distance)
    gap = np.maximum(margin - distance, 0.0)
    loss = y * squared_distance + (1 - y) * gap * gap
    return float(np.mean(loss))
