import os
import json
from os.path import exists, join as join_path
from metrics import _compute


def get_path(data, formatted=False, dir=None):
    """
    :param data:
    :param formatted:
    :param dir:
    :return:
    """
    fmt = "formatted" if formatted else "unformatted"
    path = f'ageojo_runs/{fmt}/{data}/test_results.json'
    if not dir:
        dir = os.getcwd()
    assert exists(dir) and exists(join_path(dir, path))
    return join_path(dir, path)


def load_json(infile):
    """
    :param infile:
    :return:
    """
    return json.load(open(infile, 'r+'))


def evaluate(infile):
    """
    :param infile: str, path to json file with results from discovery
    :return dict; keys "accuracy" and "cm" with values float and list of lists (confusion matrix counts)
    """
    data = load_json(infile)
    expected = data["expected_intents"]
    observed = data["observed_intents"]
    stop = expected.index("not_quote")
    y = expected[:stop]
    y_ = observed[:stop]

    cm = _compute(y_true=y, y_pred=y_, label='quote')
    accuracy = (cm["TP"] + cm["TN"]) / len(y)
    return {"accuracy": accuracy, "cm": cm}


quotes_dir = os.getcwd()
print(quotes_dir)
# '/home/amelie/src/greenkey-discovery-sdk-private/examples/quotes'

#########################################################################
# imstrings.txt     N=23,579
#########################################################################

# FORMATTED
# formatted imstrings
infile = formatted_imstrings_results = get_path('imstrings', formatted=True, dir=quotes_dir)
formatted_imstrings = evaluate(infile)
print(formatted_imstrings)  # accuracy: 0.10%
# {
#   'accuracy': 0.0010178548708596634,
#   'cm': {
#       'TP': 24,
#       'FN': 23555,
#       'FP': 0,
#       'TN': 0
#   }
# }

# UNFORMATTED
# unformatted imstrings (clean_up function)
infile = unformatted_imstrings_results = get_path('imstrings', formatted=False, dir=quotes_dir)
unformatted_imstrings = evaluate(infile)
print(unformatted_imstrings)  # accuracy = 99.57%
# {
#   'accuracy': 0.9957165274184656,
#   'cm': {
#       'TP': 23478,
#       'FN': 101,
#       'FP': 0,
#       'TN': 0
#   }
# }

#########################################################################
# security_db.txt     N=394
#########################################################################
# FORMATTED
# formatted security_db
infile = formatted_security_db_results = get_path('security_db', formatted=True, dir=quotes_dir)
formatted_security = evaluate(infile=infile)
print(formatted_security)  # accuracy = 0.00%
# {
#   'accuracy': 0.0,
#   'cm': {
#       'TP': 0,
#       'FN': 394,
#       'FP': 0,
#       'TN': 0
#   }
# }

# UNFORMATTED
# unformatted security_db via clean_up function
infile = unformatted_security_db_results = get_path('security_db', formatted=False, dir=quotes_dir)
unformatted_security_db = evaluate(infile)
print(unformatted_security_db)  # accuracy = 5.58%
# {
#   'accuracy': 0.05583756345177665,
#   'cm': {
#       'FN': 372,
#       'FP': 0,
#       'TN': 0,
#       'TP': 22
#   }
# }

infile = unformatted_security_db_round3_results = get_path('security_round3', formatted=False, dir=quotes_dir)
unformatted_security_round3 = evaluate(infile)
print(unformatted_security_round3)  # accuracy = 97.46%
# {
#   'accuracy': 0.9746192893401016,
#   'cm': {
#       'TP': 384,
#       'FN': 10,
#       'FP': 0,
#       'TN': 0
#   }
# }

##############################
# #######################################
# (ins)amelie@amu:~/src/gree...es/equal_sample_size$ wc -l *
#     5238 formatted_test_not_quotes_10.txt
#    47131 formatted_train_not_quotes_90.txt
#    58443 formatted_train_quotes_90.txt
#    23578 imstrings.txt
#      394 security_db.txt
#     5239 unformatted_test_not_quotes_10.txt
#    47146 unformatted_train_not_quotes_90.txt
#    58543 unformatted_train_quotes_90.txt
#   245712 total
#####################################################################

# #####################################################################
# # RUNS - All QUOTES
# ######################################################################
#
# # Formatted Runs
# # (no modification Except: security_db_round3 --> round long numbers
# # 23,578
# imstrings = 'imstrings.txt'
#
# # 394
# security = 'security_db.txt'
#
# # Unformatted RUNs
# # - clean_up(s)
# # -------------------------------------------------------------------------
# # ALL QUOTES
#
# # 23,578
# unformatted_imstrings = "unformatted_imstrings.txt"
#
# # 394
# unformatted_security = "unformatted_security_db.txt"
# unformatted_security_round3 = "unformatted_security_db.txt"
#
#
# ##########################################################################
# # TEST textclassifiers
#
# #     5239 unformatted_test_not_quotes_10.txt    # clean_up(original)
# #     5238 formatted_test_not_quotes_10.txt      # formatter microservice
# ###########################################################################
#
# # ALL NOT_QUOTES
#
# # Formatted (N = 5238)      # formatter microservice
# formatted_not_quotes = "formatted_test_not_quotes_10.txt"
#
# # Unformatted (N = 5239)    # clean_up(s)
# unformatted_not_quotes = "unformatted_test_not_quotes_10.txt"
#
#
# ############################################################################
# # TRAIN textclassifiers
# #    58543 unformatted_train_quotes_90.txt         # clean_up(original)
# #    47146 unformatted_train_not_quotes_90.txt
# #
# #    58443 formatted_train_quotes_90.txt           # formatter microservice
# #    47131 formatted_train_not_quotes_90.txt
# ############################################################################
#
# #    Formatted
#
# # quotes (N = 58443)     # formatter microservice
# formatted_train_quotes = "formatted_train_quotes_90.txt"
#
# # not_quotes (N = 47131)
# formatted_train_not_quotes = "formatted_train_not_quotes_90.txt"
#
# # --------------------------------------------------------------------
#
# #    Unformatted
#
# # quotes (N = 58543)
# unformatted_train_quotes = "unformatted_train_quotes_90.txt"
#
# # not_quotes (N = 47146)
# unformatted_train_not_quotes = "unformatted_train_not_quotes_90.txt"
#
#
# ########################################################################
