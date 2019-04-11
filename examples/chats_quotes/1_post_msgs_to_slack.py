#!/usr/bin/env python3

# - quote and not_quote strings - value of `transcript` of each test in `tests.txt`

import json
import os
import requests
import sys
from pathlib import Path
from collections import defaultdict
from time import sleep


def get_test_transcripts(infile='tests.txt'):
	return [line.split(":")[1].strip() for line in Path(infile).read_text().split() if line.split(":")[0].strip() == "transcript"]


def post_message_to_slack(transcript, channel_id, slack_access_token):
	"""transcript: str; chat to post to Slack"""
	url = "https://slack.com/api/chat.postMessage"
	headers = dict(Authorization="Bearer {}".format(slack_access_token))
	payload = {
		"channel": channel_id,
		"text": transcript,
		"as_user": "true"
	}
	requests.post(url, headers=headers, json=payload)


def main(transcripts, channel_id, slack_access_token, outfile='chats_not_posted.json'):
	# transcripts = get_test_transcripts(infile)
	failed_to_post = []
	for i, transcript in enumerate(transcripts):
		try:
			post_message_to_slack(transcript, channel_id, slack_access_token)
		except:           # TODO specify except
			sleep(2)
			try:
				post_message_to_slack(transcript, channel_id, slack_access_token)
			except:
				tup = (i, transcript)
				failed_to_post.append(tup)
				print(tup)
	json.dump(dict(failed_to_post), open(outfile, 'w+'))
	return failed_to_post


if __name__ == "__main__":
	SLACK_ACCESS_TOKEN = "xoxp-4953937137-344679330118-509400138422-a20f349799113ba21f5c91e8a190cd14"
	slack_access_token = os.environ.get("SLACK_ACCESS_TOKEN", SLACK_ACCESS_TOKEN)
	channel_id = os.environ.get("CHANNEL_ID", "CEXMKJAJH")
	try:
		infile = sys.argv[1]
	except IndexError:
		infile = "tests.txt"
	try:
		outfile = sys.argv[2]
	except IndexError:
		outfile = "chats_not_posted.json"
	assert Path(infile).exists() and Path(infile).is_file()

	transcripts = get_test_transcripts(infile)
	failed_to_post = main(transcripts, channel_id, slack_access_token, outfile)
