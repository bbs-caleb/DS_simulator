"""Cross-validated Cross-Entropy Loss evaluation for a classifier."""

from typing import List

from sklearn.model_selection import KFold, cross_val_score


def evaluate(model, embeddings, labels, cv: int = 5) -> List[float]:
    """Return Cross-Entropy Loss of the model for each cross-validation fold"""
    folds = KFold(n_splits=cv, shuffle=False)
    scores = cross_val_score(
        model, embeddings, labels, cv=folds, scoring="neg_log_loss"
    )
    return [-float(score) for score in scores]  # neg_log_loss -> Cross-Entropy Loss
