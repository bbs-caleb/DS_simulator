"""Metrics for evaluating the quality of a ranked top-K result."""

from typing import List, Tuple


def _confusion_matrix_at_k(
    labels: List[int], scores: List[float], k: int
) -> Tuple[int, int, int, int]:
    """Return TP, FP, TN and FN after selecting the top-K scores."""
    if len(labels) != len(scores):
        raise ValueError("labels and scores must have the same length")

    top_k = min(max(k, 0), len(labels))
    ranked_indices = sorted(
        range(len(scores)),
        key=scores.__getitem__,
        reverse=True,
    )
    top_indices = set(ranked_indices[:top_k])

    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0

    for index, label in enumerate(labels):
        predicted_positive = index in top_indices

        if label == 1 and predicted_positive:
            true_positive += 1
        elif label == 0 and predicted_positive:
            false_positive += 1
        elif label == 0 and not predicted_positive:
            true_negative += 1
        elif label == 1 and not predicted_positive:
            false_negative += 1

    return true_positive, false_positive, true_negative, false_negative


def recall_at_k(labels: List[int], scores: List[float], k=5) -> float:
    """Return the fraction of all relevant objects found in the top-K."""
    true_positive, _, _, false_negative = _confusion_matrix_at_k(
        labels, scores, k
    )
    denominator = true_positive + false_negative

    if denominator == 0:
        return 0.0

    return true_positive / denominator


def precision_at_k(labels: List[int], scores: List[float], k=5) -> float:
    """Return the fraction of relevant objects among the top-K objects."""
    true_positive, false_positive, _, _ = _confusion_matrix_at_k(
        labels, scores, k
    )
    denominator = true_positive + false_positive

    if denominator == 0:
        return 0.0

    return true_positive / denominator


def specificity_at_k(labels: List[int], scores: List[float], k=5) -> float:
    """Return the fraction of irrelevant objects left outside the top-K."""
    _, false_positive, true_negative, _ = _confusion_matrix_at_k(
        labels, scores, k
    )
    denominator = true_negative + false_positive

    if denominator == 0:
        return 0.0

    return true_negative / denominator


def f1_at_k(labels: List[int], scores: List[float], k=5) -> float:
    """Return the harmonic mean of precision@K and recall@K."""
    true_positive, false_positive, _, false_negative = (
        _confusion_matrix_at_k(labels, scores, k)
    )
    denominator = 2 * true_positive + false_positive + false_negative

    if denominator == 0:
        return 0.0

    return 2 * true_positive / denominator
