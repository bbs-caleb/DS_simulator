import numpy as np

from src.metrics import recall_at_precision, recall_at_specificity


def test_recall_at_precision():
    """Test recall at precision metric"""
    true_labels = [1, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    pred_scores = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]

    metric = recall_at_precision(true_labels, pred_scores, 0.9)

    msg = "Metric should be float"
    assert isinstance(metric, float), msg

    msg = f"Metric should be equal to {metric}"
    assert np.isclose(metric, 0.333333333), msg


def test_recall_at_specificity():
    """Test recall at specificity metric"""
    true_labels = [1, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    pred_scores = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]

    metric = recall_at_specificity(true_labels, pred_scores, 0.7)

    msg = "Metric should be float"
    assert isinstance(metric, float), msg

    msg = f"Metric should be equal to {metric}"
    assert np.isclose(metric, 0.666666666), msg
