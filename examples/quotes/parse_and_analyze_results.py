import os
from os.path import join as join_path, basename
import json
import csv
import itertools

root_dir = os.getcwd()
assert basename(root_dir) == 'greenkey-discovery-sdk-private'

quotes_dir = join_path(root_dir, 'examples', 'quotes')

OUTPUT_DIR =  quotes_dir


def bucket(items, n):
  """
  Breaks items into a list of lists of n items each. Order is retained:
  >>> bucket([1, 2, 3, 4, 5, 6], 2)
  [[1, 2], [3, 4], [5, 6]]
  """
  bucket = []
  start = 0
  sub = items[start:start + n]
  while sub:
    bucket.append(sub)
    start += n
    sub = items[start:start + n]
  return bucket


def flatten_one_level(lists):
  return itertools.chain.from_iterable(lists)


def csv_write(output_lines, outfile):
  out = os.path.join(OUTPUT_DIR, outfile)
  with open(out, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(output_lines)

########################
"""
======
 Test Number: 0
======
Testing: quotes_not_quotes 0

 Expected Intent: quote 
 Observed Intent: quote

Test passed
---

======
"""
import re
root_dir = os.getcwd()
assert basename(root_dir) == 'greenkey-discovery-sdk-private'
quotes_dir = join_path(root_dir, 'examples', 'quotes')
os.listdir(quotes_dir)
# infile = 'results_quotes.txt'
# infile = join_path(quotes_dir,'results_quotes.txt')

def test_accuracy(infile, accuracy):
  with open(infile, 'r+', encoding='utf-8') as f:
    list_of_lines = f.readlines()
    # last_line = list_of_lines[-1].replace("\n", '').strip()
    last_line = '(11688 / 11745) tests passed in 187s'
    try:
      correct, total, time = re.findall("\d+", last_line)
    except ValueError:
      print("Reported Accuracy and Time Unknown")
    assert correct/total == accuracy
    return {'num_correct':correct, 'num_tests': total, 'accuracy': correct/total}


OUTPUT_DIR = quotes_dir

infile = 'test_results.txt'
inpath = join_path(OUTPUT_DIR, infile)


with open(inpath, 'r+', encoding='utf-8') as f:
  correct, total, time = re.findall('\d+', f.read())[-3:]

# import subprocess
# last_line = subprocess.call("tail -1 {}".format(infile), shell=True)

with open(inpath, 'r+', encoding='utf-8') as f:
  list_of_lines = f.readlines()
  last_line = list_of_lines[-1].replace("\n", '').strip()
  try:
    correct, total, time = re.findall("\d+", list_of_lines[-1])
  except ValueError:
    print("Reported Accuracy and Time Unknown")
    correct, total, time = 0,0,0

  out = [tuple(line.strip().lower().split(":")) for line in list_of_lines if line.strip() and line.split(":")[0].split()[0].lower().strip() in ['testing', 'expected', 'observed']]
  # print(out[:10])

# List[Tuple[str, str]] -> List[Dict]  # 3 keys per Dict
# tests = [dict(grouped) for grouped in bucket(out, 3)]  # List[Dict]

tests = list(map(dict, bucket(
  items=[
    (key.strip().split()[0], val.strip().split()[-1])
    for key, val in out
  ],
  n=3)))

assert not len(tests) % 3
test_n_max = int(tests[-1]['testing'])+1  # start=0
assert test_n_max == len(tests)


import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame(tests)
df.head()

df['correct'] = df['expected'] == df['observed']
df['y_true'] = df.expected.apply(lambda x: 1 if x == 'quote' else 0)
df['y_pred'] = df.observed.apply(lambda x: 1 if x == 'quote' else 0)
y_true, y_pred = df.y_true, df.y_pred


from pandas_ml import ConfusionMatrix
confusion_matrix = ConfusionMatrix(y_true, y_pred)
print("Confusion matrix:\n%s" % confusion_matrix)

# Produce Plot of Confusion Matrix
confusion_matrix.plot()
plt.title('Confusion Matrix: Quotes Classifier')
plt.show()

# normalized matrix
confusion_matrix.plot(normalized=True)
plt.title('Normalized Confusion Matrix: Quotes Classifier')
plt.show()

# print(confusion_matrix.stats())
import pprint as pp
pp.pprint(confusion_matrix.stats())

# Save Summary Stats
outfile = 'cm_summary.json'
outpath = join_path(quotes_dir, outfile)

cm_stats = confusion_matrix.stats()

# Need to do this or get: TypeError: Object of type 'int64' is not JSON serializable
# or if do below without casting to str and float -> something about
d = {}
for k, v in cm_stats.items():
  d[str(k)] = float(v)
print(d)
json.dump(d, open(outpath, 'w+'))

# cannot pickle with cm_stats or d  -> TypeError: write() argument must be str, not bytes




####################################################################################
# SUMMARY AND COMPUTE DIRECTLY
# save stats as json
####################################################################################

# # compute accuracy
for test in tests:
  test['correct'] = test['expected'] == test['observed']

num_correct = len(list(filter(lambda x: x['correct'] == True, tests)))
num_total = len(tests)

if correct and total:
  assert num_correct == int(correct)
  assert num_total == int(total)

summary = {}
summary['accuracy'] = accuracy = round(num_correct/num_total, 3)

# total quotes
quotes = list(filter(lambda x: x['expected'] == 'quote', tests))
not_quotes = list(filter(lambda x: x['expected'] == 'not_quote', tests))
num_quotes, num_not_quotes = len(quotes), len(not_quotes)
assert num_not_quotes == num_total - num_quotes

# correct quotes
correct_quotes = list(filter(lambda x: x['correct'] and x['expected']=='quote', tests))
TP = num_correct_quotes = len(correct_quotes)
correct_not_quotes = list(filter(lambda x: x['correct'] and x['expected']=='not_quote', tests))
TN = num_correct_not_quotes = true_negatives = len(correct_not_quotes)
# Recall: # TP/ TP + FN   (all positives -> denomoinator = all quotes)
summary['recall'] = recall = round(num_correct_quotes/num_quotes, 3)

# Precision: TP/ TP + FP     (of all predicted as positive, how many are true positives - true positive rate)
predicted_quotes = list(filter(lambda x: x['observed'] == 'quote', tests))
num_predicted_quotes = len(predicted_quotes)
summary['precision'] = precision = round(num_correct_quotes/num_predicted_quotes, 3)      # TP / all predicted positives

summary['f1_score'] = f1_score = 2*((precision*recall)/(precision+recall))
# True       quote           not_quote
# quote:      TP               FN       # recall = TP/TP + FN
# not_quote:  FP               TN

# precision = TP/TP + FP
# f1 = 2 * ((precision*recall) / (precision+recall))
FN = num_quotes-TP      # false negatives; quotes that were not identified as such
FP = num_predicted_quotes - TP     # predicted quotes that were actually not_quotes; false positives
# TP and TN known

assert TP + FN + FP + TN == len(tests)

labels = [
  ['pred_quotes', 'pred_not_quotes'],
  ['true_quotes', 'true_not_quotes']
]
# labels = ['quotes', 'not_quotes']
cm = my_confusion_matrix = [
  [TP, FN],
  [FP, TN]
]

q_count = TP+FN
not_q_count = FP+TN
normalized_confusion_matrix = [
  [round(TP/q_count,3), round(FN/q_count, 3)],
  [round(FP/not_q_count,3), round(TN/not_q_count,3)]
]
print(normalized_confusion_matrix)
# would need to np.reshape(2,2)
# normalized_matrix = [round(cell, 3) for row in normalized_confusion_matrix for cell in row]

summary['normalized_cm'] = normalized_confusion_matrix
summary['cm'] = confusion_matrix
summary['TP'], summary['FN'], summary['FP'], summary['TN'] = TP, FN, FP, TN

# Save Summary Stats
outfile = 'summary.json'
outpath = join_path(quotes_dir, outfile)
print("\n", summary.keys(), "\n")
json.dump(summary, open(outpath, 'w+'))


####################################################################################
# PLOT confusion matrix & normalized
####################################################################################
import matplotlib.pyplot as plt
plt.matshow(confusion_matrix)

plt.matshow(normalized_confusion_matrix)
plt.colorbar()