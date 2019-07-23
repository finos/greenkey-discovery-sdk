#!/usr/bin/env python3

from collections import defaultdict


def compute_counts(y_true, y_pred, label):
    """
    :param y_true: List[str/int] : List of true labels (expected value) for each test
    :param y_pred: List[str/int]: List of classifier predicted labels (observed_values) / test
    :param label: label to use as reference for computing counts
    :return: 5-tuple: Tuple(int, int, int, int, int, dict (contains same information as int but with headers)
    """
    true_pos, false_neg, false_pos, true_neg = 0, 0, 0, 0
    for y, y_ in zip(y_true, y_pred):
        expected_matches_label = y == label
        predicted_matches_expected = y == y_
        if expected_matches_label:
            if predicted_matches_expected:
                true_pos += 1
            else:
                false_neg += 1
        else:
            if predicted_matches_expected:
                true_neg += 1
            else:
                false_pos += 1
    return dict(TP=true_pos, FN=false_neg, FP=false_pos, TN=true_neg)


def precision_recall_f1_accuracy(y_true, y_pred, label=1):
    """
    :param y_true: List[str/int], true labels
    :param y_pred: List[str/int], model predicted labels
    :param label: str, referemce label for confusion matrix 
    :return: dict with precision, recall, f1_score and accuracy as percent
    """
    d = compute_counts(y_true, y_pred, label)
    TP, FN, FP, TN = d["TP"], d["FN"], d["FP"], d["TN"]
    precision = TP / (TP + FP)
    recall = TP / (TP + FN)
    f1_score = 2 * (precision * recall) / (precision + recall)
    accuracy = (TP + TN) / (TP + TN + FP + FN)
    metrics = {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "accuracy": accuracy * 100,
    }
    metrics.update(d)
    return metrics


def confusion_matrix(y_true, y_pred, label, normalize=True):
    """
    :param y_true: List[str/int], true labels
    :param y_pred: List[str/int], model predicted labels
    :param label: str, label to use as reference for confusion matrix
    :param normalize: bool; if True, returns normalized confusion matrix
    :return: List[List[int/float, int/float], List[int/float, int/float]]
        Lists contain ints if count matrix, if normalized, floats

    """
    d = compute_counts(y_true, y_pred, label)
    TP, FN, FP, TN = d["TP"], d["FN"], d["FP"], d["TN"]
    cm = [[TP, FP], [FN, TN]]

    return [[TP / (TP + FP), FP / (TP + FP)], \
            [FN / (FN + TN), TN / (FN + TN)]] if normalize else cm


def get_label_counts(y_true, y_pred, labels=None):
    """
    :param y_true:
    :param y_pred:
    :param labels: List[str], optional; if not passed, returns counts for each unique label in y_true

    :return: Dict[
                    label(str): {"n_true"(str): int-> count, "n_pred"(str): int->count},
                    ...
                    last_label(str): {"n_true": int, "n_pred": int}
                ]

        dict of dicts, keys of outer dicts are labels in y_true
        inner dict keys are "n_true" and "n_pred"  --> values are counts: # of times label is in y_true and y_pred

    """
    d = defaultdict(dict)
    if not labels:
        labels = list(set(y_true))
    for label in labels:
        try:
            n_true = len(list(filter(lambda x: x == label, y_true)))
            n_pred = len(list(filter(lambda x: x == label, y_pred)))
            d[label] = {'n_true': n_true, 'n_pred': n_pred}
        except:
            print("Could not get counts for label: {}".format(label))
    return d


def compute_all(y_true, y_pred, labels=None):
    """
    :param y_true:
    :param y_pred:
    :param labels:
    :return: computes and returns following stats if possible
        TP, FP, FN, TN
        normalized cm
        precision, recall, f1_score, accuracy
    """
    d = defaultdict(dict)
    for label in labels if labels is not None else sorted(list(set(y_true))):
        try:
            d[label] = {"cm": compute_counts(y_true, y_pred, label)}
            d[label]["normalized_cm"] = confusion_matrix(y_true,
                                                         y_pred,
                                                         label,
                                                         normalize=True)
            d[label]['metrics'] = precision_recall_f1_accuracy(y_true, y_pred, label)
            d["label_count_dict"] = get_label_counts(y_true, y_pred, labels)
        except Exception as exc:
            print("Error: %s with metric computation", exc)
            continue
    return d


if __name__ == "__main__":
    # TODO add to unittests
    def test_metrics():
        y_true = [0, 1, 1, 0, 1, 1]
        y_pred = [0, 0, 1, 0, 0, 1]

        # metrics + cm counts
        observed_metrics = precision_recall_f1_accuracy(y_true, y_pred, label=1)
        # Confusion Matrix - counts and normalized
        observed_normalized_cm = confusion_matrix(y_true,
                                                  y_pred,
                                                  label=1,
                                                  normalize=True)
        observed_cm = confusion_matrix(y_true, y_pred, label=1, normalize=False)

        expected_metrics = {
            "precision": 1.0,
            "recall": 0.5,
            "f1_score": 0.6666666666666666,
            "accuracy": 66.66666666666666,
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

    test_metrics()
