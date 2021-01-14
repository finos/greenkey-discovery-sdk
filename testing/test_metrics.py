#!/usr/bin/env python3

from metrics import (
    compute_all,
    confusion_matrix,
    precision_recall_f1_accuracy,
    print_normalized_confusion_matrix,
)


def test_metrics():
    y_true = [0, 1, 1, 0, 1, 1]
    y_pred = [0, 0, 1, 0, 0, 1]

    # metrics + cm counts
    observed_metrics = precision_recall_f1_accuracy(y_true, y_pred, label=1)
    # Confusion Matrix - counts and normalized
    observed_normalized_cm = confusion_matrix(y_true, y_pred, label=1, normalize=True)
    observed_cm = confusion_matrix(y_true, y_pred, label=1, normalize=False)

    expected_metrics = {
        "precision": 1.00,
        "recall": 0.50,
        "f1_score": 0.67,
        "accuracy": 66.67,
        "TP": 2,
        "FN": 2,
        "FP": 0,
        "TN": 2,
    }
    expected_normalized_cm = [[1.0, 0.0], [0.5, 0.5]]
    expected_cm = [[2, 0], [2, 2]]

    assert observed_metrics == expected_metrics
    assert observed_cm == expected_cm
    assert observed_normalized_cm == expected_normalized_cm

    actual = ["B", "B", "C", "A", "B", "B", "C", "A", "A", "B", "D"]
    predicted = ["A", "B", "B", "A", "C", "B", "C", "C", "A", "C", "D"]
    print_normalized_confusion_matrix(actual, predicted)
    matrix, labels = confusion_matrix(actual, predicted, normalize=True)
    assert matrix == [
        [0.67, 0.33, 0.0, 0.0],
        [0.0, 0.67, 0.33, 0.0],
        [0.25, 0.5, 0.25, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]
    assert sorted(labels) == ["A", "B", "C", "D"]

    compute_all(actual, predicted)
