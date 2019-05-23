#!/usr/bin/env python3

import json
import os
import pprint as pp
from collections import OrderedDict
from pathlib import Path

from asrtoolkit.clean_formatting import clean_up

# -------------------------------------------------------------
# File Handlers
# -------------------------------------------------------------


def load_json(infile):
    return json.load(open(infile, 'r+'))


def dump_json(data, outfile):
    json.dump(data, open(outfile, 'w+'))


# -------------------------------------------------------------
# Test Results
# -------------------------------------------------------------


def missing_results(directory=None, verbose=False):
    if not directory:
        directory = os.getcwd()
    files = os.listdir(directory)
    num_strs = [file.split("_", maxsplit=1)[0] for file in files if file.endswith(".json")]
    nums = sorted([int(num.strip()) for num in num_strs])
    missing = [nums[i] for i in range(len(nums)) if nums[i] != i]
    if verbose:
        print(f"\n Total:   {len(nums)}\n Missing: {len(missing)}\n")
        print(f"\n Min test_no: {min(nums)}\n Max test_no: {max(nums)}\n")
    return nums, missing


def list_files(directory=None):
    if not directory:
        directory = os.getcwd()
    list_of_files = [file for file in os.listdir(directory) if file.endswith(".json")]
    for i in range(len(list_of_files)):
        yield f"{i}_not_quote.json"


def test_dict(result, verbose=False):
    test_no = result["test_no"]
    test_transcript = result["test_transcript"]
    expected_intent = result["expected_intent"]
    test_dict = dict(
        test_no=test_no,
        test_transcript=test_transcript,
        transcript=clean_up(test_transcript),
        expected_intent=expected_intent
    )
    if verbose:
        pp.pprint(test_dict)
    return test_dict


def pred_intent(segment, confidence_threshold=0.5):
    prob, intent_label = sorted(
        [(intent_dict["probability"], intent_dict["label"]) for intent_dict in segment["intents"]], reverse=True
    )[0]
    assert prob >= confidence_threshold  # INTENT_THRESHOLD
    return intent_label, prob


def validate(infile, test, segment):
    # need for validation
    try:
        assert test["transcript"] == segment["transcript"]
    except:
        print("\nTranscript sent to Discovery does not match transcript posted to Slack. Invalid Test\n")
        return False
    try:
        file_no = int(infile.split("_")[0])
        test_no = test["test_no"]
        assert test_no == file_no
    except AssertionError:
        print(f"\nTest Number in File Name {file_no} does not match Test Number in Result {test_no}\n")
        return False
    return True


def test_output(infile, verbose=False):
    """
	infile: str, path to JSON output from Discovery;
	return: dict:
			with y/y_pred+confidence & chat-relevant info

	note: avg_intent_preds = result["intents"]
		is avg of confidences for all segments when multiple segments present
	"""
    assert Path(infile).exists() and Path(infile).is_file()
    result = load_json(infile)

    segments = result["segments"]
    assert len(segments) == 1

    test = test_dict(result)
    test_no = test['test_no']
    expected_intent = test["expected_intent"]

    if verbose:
        print(f"\n Test Number: {test_no}\n Expected intent: {expected_intent}\n")
        pp.pprint(test)
        print(f"\n Segments: \n")
        pp.pprint(segments)

    segment = segments[0]

    is_valid = validate(infile, test, segment)
    if not is_valid:
        return False

    # intent - discovery predicted most likely + confidence
    predicted_intent, confidence = pred_intent(segment)

    out = OrderedDict(
        test_no=test["test_no"],
        transcript=test["transcript"].strip(),
        expected_intent=test["expected_intent"],
        predicted_intent=predicted_intent,
        confidence=confidence,
        correct=predicted_intent == expected_intent,
        punctuated_transcript=segment["punctuated_transcript"].strip("\n").strip(),
        speaker=segment["speakerInfo"],
        start_time=segment["startTimeSec"],  # estimate using typing speed
        end_time=segment["endTimeSec"]
    )
    return out


############################################

# prints total number of tests, number missing, min_test_no and max_test_no if verbose=True
# nums, missing = missing_results(verbose=True)

# First check for missing files
present_file_nums, missing_file_nums = missing_results(directory=None, verbose=False)
if missing_file_nums:
    print("Missing File/Test Numbers: {}".format(missing_file_nums))

# get last file/test
last_infile = present_file_nums[-1]
print(last_infile)

############################################
