import fire
import json
import pickle
import pandas as pd

from sklearn.ensemble import IsolationForest

from src.features import add_features
from src.metrics import recall_at_precision, recall_at_specificity, curves


def train(
    train_path: str = "",
    test_path: str = "",
    target: str = "target",
):
    """Model training job

    Args:
        train_path (str): Train dataset path
        test_path (str): Test dataset path
        target (str): Target column name
    """
    train_dataset = pd.read_csv(train_path)
    test_dataset = pd.read_csv(test_path)

    train_dataset = add_features(train_dataset)
    test_dataset = add_features(test_dataset)

    train_dataset.to_csv(train_path, index=False)
    test_dataset.to_csv(test_path, index=False)

    model = IsolationForest(n_estimators=10)
    model.fit(train_dataset.drop(target, axis=1))

    test_targets = test_dataset[target].values
    pred_scores = -model.score_samples(test_dataset.drop(target, axis=1))

    metrics = {
        "recall_precision_95": recall_at_precision(test_targets, pred_scores, 0.95),
        "recall_specificity_95": recall_at_specificity(test_targets, pred_scores, 0.95),
    }
    with open("./metrics/metrics.json", "w") as f:
        json.dump(metrics, f)

    curves(test_targets, pred_scores)

    with open("./models/model.pkl", "wb") as f:
        pickle.dump(model, f)


if __name__ == "__main__":
    fire.Fire(train)
