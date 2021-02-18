#!/usr/bin/env python3

from collections import defaultdict


def divide_or_zero(numerator, denominator):
    return numerator / denominator if denominator > 0 else 0


def std_float(number):
    return float("{:.2f}".format(number))


def normalize_confusion_matrix(matrix, imap, unique):
    sigma = [sum(matrix[imap[i]]) for i in unique]
    normalized_rows = []
    for n, row in enumerate(matrix):
        normalized_rows.append(
            list(map(lambda j: float(std_float(divide_or_zero(j, sigma[n]))), row))
        )
    matrix = normalized_rows

    return matrix


def calculate_matrix_with_labels(actual, predicted, label, normalize=False):
    TP, FN, FP, TN = compute_counts(actual, predicted, label)
    cm = [[TP, FP], [FN, TN]]

    return (
        [
            [divide_or_zero(TP, (TP + FP)), divide_or_zero(FP, (TP + FP))],
            [divide_or_zero(FN, (FN + TN)), divide_or_zero(TN, (FN + TN))],
        ]
        if normalize
        else cm
    )


def compute_confusion_matrix(actual, predicted):
    unique = sorted(set(actual).union(set(predicted)))
    matrix = [[0 for _ in unique] for _ in unique]
    imap = {key: i for i, key in enumerate(unique)}

    for p, a in zip(predicted, actual):
        matrix[imap[p]][imap[a]] += 1
    return matrix, imap, unique


def confusion_matrix(actual, predicted, label=None, normalize=False):
    if label:
        return calculate_matrix_with_labels(actual, predicted, label, normalize)

    matrix, imap, unique = compute_confusion_matrix(actual, predicted)

    if normalize:
        matrix = normalize_confusion_matrix(matrix, imap, unique)

    return matrix, [str(_) for _ in list(imap.keys())]


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
        true_pos += expected_matches_label and predicted_matches_expected
        false_neg += expected_matches_label and not predicted_matches_expected
        true_neg += not expected_matches_label and predicted_matches_expected
        false_pos += not expected_matches_label and not predicted_matches_expected
    return true_pos, false_neg, false_pos, true_neg


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
            d[label] = {"n_true": n_true, "n_pred": n_pred}
        except:
            print("Could not get counts for label: {}".format(label))
    return d


def precision_recall_f1_accuracy(y_true, y_pred, label=1):
    """
    :param y_true: List[str/int], true labels
    :param y_pred: List[str/int], model predicted labels
    :return: dict with precision, recall, f1_score and accuracy as percent
    """
    TP, FN, FP, TN = compute_counts(y_true, y_pred, label)
    precision = divide_or_zero(TP, (TP + FP))
    recall = divide_or_zero(TP, (TP + FN))
    f1_score = divide_or_zero(2 * (precision * recall), (precision + recall))
    accuracy = divide_or_zero((TP + TN), (TP + TN + FP + FN))
    metrics = {
        "precision": std_float(precision),
        "recall": std_float(recall),
        "f1_score": std_float(f1_score),
        "accuracy": std_float(accuracy * 100),
    }
    metrics.update(dict(TP=TP, FN=FN, FP=FP, TN=TN))
    return metrics


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
    if not labels:
        labels = sorted(list(set(y_true)))

    for label in labels:
        d[label]["cm"] = confusion_matrix(y_true, y_pred, label)
        d[label]["normalized_cm"] = confusion_matrix(
            y_true, y_pred, label, normalize=True
        )
        d[label]["metrics"] = precision_recall_f1_accuracy(y_true, y_pred, label)
        d["label_count_dict"] = get_label_counts(y_true, y_pred, labels)
    return d


def print_normalized_confusion_matrix(actual, predicted):
    matrix, labels = confusion_matrix(actual, predicted, normalize=True)
    print("\nConfusion Matrix:")
    print("\t\tActual")
    print("Predicted\t" + "\t".join([_[:7] for _ in labels]))
    print(
        "\n".join(
            [
                "\t" + label[:7] + "\t" + "\t".join([str(cell) for cell in row])
                for label, row in zip(labels, matrix)
            ]
        )
    )
