#!/usr/bin/env python3

import os
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import sys
from opts import get_env_opts

START = 0
END = 10


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


def load_tests(test_file):
    """
 reads in tests.txt and returns an iterator of dicts corresponding to each test
 :param test_file:
 :return:
 """
    test_data = Path(test_file).read_text().splitlines()
    tests = [
        line.split(":", maxsplit=1)
        # line.strip().split(":", maaxsplit) #[1].strip()  ??
        for line in test_data
        if line.strip() and line.split(":")[0].strip() in ['test', 'transcript', 'intent']
    ]
    return map(dict, bucket(tests, 3))


def dump_json(data, outfile):
    json.dump(data, open(outfile, 'w+'))


##################################################################################
# rootdir = os.path.dirname(os.path.dirname(os.getcwd()))
##sdk_root_dir = rootdir
sdk_root_dir = os.getcwd()
quotes_dir = Path(sdk_root_dir) / 'examples' / 'chats_quotes'
quotes_dir.exists() and quotes_dir.is_dir()
os.chdir(quotes_dir)


# # Tests.txt
# test_file = "tests.txt"
# test_file = quotes_dir / test_file
# assert test_file.exists() and test_file.is_file()
# tests = load_tests(test_file=test_file)
# # list(tests)[0]

##############
# Quotes
quotes_test = 'test_quotes_10.txt'
quotes_test = Path(quotes_test)
# quotes_test = quotes_dir / quotes_test
assert quotes_test.exists() and quotes_test.is_file()

test_quotes = quotes_test.read_text().strip().splitlines()
# test_quotes[:10]
# len(test_quotes)

quotes_df = pd.DataFrame(data=test_quotes, columns=["transcript"])  # , columns="quotes", index=range(len(test_quotes)))
quotes_df.drop_duplicates(inplace=True)
quotes_df['is_quote'] = 1
quotes_df["expected_intent"] = "quote"
# quotes_df.shape
# quotes_df.head()
# 6505 -> 6130   after drop duplicaates

################
# Not_Quotes
not_quotes_test = 'test_not_quotes_10.txt'
not_quotes_test = Path(not_quotes_test)
# not_quotes_test = quotes_dir / not_quotes_test
not_quotes_test.exists() and not_quotes_test.is_file()
test_not_quotes = not_quotes_test.read_text().strip().splitlines()
# test_not_quotes[:10]
# len(test_not_quotes)

not_quotes_df = pd.DataFrame(data=test_not_quotes, columns=["transcript"])
not_quotes_df.drop_duplicates(inplace=True)
not_quotes_df['is_quote'] = 0
not_quotes_df["expected_intent"] = "not_quote"
# not_quotes_df.shape
# not_quotes_df.head()
# 5239  no duplicate quotes

#####################
# df = pd.concat([quotes_df, not_quotes_df])
# df['formatted'] = 0

# df.head()
# df.columns
#######################################################################
df = pd.concat([quotes_df, not_quotes_df])
df['formatted'] = 0
df['test_no'] = df.index.values
# df.shape
empty_dict_array = [{} for i in range(df.shape[0])]
df["posted_to_slack_json"] = empty_dict_array  # df.transcript.apply(post_message_to_slack)
df["is_posted_to_slack"] = 0  # df.posted_to_slack_json.apply(validate_post_message)
df["chat_segments"] = empty_dict_array  # df.transcript.apply(fetch_chats_via_chat_slack)
df['discovery_segments'] = empty_dict_array  # df.chat_segments.apply(extract_intents_via_discovery)

# Save DataFrame with all tests loaded
dump_json(data=df.to_json(orient="records"), outfile="df_test_data_4.20.18.json")

##############################################################################################################################################

# if not os.path.basename("chat_quotes"):
#	os.chdir(quotes_dir)

# start=START
# end=END

# results = []
# for i, row in enumerate(df[start:end].itertuples(name="Chat"), start=start):
#	print()
#	Chat = row
#	#NOTE: out is 1 if succeeded posting to chat_slack, 0 if it failed
#	out = run_main(Chat.Index, Chat.transcript, Chat.expected_intent)
#	results.append((Chat, out))

# Chat.posted_to_slack_json = posted_message = vadlidate_post_message(
# 	post_message_to_slack(transcript=Chat.transcript)
# )
# Chat.chat_segments = fetch_chats_via_chat_slack(Chat.posted_slack_json)
# Chat.discovery_segments = extract_intents_via_discovery(Chat.chat_segments)

########################################################################
#
# from pipe_transcript import post_message_to_slack
# ########################################################################

# SLACK_API_URL
SLACK_ACCESS_TOKEN = "xoxp-4953937137-344679330118-509400138422-a20f349799113ba21f5c91e8a190cd14"
slack_access_token = os.environ.get("SLACK_ACCESS_TOKEN", SLACK_ACCESS_TOKEN)
#
CHANNEL_NAME = channel_name = os.environ.get("CHANNEL_NAME", "ageojo_test")
CHANNEL_ID = channel_id = os.environ.get("CHANNEL_ID", "CEXMKJAJH")
#
SERVICE_NAME = service_name = os.environ.get("SERVICE_NAME", "slack")
CHAT_SLACK_PORT, DISCOVERY_PORT = 8005, 8006
chat_slack_url = "http://localhost:{}/process".format(CHAT_SLACK_PORT)
discovery_url = "http://localhost:{}/process".format(DISCOVERY_PORT)
#
MAX_TRIES = 5
TIMEOUT = 10
DELAY = 2
#
MAX_PAGES = 1
COUNT = 1

LATEST_TS = time_now = datetime.now().timestamp()


def post_to_chat_slack(transcript):
    params = dict(
        channel_name=CHANNEL_NAME,
        channel_id=CHANNEL_ID,
        count=COUNT,
        max_pages=MAX_PAGES,
        latest_ts=datetime.now().timestamp(),
        transcript=transcript
    )
    request_dict = dict(service_name=SERVICE_NAME, params=params)
    return request_dict


if __name__ == "__main__":
    from pipe_transcript import main

    parser = get_env_opts()
    args = parser.parse_args()

    for i in range(START, END):
        print("\n-------------------------------------\n")
        print("Test Number {}", format(i))
        test_no = i
        transcript = df.iloc[i]['transcript']
        expected_intent = df.iloc[i]["expected_intent"]
        test_dict = dict(test_no=test_no, transcript=transcript, expected_intent=expected_intent)

        posted_json, chat_segments, discovery_segments = main(
            request_dict=post_to_chat_slack(transcript),
            test_dict=test_dict,
            outfile=None,
            chat_slack_port=CHAT_SLACK_PORT,
            discovery_port=DISCOVERY_PORT
        )
        df["posted_to_slack_json"].iloc[i] = posted_json
        df.iloc[i]["chat_segments"] = chat_segments
        df.iloc[i]["discovery_segments"] = discovery_segments

# Save Batch
dump_json(data=df.to_json(orient="records"), outfile="df_test_data_{}_{}.json".format(START, END))

        # posted_json = post_message_to_slack(transcript)
        # message_was_posted = posted_json and posted_json["ok"] is True and posted_json["message"][
        #   "text"] == transcript


###########
# for i in range(0):
#   df.iloc[i]["test_no"] = i
#
#   try:
#     transcript = df.iloc[i]["transcript"]
#     posted_json = post_message_to_slack(transcript)
#     df.iloc[i]["posted_to_slack_json"] = posted_json
#     df.iloc[i]['is_posted_to_slack'] = validate_post_message(posted_json) #df.transcript.apply(post_message)
#
#     #if df.iloc[i]["is_posted_to_slack"]:
#     params = dict(channel_name=CHANNEL_NAME, channel_id=CHANNEL_ID, count=COUNT, max_pages=MAX_PAGES, latest_ts=datetime.time().timestamp())
#     request_dict = dict(service_type="slack", params=params)
#     chat_segments = fetch_chats_via_chat_slack(request_dict)
#     if chat_segments:
#       chat_segments["transcripts_match"] =  transcript==chat_segments["segments"]["transcript"]
#     df.iloc[i]["chat_segments"] = chat_segments
#
#     discovery_segments = extract_intents_via_discovery(chat_segments)
#     df.iloc[i]["discovery_segments"] = discovery_segments
#     print("\nFinal Row {}: {}\n".format(i, d.iloc[i]))
#   except Exception as e:
#     print("\nFailed to complete test {} \n Exception: {}".format(i, e))
#     continue
