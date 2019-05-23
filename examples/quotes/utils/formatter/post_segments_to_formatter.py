import requests
import os
import sys
import json
import time
import pprint as pp
from collections import defaultdict
from pathlib import Path
from os.path import dirname, basename, exists, join as join_path

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Tested and verified with:
#infile = "0_quote.json"
#outfile = "test_formatted_quotes_10.txt"
#data = json.load(open(infile, 'r+'))
# out = post_to_formatter(data)
# pp.pprint(out)
############################################

#INPUT_DIR = sys.argv[1]
#OUTPUT_DIR = sys.argv[2]

###################################
import pprint as pp

from collections import OrderedDict
from asrtoolkit.data_structures.segment import segment as Segment

DELAY = 10
RETRIES = max_tries = 5
FORMATTER_PORT = formatter_port = 8005
print(formatter_port)

quotes_file = 'test_quotes_10.txt'
not_quotes_file = 'test_not_quotes_10.txt'


def post_to_formatter(transcript):
    data = {"transcript": transcript}
    headers = {"Content-type": "application/json"}
    url = "http://localhost:{}/process".format(FORMATTER_PORT)

    for i in range(RETRIES):
        r = requests.post(url, headers=headers, json=data, timeout=10)
        if r.status_code == 200:
            return r.json()
        time.sleep(2)
    return {}


def load_lines(infile):
    """
  Reads in text file and returns List[str], each str is a line
  """
    with open(infile) as f:
        return [line.strip() for line in f.readlines() if line.strip()]


root_dir = os.getcwd()
assert basename(root_dir) == 'greenkey-discovery-sdk-private'
directory = join_path(root_dir, 'examples/chats_quotes')

# QUOTES : Load unformatted test data
infile = join_path(directory, quotes_file)
exists(infile)
quotes_file = load_lines(infile=join_path(directory, infile))

START = 0
END = 1

batch = quotes_file[START:END]


def format(batch):
    segment_list = []
    for i, line in enumerate(batch, start=START):
        formatted = post_to_formatter(transcript=line)
        if not formatted:
            logger.error(f"Failed to Format Transcript {i}: {line}")
        formatted["transcript_id"] = i
        segment_list.append(Segment(formatted))
        if i % 50 == 0:
            time.sleep(DELAY)
    return segment_list


def print_seg(segment):
    pp.pprint(segment.__dict__)


####################################
first = format(batch)
# first[0].__dict__()
print(first[0])
pp.pprint(first[0].__dict__)
#################################################

START = 0
END = 500
first_500 = format(batch=quotes_file[START:END])

batch = quotes_file[START:END]
first_500 = format(batch)

START = 500
END = 1000
second_500_to_1000 = format(batch=quotes_file[START:END])
len(second_500_to_1000)

START = 1000
END = 2000
third_1000_to_2000 = format(batch=quotes_file[START:END])
len(third_1000_to_2000)

START = 2000
END = 4000
fourth_2000_to_4000 = format(batch=quotes_file[START:END])
len(fourth_2000_to_4000)

len(quotes_file)

quote_segments = first_500 + second_500_to_1000 + third_1000_to_2000 + fourth_2000_to_4000
len(quote_segments)
# 4000

len(quotes_file)
# 6505

START, END = 4000, 6505
last_4000_to_6505 = format(batch=quotes_file[START:END])
len(last_4000_to_6505)

quote_segments = (first_500 + second_500_to_1000 + third_1000_to_2000 + fourth_2000_to_4000 + last_4000_to_6505)

assert len(quote_segments) == len(quotes_file)


# NOT QUOTES : Load unformatted test data
def format_not_quotes(directory, not_quotes_file):
    infile = join_path(directory, not_quotes_file)
    assert exists(infile)
    not_quotes_lines = load_lines(infile=join_path(directory, infile))
    print(not_quotes_lines)
    not_quote_segments = []
    for START, END in [[0, 2000], [2000, 4000], [4000, 5239]]:
        print("\n---------------------------------------\n")
        print("\nStart: {} and End: {}\n".format(START, END))
        not_quotes = format(batch=not_quotes_lines[START:END])
        not_quote_segments = not_quote_segments + not_quotes
        print("\n---------------------------------------\n")
    return not_quote_segments


print("\n\nFormatting not_quote lines --> Segments\n")
not_quote_segments = format_not_quotes(directory, not_quotes_file)
assert len(not_quote_segments) == len(load_lines(infile=join_path(directory, not_quotes_file)))

# Save all segments - contain formatted and unformatted test data (10% of original quote and not_quote data)
# note: unformatted is raw_data --> NOT clean_up(raw_transcript), which is what it should be
import pickle
outfile = open(join_path(directory, 'test_segments.pkl'), 'wb+')
pickle.dump([quote_segments, not_quote_segments], outfile)

#
# def write_intent_test_txt_files(intent,infile=None, data=None, test_size=10):
#   if infile:
#     quote_segments, not_quote_segments = pickle.load(open(infile), 'wb+')
#
# ##############################################################
# from asrtoolkit.clean_formatting import clean_up
# # Add expected intent attribute
# seg.__setattr__("exected_intent_test", 'quote')
# raw_transcript = seg.transcript
# seg.__setattr__('raw_transcript', raw_transcript)
# seg.__setattr__("transcript", clean_up(raw_transcript))
# print_seg(seg)
# seg.__dict__.keys()
###############################################################
pickled_file = join_path(directory, 'test_segments.pkl')
assert exists(pickled_file)


def load_pickle(pickled_file):
    return pickle.load(open(pickled_file, 'wb+'))


# data = load_lines(pickled_file)
# pickled_quote_segments, pickled_not_quote_segments = pickle.load(open(pickled_file, 'wb+'))
#
#directory: examples/chats_quotes
quotes_outfile = join_path(directory, 'formatted_test_quotes_10.txt')
not_quotes_outfile = join_path(directory, 'formatted_test_not_quotes_10.txt')


def update_segment_attributes(segment, intent, formatted=True):
    raw_transcript = segment.transcript
    unformatted_transcript = clean_up(raw_transcript)
    segment.__setattr__('raw_transcript', raw_transcript)
    segment.__setattr__('unformatted_transcript', unformatted_transcript)
    # formatted_transcript stays put
    # set 'transcript' to formatted_transcript or unformatted_transcript depending on value of formatted
    selected_transcript = segment.formatted_transcript if formatted else segment.unformatted_transcript
    segment.__setattr__('transcript', selected_transcript)
    segment.__setattr__('intent', intent)
    return segment


def update_all_segments(segments_list, intent, formatted=True):
    updated = []
    failed = []
    for segment in segments_list:
        if not hasattr(segment, 'unformatted_transcript') or not hasattr(segment, 'raw_transcript'):
            try:
                updated_segment = update_segment_attributes(segment, intent, formatted)
                updated.append(updated_segment)
            except Exception as e:
                print(e)
                print_seg(segment)
                print()
                failed.append(segment)
        else:
            updated.append(segment)
    return updated, failed


# Update segments - correct attribute labeling & run clean_up to get unformatted version of raw
quote_segments_updated = update_all_segments(quote_segments, intent='quote', formatted=True)

not_quote_segments_updated, failed_update = update_all_segments(not_quote_segments, intent='not_quote', formatted=True)
len(not_quote_segments), len(
    not_quote_segments_updated
)  # one of the not_quote_segments did not have any text so it is effectively removed during update


def write_intent_test_file(directory, segments, intent, test_size=10, formatted=True):
    # Outfile
    prefix = "formatted" if formatted else "unformatted"
    filename = f"{prefix}_test_{intent}_{test_size}.txt"
    outfile = join_path(directory, filename)

    # Open text file to write `{formatted}_tests_{intent}_{test_size}.txt`
    fw = open(outfile, 'w+')

    segment_dict_list = []
    for segment in segments:  # segments have 'text' and 'formatted_text' but format_segments produces dict with 'transcript' and 'punctuated_transcript'
        try:
            # write line
            line = f"{segment.transcript}\n"
            fw.write(line)

            # transform to dict and append
            segment_dict_list.append(segment.__dict__)
        except Exception as e:
            print("\nError: Failed to write ine {segment.transcript_id}: {segment.transcript}\n Error Details: {e}\n")
    # print("\nSuccess! Wrote Text File\n")
    return segment_dict_list


basename(directory)  # chats_quotes

# writes intent specific test file (.txt)
# formatted_test_quotes_10.txt
write_intent_test_file(directory, segments=quote_segments_updated, intent='quote', test_size=10, formatted=True)

# formatted_test_quotes_10.txt
write_intent_test_file(directory, segments=not_quote_segments_updated, intent='not_quote', test_size=10, formatted=True)
