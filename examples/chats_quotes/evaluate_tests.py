"""
# Precision: TP/ TP + FP     (of all predicted as positive, how many are true positives - true positive rate)
"""


# Returns metrics (more than compute key metrics) but also includes the arrays that comprise than as well as
# confusion matrix and normalized confusion matrix
def compute_metrics_and_tests(tests, intent, decimals=3):
	"""
	:param tests:
	:param intent:
	:param decimals: #TODO round all floats
	:return: returns both metrics as well as arrays corresponding to it for further analysis
	"""
	# TODO Use Pluck AND Refactor
	intent_is_expected = [test for test in tests if intent == test['expected']]
	intent_not_expected = [test for test in tests if intent != test['expected']]

	true_positives = [test for test in intent_is_expected if test['observed'] == intent]  # all == test.expected
	true_negatives = [test for test in intent_not_expected if test['observed'] == intent]

	false_negatives = [test for test in intent_is_expected if test['observed'] != test['expected']]
	false_positives = [test for test in intent_not_expected if test['observed'] != test['expected']]

	TP, TN = len(true_positives), len(true_negatives)
	FN, FP = len(false_negatives), len(false_positives)

	confusion_matrix = [[TP, FN], [FP, TN]]
	total_positives = TP + FN
	total_negatives = FP + TN

	normalized_cm = [[TP / total_positives, FN / total_positives], [FP / total_negatives, TN / total_negatives]]

	return dict(
		true_positives=true_positives,
		true_negatives=true_negatives,
		false_positives=false_positives,
		false_negatives=false_negatives,
		TP=TP,
		FN=FN,
		FP=FP,
		TN=TN,
		confusion_matrix=cm,
		normalized_cm=normalized_cm
	)


def compute_key_metrics(intent, tests, decimals=3):
	"""
	:param intent:
	:param tests: List[Dict] : keys = test, iintent/expected, observed
	:param decimals:
	:return:
	"""
	true_positives = list(filter(lambda x: x['expected'] == intent and x['observed'] == intent, tests))
	TP = len(true_positives)

	true_negatives = list(filter(lambda x: x['expected'] != intent and x['observed'] != intent, tests))
	TN = len(true_negatives)

	false_negatives = list(filter(lambda x: x['expected'] == intent and x['observed'] != intent, tests))
	FN = len(false_negatives)

	false_positives = list(filter(lambda x: x['expected'] != intent and x['observed'] == intent, tests))
	FP = len(false_positives)

	# get all exemplars where expected is current intent
	expected_intents = list(filter(lambda x: x['expected'] == intent, tests))
	num_is_expected_intent = len(expected_intents)  # TP + FN
	assert (TP + FN) == num_is_expected_intent

	expected_not_intents = list(filter(lambda x: x['expected'] != intent, tests))
	num_not_expected_intent = len(expected_not_intents)
	assert (TN + FP) == num_not_expected_intent

	num_tests = TP + FN + TN + FP
	assert num_tests == len(tests)

	recall = TP / (TP + FN)  # TP / num_expected_intents
	precision = TP / (TP + FP)  # TP / num_expected_not_intents

	# F1 Score
	f1_score = 2 * (precision * recall) / (precision + recall)

	# accuracy
	accuracy = (TP + TN) / num_tests  # (TP + TN + FP + FN)

	metrics = {
		"precision": precision,
		"recall": recall,
		"f1_score": f1_score,
		"accuracy": accuracy
	}
	if decimals:
		for key, val in metrics.items():
			metrics[key] = round(val, decimals)
	return metrics

import os
import requests



class InterpreterTest:
	# name = 'discovery_interpreter_test'
	def __init__(self, test_dict, request_dict=None, chat_slack_lattice=None, discovery_lattice=None):
	# def __init__(self, test_name, transcript, expected_intent):
		self.test = test_dict
		self.chat_slack_request = request_dict

	@property
	def transcript(self):
		return self.test['transcript']

	@property
	def observed(self):
		return self.test['intent']

	@property
	def name(self):
		return self.test['test']

	@property
	def expected(self):
		return self.get_expected_intent()
##########################################################################

"""
transcript will be posted to Slack, then retrieved via Chat_Slack microservice, then posted to Disocvery
performance will be evaluated by comparing observed (discovery custom interpreter predicted intent) with expected (
true intent as specified in tests.txt following key `intent`
"""

# FUNCS
# TODO: sessionize, make robust, take into account possible errors
# TODO: SEE microsesrvice middleware stuffs
# TODO: RETRIES & SLEEP
# TODO support query_params?  ||     f"{url}?q={query_params}"
def post(url, headers, payload):
	""" generic function to /POST to url (str), headers (dict); payload: JSON (use json param)"""
	r = requests.post(url, headers=headers, json=payload)
	if r.status_code in requests.codes.ok:  #TODO  r.raise_for_status()    ??
		return r.json()


def bucket(data, n):
	"""data: List of items; returns List with consecutive n items grouped"""
	pass


def get_tests(infile):
	"""
	:param infile:
	:return: List[Dict] -> each is a test with keys: test, transcript (str) and intent (expected intent_
	"""
	pass


# GKT_USERNAME
# GKT_SECRETKEY
SCRIBE_API_URL = os.getenv("SCRIBE_API_URL", "http://scribeapi.com/")
CHAT_SLACK_PORT = 8005
DISCOVERY_PORT = 8006
chat_slack_url = f"{SCRIBE_API_URL}:{CHAT_SLACK_PORT}/process"
discovery_url = f"{SCRIBE_API_URL}:{DISCOVERY_PORT}/process"

# Slack specific information needed to make requests --> already in env b.c of docker compose
SLACK_API_URL = os.getenv("SLACK_API_URL", "http://slack.com/api")   # important no trailing slash
SLACK_ACCESS_TOKEN = os.getenv("SLACK_ACCESS_TOKEN", None)

def post_message_to_slack(message):
	url = "http://slack.api/post.Message"     # f"{SLACK_API_URL.rstrip("/"}/{post.Message}"
	slack_auth_headers = dict(Authorization="Bearer {}".format(SLACK_ACCESS_TOKEN))
	post(url, headers=slack_auth_headers, payload=message)

def post_to_microservice(request_dict, port):
	url = "http://scribeapi.com:{}/process".format(port)
	headers = {"Content-type": "application/json"}
	return post(url=url, headers=headers,  payload=request_dict)

# fetch_chat_from_slack     # Chat_Slack
def fetch_chat(params, port):
	"""
	POST to chat_slack to retrieve chat matching params in
	:param params: dict; must contain 'channel_name'
		TODO set default to ageojo & mod so do not have to look up ids for all channels if found once
	:param port: int, port to POST to chat_slack service
	:return: JSON, dict with top level key 'segments' & value: List[Dict],
		each Dict in the list represents a chat & contains
		key/val for Segment properties #TODO add in chat-specific information
	"""
	service = "slack"
	request_dict = dict(service=service, params=params)
	chat_segment = post_to_microservice(request_dict=request_dict, port=port)
	# validate chat_segment
	return chat_segment

# extract_intents_from_chat   # Discovery
def extract_intents(segment, port):
	"""
	:param segment: dict; JSON lattice input to microservices
		for chats, top level key is 'segments', value is List[Dict]
			each Dict contains information returned from chat_slack
				(segment properties + chat specific ones?)
	:param port: int, port to post to Discovery
	:return: JSON, dict; input lattice augmented with additional keys - intent (& entities)
	"""
	discovery_segment = post_to_microservice(request_dict=segment, port=port)
	# validate discovery_segment
	return discovery_segment

if __name__ == "__main__":
	infile = 'tests.txt'
	tests = get_tests(infile)
	transcript = tests.__next__()

	post_msg_resp = post_message_to_slack(message=transcript)     # POST Slack /post.Message
	# POST chat_slack /process    -> GET Slack /channels.list  --> GET Slack  /channels.history   --> segment lattice

	# if post was successful, then get the latest chat (one just posted) with chat_slack
	from datetime import datetime
	TIME = datetime.now().timestamp()
	params = dict(channel_name="ageojo_test", channel_id="", count=1, page=1, latest_ts=TIME)   # TODO other paramaters

	chat_segment = fetch_chat(params, port=CHAT_SLACK_PORT)                                          #, service='slack')
	discovery_segment = extract_intents(chat_segment, port=DISCOVERY_PORT)

	# for test_no, test in tests:                         # expected intent
	# 	name, transcript, expected = test['test'], test['transcript'], test['intent']


import pandas as pd
tests = load_tests(infile='tests.txt')
# df = pd.from_dict(tests, orient='h').rename(columns={"intent" : "expected"}, inplace=True)
# pd.DataFrame.from_dict(data=test, orient='')

pd.read_json(lines=True, orient='h', encoding='utf-8')

# test transcript intent







for test_no, test in load_tests(infile):
	interpreter = InterpreterTest(test_no, test_dict=test)










# class ChatSegment:
# 	name = "chat"
#
# 	def __init__(self, input_dict):
# 		self.__dict__ = {
# 			"test_name": self.test_name,
# 			"transcript": self.transcript,
# 			"expected": self.expected,
# 			"observed": self.observed,
# 		}
# 		self.__dict__.update(input_dict if input_dict else {})
#
# 	@property
# 	def test_id(self):
# 		return hash(self.test_name)
#
#
#
#
#
# test = IntentTest(intent, tests)  # for each test in tests -> computes metrics for specified intent
# test.TP  # test.FP etc.
# cm = test.confusion_matrix()
# normalized_cm = test.confusion_matrix(normalized=True)
