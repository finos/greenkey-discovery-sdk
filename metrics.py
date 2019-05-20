#!/usr/bin/env python3

def compute_counts(y_true, y_pred, label):
	"""
	:param y_true: List[str/int] : List of true labels (expected value) for each test
	:param y_pred: List[str/int]: List of classifier predicted labels (observed_values) / test
	:param label: label to use as reference for compuing counts
	:return: 5-tuple: Tuple(int, int, int, int, int, dict (contains same information as int but with headers)
	"""
	true_pos, false_neg, false_pos, true_neg = 0, 0, 0, 0
	for y, y_ in zip(y_true, y_pred):
		expected_matches_label = y==label
		predicted_matches_expected = y==y_
		if expected_matches_label:
			if predicted_matches_expected:
				true_pos +=1
			else:
				false_neg +=1
		else:
			if predicted_matches_expected:
				true_neg +=1
			else:
				false_pos +=1
	return dict(TP=true_pos, FN=false_neg, FP=false_pos,TN=true_neg)


# def _compute(y_true, y_pred, label):
# 	"""
# 	:param y_true: List[str]
# 	:param y_pred: List[str]
# 	:param label: str; should be among the set of strings in y_true
# 	:return:
# 	"""
# 	# assert label in set(y_true)
# 	true_pos = [(y, y1) for y, y1 in zip(y_true, y_pred) if y == label and y == y1]
# 	true_neg = [(y, y1) for y, y1 in zip(y_true, y_pred) if y != label and y == y1]
# 	false_neg = [(y, y1) for y, y1 in zip(y_true, y_pred) if y == label and y != y1]
# 	false_pos = [(y, y1) for y, y1 in zip(y_true, y_pred) if y != label and y != y1]
# 	TP, FN = len(true_pos), len(false_neg)
# 	FP, TN = len(false_pos), len(true_neg)
# 	return dict(TP=TP, FN=FN, FP=FP, TN=TN)


def precision_recall_f1_accuracy(y_true, y_pred, label):
	"""
	:param y_true: List[str]
	:param y_pred: List[str]
	:param label: positive/reference label
	:return:
	"""
	# d = _compute(y_true, y_pred, label)
	d = compute_counts(y_true, y_pred, label)
	TP, FN, FP, TN = d["TP"], d["FN"], d["FP"], d["TN"]
	precision = TP / (TP + FP)
	recall = TP / (TP + FN)
	f1_score = 2 * (precision * recall) / (precision + recall)
	accuracy = (TP + TN) / (TP + TN + FP + FN)
	metrics = {"precision": precision, "recall": recall, "f1_score": f1_score, "accuracy": accuracy*100}
	metrics.update(d)
	return metrics


def confusion_matrix(y_true, y_pred, label=1, normalize=True):
	"""
	:param y_true:
	:param y_pred:
	:param label:
	:param normalize:
	:return:
	# # np.asarray(normalized_cm)
	"""
	# d = _compute(y_true, y_pred, label)
	d = compute_counts(y_true, y_pred, label)
	TP, FN, FP, TN = d["TP"], d["FN"], d["FP"], d["TN"]
	cm = [[TP, FP], [FN, TN]]
	if not normalize:
		return cm           # denominator is predicted_pos_total and predicted_negative_total
	normalized_cm = [[TP / (TP + FP), FP / (TP + FP)], [FN / (FN + TN), TN / (FN + TN)]]
	return normalized_cm


if __name__ == "__main__":
	# TODO add to unittests
	def test_metrics():
		y_true = [0, 1, 1, 0, 1, 1]
		y_pred = [0, 0, 1, 0, 0, 1]

		# metrics + cm counts
		observed_metrics = precision_recall_f1_accuracy(y_true, y_pred, label=1)
		# Confusion Matrix - counts and normalized
		observed_normalized_cm = confusion_matrix(y_true, y_pred, label=1, normalize=True)
		observed_cm = confusion_matrix(y_true, y_pred, label=1, normalize=False)

		expected_metrics = {
			'precision': 1.0,
			'recall': 0.5,
			'f1_score': 0.6666666666666666,
			'accuracy': 66.66666666666666,
			'TP': 2,
			'FN': 2,
			'FP': 0,
			'TN': 2
		}
		expected_normalized_cm = [[1.0, 0.0], [0.5, 0.5]]
		expected_cm = [[2, 0], [2, 2]]

		assert observed_metrics == expected_metrics
		assert observed_cm == expected_cm
		assert observed_normalized_cm == expected_normalized_cm

	test_metrics()

