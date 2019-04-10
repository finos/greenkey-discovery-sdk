#!/usr/bin/env python3

# - quote and not_quote strings - value of `transcript` of each test in `tests.txt`

import json
import os
import requests
import sys
from pathlib import Path
from collections import defaultdict
from time import sleep

# SLACK_API_URL = "https://slack.com/api"
# SLACK_ACCESS_TOKEN = "xoxp-4953937137-344679330118-509400138422-a20f349799113ba21f5c91e8a190cd14"
# #
# # SERVICE_TYPE = "slack"
# # CHANNEL_NAME = "ageojo_test"
# CHANNEL_ID = "CEXMKJAJH"  # channel id corresponding to #ageojo_test
# #
# infile = 'tests.txt'
# tests = Path(infile).read_text().splitlines()
# transcripts = [line.split(":")[1].strip() for line in tests if line.split(":")[0].strip() == "transcript"]
# #
# # # auth_headers = dict(("Authorization: Bearer {}".format(SLACK_ACCESS_TOKEN)), 'Content-type: application/json'})
# # # url = f"{SLACK_API_URL}/chat.postMessage"
# headers = defaultdict()
# headers["Authorization"] = "Bearer {}".format(SLACK_ACCESS_TOKEN)
# URL = url = "https://slack.com/api/chat.postMessage"


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




# 	not_sent_transcripts = [transcripts[num] for num in not_posted]
# 	outfile = '2_chats_not_posted.json'
# 	main(not_sent_transcripts, channel_id, slack_access_token, outfile)
# # ^ file is empty so remaining chats were successfully posted


	# transcripts = get_test_transcripts(infile)
	# failed_to_post = []
	# for i, transcript in enumerate(transcripts):
	# 	try:
	# 		post_message_to_slack(transcript)
	# 	except:
	# 		failed_to_post.append((i, transcript))
	#
	# json.dump(dict(failed_to_post), open('chats_not_posted.json', 'w+'))



d = defaultdict(dict)
for num in not_posted:
	d[num] = transcripts[num]
json.dump(dict(d), open('1_chats_not_posted.json', 'w+'))

def post_chats_to_slack(list_of_chats):
	"""List[str], each str is a chat to post to Slack"""
	headers = defaultdict()
	headers["Authorization"] = "Bearer {}".format(SLACK_ACCESS_TOKEN)
	URL = "https://slack.com/api/chat.postMessage"

	not_posted = []
	for i, chat in enumerate(list_of_chats):
		# print("{}: {}".format(i, transcript))
		try:
			post_message_to_slack(transcript)
		# ToDo add sleep time - avoid API timeout limits
		except:
			# print(i)
			not_posted.append(i)
	return not_posted


# def main(infile):
# 	"""
# 	:param infile: str, file to read transcripts (chats) to post to Slack
# 	:return:
# 	"""
# 	tests = Path(infile).read_text().splitlines()
# 	transcripts = [line.split(":")[1].strip() for line in tests if line.split(":")[0].strip() == "transcript"]
#
# 	# url = f"{SLACK_API_URL}/chat.postMessage"
# 	headers = defaultdict()
# 	headers["Authorization"] = "Bearer {}".format(SLACK_ACCESS_TOKEN)
# 	URL = "https://slack.com/api/chat.postMessage"
# 	not_posted = post_chats_to_slack(transcripts)
# 	return not_posted


if __name__ == "__main__":
	SLACK_API_URL = "https://slack.com/api"
	SLACK_ACCESS_TOKEN = "xoxp-4953937137-344679330118-509400138422-a20f349799113ba21f5c91e8a190cd14"

	# SERVICE_TYPE = "slack"
	# CHANNEL_NAME = "ageojo_test"
	CHANNEL_ID = "CEXMKJAJH"  # channel id corresponding to #ageojo_test

	infile = 'tests.txt'

	list_of_chats = [
		line.split(":")[1].strip()
		for line in Path(infile).read_text().split()
		if line.split(":")[0].strip() == "transcript"
	]

	post_chats_to_slack(list_of_chats)

# main(infile)

###########################################################
not_posted = []
for i, transcript in enumerate(transcripts[1:]):
	print("{}: {}".format(i, transcript))
	try:
		post_transcript(transcript)
	except:
		print(i)
		not_posted.append(i)


###########################################################


# def get_test_chats(infile='tests.txt'):
# 	"""
# 	:param: infile: str; path to `tests.txt` file (see discovery sdk)
# 	:return: Tuple(List[str], List[str])
# 		List of chats (transcripts to post to Slack)
# 		List of intents corresponding to each chat
# 	"""
#
# 	def _get_text(key):
# 		return [line.split(":")[1].strip() for line in tests if line.split(":")[0].strip() == key]
#
# 	tests = Path(infile).read_text().splitlines()
# 	return _get_text("transcript"), _get_text("intent")


def post_message_to_slack(channel_id, text, as_user="true"):
	"""
	post a message to a slack channel (as user - not bot; subtype='bot-?')
			post_to_slack_url = "https://slack.com/api/chat.postMessage
	"""
	auth_headers = dict(Authorization=f"Bearer {SLACK_ACCESS_TOKEN}")

	url = f"{SLACK_API_URL}/chat.postMessage"

	data = {
		"channel": channel_id,
		"text": text,
		"as_user": as_user
	}

	r = requests.post(url, headers=auth_headers, json=data)
	return json.loads(r.text)

# def post_test_chats_to_slack(channel_id="CEXMKJAJH", infile='tests.txt', as_user="true"):
# 	"""
# 	:param: chats; List[Dict]
# 	:return: List[Dict]
# 		timestamp, channel_id, text, intent, and response returned from Slack API when posted chat transcript
# 		channel_name='ageojo_test'  -> channel id = "CEXMKJAJH"
# 	"""
# 	list_of_chats, list_of_intents = get_test_chats(infile)  # infile = tests.txt
#
# 	# make sure chat & intent are values of "transcript" and  "intent" for a given test
# 	tests = []
#
# 	for i, (chat, intent) in enumerate(zip(list_of_chats, list_of_intents)):
# 		d = defaultdict(dict)
# 		try:
# 			response = post_message_to_slack(channel_id, text=chat, as_user=as_user)
# 			d[str(i)] = {
# 				"timestamp": datetime.now().timestamp(),
# 				"channel_id": channel_id,
# 				"chat": chat,
# 				"intent": intent,
# 				"response": response
# 			}
# 			tests.append(d)
# 		except:  # TODO specify Exception
# 			pass
# 	return tests


# if __name__ == '__main__':
# 	# run from interpreter directory containing `tests.txt` and `custom/` dir
# 	posted_chats = post_test_chats_to_slack(infile='tests.txt', as_user='true')
# 	json.dump(posted_chats, open('posted_transcripts.txt', 'w+'))
