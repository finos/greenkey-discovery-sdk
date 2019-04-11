# import re
# def test_accuracy(infile, accuracy):
# 	with open(infile, 'r+', encoding='utf-8') as f:
# 		list_of_lines = f.readlines()
# 		# last_line = list_of_lines[-1].replace("\n", '').strip()
# 		last_line = '(11688 / 11745) tests passed in 187s'
# 		try:
# 			correct, total, time = re.findall("\d+", last_line)
# 		except ValueError:
# 			print("Reported Accuracy and Time Unknown")
# 		assert correct / total == accuracy
# 		return {
# 			'num_correct': correct,
# 			'num_tests': total,
# 			'accuracy': correct / total
# 		}
#
# test_acc = test_accuracy(infile, accuracy)
# correct, total, accuracy = test_acc['num_correct'], test_acc['num_tests'], test_acc["accuracy"]
#
#
# def summary(intents, tests):
# 	d = defaultdict(dict)
# 	for intent in intents:
# 		list(filter(lambda x: x['expected'], tests))
from somewhere import bucket

inpath = 'tests.txt'
with open(inpath, 'r+', encoding='utf-8') as f:
	list_of_lines = f.readlines()

out = [tuple(line.strip().lower().split(":")) for line in list_of_lines if
       line.strip() and line.split(":")[0].split()[0].lower().strip() in ['testing', 'expected', 'observed']]
# print(out[:10])

# List[Tuple[str, str]] -> List[Dict]  # 3 keys per Dict
# tests = [dict(grouped) for grouped in bucket(out, 3)]  # List[Dict]

tests = list(map(dict, bucket(
	items=[
		(key.strip().split()[0], val.strip().split()[-1])
		for key, val in out
	],
	n=3)))

# correct quotes
for test in tests:
	test['correct'] = test['expected'] == test['observed']

num_correct = len(list(filter(lambda x: x['correct'] == True, tests)))
num_total = len(tests)

# if correct and total:
# 	assert num_correct == int(correct)
# 	assert num_total == int(total)

summary = {}
summary['accuracy'] = accuracy = round(num_correct / num_total, 3)

# total quotes
quotes = list(filter(lambda x: x['expected'] == 'quote', tests))
not_quotes = list(filter(lambda x: x['expected'] == 'not_quote', tests))
num_quotes, num_not_quotes = len(quotes), len(not_quotes)
assert num_not_quotes == num_total - num_quotes

correct_quotes = list(filter(lambda x: x['correct'] and x['expected'] == 'quote', tests))
TP = num_correct_quotes = len(correct_quotes)
correct_not_quotes = list(filter(lambda x: x['correct'] and x['expected'] == 'not_quote', tests))
TN = num_correct_not_quotes = true_negatives = len(correct_not_quotes)
# Recall: # TP/ TP + FN   (all positives -> denomoinator = all quotes)
summary['recall'] = recall = round(num_correct_quotes / num_quotes, 3)

# Precision: TP/ TP + FP     (of all predicted as positive, how many are true positives - true positive rate)
predicted_quotes = list(filter(lambda x: x['observed'] == 'quote', tests))
num_predicted_quotes = len(predicted_quotes)
summary['precision'] = precision = round(num_correct_quotes / num_predicted_quotes, 3)  # TP / all predicted positives

summary['f1_score'] = f1_score = 2 * ((precision * recall) / (precision + recall))
# True       quote           not_quote
# quote:      TP               FN       # recall = TP/TP + FN
# not_quote:  FP               TN

# precision = TP/TP + FP
# f1 = 2 * ((precision*recall) / (precision+recall))
FN = num_quotes - TP  # false negatives; quotes that were not identified as such
FP = num_predicted_quotes - TP  # predicted quotes that were actually not_quotes; false positives
# TP and TN known

assert TP + FN + FP + TN == len(tests)
