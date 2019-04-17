#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path
import pandas as pd

from opts import get_env_opts

# When running must add --transcript, --test-no, --expected-intent
parser = get_env_opts()
# parser.print_help()
args = parser.parse_args()

##################################################################################


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


##################################################################################
rootdir = os.path.dirname(os.path.dirname(os.getcwd()))
sdk_root_dir = rootdir
root_dir = os.getcwd()
quotes_dir = Path(sdk_root_dir) / 'examples' / 'chat_quotes'
quotes_dir.exists() and quotes_dir.is_dir()

# # Tests.txt
# test_file = "tests.txt"
# test_file = quotes_dir / test_file
# assert test_file.exists() and test_file.is_file()
# tests = load_tests(test_file=test_file)
# # list(tests)[0]

##############
# Quotes
quotes_test = 'test_quotes_10.txt'
quotes_test = quotes_dir / quotes_test
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
# 6505 -> 6141   after drop duplicaates

################
# Not_Quotes
not_quotes_test = 'test_not_quotes_10.txt'
not_quotes_test = quotes_dir / not_quotes_test
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

empty_dict_array = [{} for i in range(df.shape[0])]
df["posted_to_slack_json"] = empty_dict_array     #df.transcript.apply(post_message_to_slack)
df["is_posted_to_slack"] = 0                      #df.posted_to_slack_json.apply(validate_post_message)
df["chat_segments"] = empty_dict_array            #df.transcript.apply(fetch_chats_via_chat_slack)
df['discovery_segments'] = empty_dict_array      #df.chat_segments.apply(extract_intents_via_discovery)


# df.shape
# df.columns
# df.head()
first = df.iloc[0]
last = df.iloc[11379]
##############################################################################################################################################

def run_main(test_no, transcript, expected_intent):
  cmd = "python pipe_transcript.py --test-no={} --transcript='{}' --expected-intent={}".format(test_no,
                                                                                             transcript,
                                                                                             expected_intent)
  return subprocess.call(cmd, shell=True)

##############################################################################################################################################

if not os.path.basename("chat_quotes"):
	os.chdir(quotes_dir)

start=0
end=10

results = []
for i, row in enumerate(df[start:end].itertuples(name="Chat"), start=start):
	print()
	Chat = row
	#NOTE: out is 1 if succeeded posting to chat_slack, 0 if it failed
	out = run_main(Chat.Index, Chat.transcript, Chat.expected_intent)
	results.append((Chat, out))


	# Chat.posted_to_slack_json = posted_message = vadlidate_post_message(
	# 	post_message_to_slack(transcript=Chat.transcript)
	# )
	# Chat.chat_segments = fetch_chats_via_chat_slack(Chat.posted_slack_json)
	# Chat.discovery_segments = extract_intents_via_discovery(Chat.chat_segments)




########################################################################
#
# from pipe_transcript import post_message_to_slack
# ########################################################################
# # SLACK_API_URL
# SLACK_ACCESS_TOKEN = "xoxp-4953937137-344679330118-509400138422-a20f349799113ba21f5c91e8a190cd14"
# slack_access_token = os.environ.get("SLACK_ACCESS_TOKEN", SLACK_ACCESS_TOKEN)
#
# CHANNEL_NAME = channel_name = os.environ.get("CHANNEL_NAME", "ageojo_test")
# CHANNEL_ID = channel_id = os.environ.get("CHANNEL_ID", "CEXMKJAJH")
#
# CHAT_SLACK_PORT, DISCOVERY_PORT = 8005, 8006
# chat_slack_url = "http://localhost:{}/process".format(CHAT_SLACK_PORT)
# discovery_url = "http://localhost:{}/process".format(DISCOVERY_PORT)
#
# MAX_TRIES = 5
# TIMEOUT = 10
# DELAY = 2
#
# import requests
# import time
#
# # Generic Post - STEP 0
# def post(url, headers, payload, max_tries=MAX_TRIES, timeout=TIMEOUT, delay=DELAY):
# 	""" post to url """
# 	for i in range(max_tries):
# 		# loop request at most max_tries; return if succeed
# 		r = requests.post(url, headers=headers, json=payload, timeout=timeout)
# 		try:
# 			# r = requests.post(url, headers=headers, json=payload, timeout=args.timeout)
# 			if r.status_code == 200:
# 				return r.json()
# 		except:
# 			print(r.status_code)
# 			time.sleep(delay + 1)  # increment delay with each post
# 			continue
# 		return {}
#
# # TODO cange back to args.channel_id and args.slack_access_token
# def post_message_to_slack(transcript, channel_id=CHANNEL_ID, slack_access_token=SLACK_ACCESS_TOKEN):
# 	return post_message_to_slack(transcript, channel_id, slack_access_token)
# 	# is_success = validate_post_message(post_message_to_slack)
# 	# posted_json, is_success
#
# def validate_post_message(posted_json):
#     if posted_json and posted_json["ok"] is True:
#         return True
#     return False


df.head()
# df["post_message"] = df.transcript.apply()
# df['posted_message_json'] = df.transcript.apply(post_message)
# df["posted_message_success"] = df.posted_message_json.apply(validate_post_message)
