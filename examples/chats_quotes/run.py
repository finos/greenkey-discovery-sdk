#!/usr/bin/env python3

import os
import requests
import json
import logging
import time
import sys
from pathlib import Path
from datetime import datetime
import pprint as pp

logger = logging.getLogger(__name__)


def dump_json(data, outfile):
    json.dump(data, open(outfile, 'w+'))


def load_json(infile):
    return json.load(open(infile, 'r+'))


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


def load_tests(test_file="tests.txt"):
    """
    :param test_file: str; default tests.txt; tests in format required for test_discovery.py
    :return:  iterator of dicts, each with all fields for a single test
        reads in tests.txt and returns an iterator of dicts corresponding to each test
    """
    test_data = Path(test_file).read_text().splitlines()
    assert Path(test_file).exists() and Path(test_file).is_file()
    tests = [
        line.split(":", maxsplit=1)
        for line in test_data
        if line.strip() and line.split(":")[0].strip() in ['test', 'transcript', 'intent']
    ]
    test_dicts = map(dict, bucket(tests, 3))
    return test_dicts    # return list(test_dicts)


# Generic Post - STEP 0
def post(url, headers, payload, timeout=10, delay=4, max_tries=5):
    """ post to url """
    # repeat request at most max_tries; return if succeed
    for i in range(max_tries):
        r = requests.post(url, headers=headers, json=payload, timeout=timeout)
        try:
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(e)
            print(r.status_code)
            time.sleep(delay + 2)  # increment delay with each post
            continue
        return {}


# STEP 1 - transcript posted to slack
def post_message_to_slack(transcript=None, channel_id=None, slack_access_token=None):#, outfile=None):
    """
    transcript str; chat to post to Slack channel given by channnel id
       OUTFILE and SLACK_ACCESS_TOKEN are globals
    """
    url = "https://slack.com/api/chat.postMessage"
    # transcript, channel_id = request_dict["transcript"], request_dict["channel_id"]
    headers = dict(Authorization="Bearer {}".format(slack_access_token))  #request_dict["slack_access_token"]))
    payload = dict(channel=channel_id, text=transcript, as_user="true")
    posted_json = post(url, headers=headers, payload=payload) # post json output
    return posted_json
    # dump_json(data=posted_json, outfile="post_message_{}".format(outfile))    # request_dict["outfile"]
    # return validate_post_messaage(posted_json, transcript), posted_json


# STEP 2 & 3: Chat_slack and Discovery
def post_to_microservice(url, payload):
    if not payload:
        return {}
    headers = {"Content-Type": "application/json"}
    response_json = post(url, headers=headers, payload=payload)
    if not response_json and not "segments" in response_json and not response_json["segments"]:
        print("Failure. Segment lattice not returned: \n {}".format(response_json))
        return {}
    return response_json


def set_params(**kwargs):
    """dict; optional; update chat_slack params"""
    params = dict(
        channel_name=CHANNEL_NAME
    )
    for k, v in kwargs.items():
        params[k] = v
    if "latest_ts" not in params:
        params["latest_ts"] = datetime.now().timestamp()
    return params


def main(tests, expected_intent, service_type, channel_id, slack_access_token, chat_slack_port, discovery_port, params):
    """
    :param tests: List[str], each str is a transcript/chat
    :param expected_intent: str; intent label
    :param service_type: str; chat service; presently, 'chat_slack'
    :param channel_id: str;  id corresponding to channel to post message to; default id is for channel #ageojo_test
    :param slack_access_token: str;
    :param chat_slack_port: int; port chat_slack is listening on
    :param discovery_port: int; port discovery is listening on
    :param count: int; number of messages chat_slack should retrieve
    :param max_pages: int; max number of pages chat_slack should retrieve messages from; default 100 messages
    per page
    :param latest_ts: float; timestamp of most recent message to returun
    :return:
        posts each str in tests to Slack channel with id channel_id,
        retrieves that chat message with chat_slack and converts to JSON segments
        posts chat segment(s) to Discovery
        adds test information (test_no, expected_intent, transcript) to Discovery output segments
        saves final output as JSON
      if any of the above steps fails, logs test information: test_no, expected_intent, and transcript
    """
    chat_slack_url = "http://localhost:{}/process".format(chat_slack_port)
    discovery_url = "http://localhost:{}/process".format(discovery_port)
    for i, transcript in enumerate(tests):
        test_no = i
        outfile = "{}_{}.json".format(test_no, expected_intent)
        try:  # post message to Slack
            posted_json = post_message_to_slack(transcript, channel_id, slack_access_token)

            # get message from chat slack
            if posted_json and posted_json["ok"] is True:
                payload = {
                    "service_type": service_type,
                    "params": params
                }
                chat_segments = post_to_microservice(url=chat_slack_url, payload=payload)

                # to discovery
                if chat_segments:
                    discovery_segments = post_to_microservice(url=discovery_url, payload=chat_segments)

                    # update discovery output with test information
                    if discovery_segments:
                        test = {
                            "test_no": test_no,
                            "test_transcript": transcript,
                            "expected_intent": expected_intent
                        }
                        discovery_segments.update(test)

                        # SAVE augmented discovery segments
                        dump_json(discovery_segments, outfile)
                        print("\nDiscovery Output for Test: {}\n {}\n".format(test_no, discovery_segments))
        except Exception as e:
            print("\nException: {}\n".format(e))
            logger.info("\nFailed: Number={} Expected={} Transcript={}\n".format(test_no, expected_intent, transcript))


if __name__ == '__main__':
    SLACK_ACCESS_TOKEN = "xoxp-4953937137-344679330118-509400138422-a20f349799113ba21f5c91e8a190cd14"
    slack_access_token = os.environ.get("SLACK_ACCESS_TOKEN", SLACK_ACCESS_TOKEN)

    CHANNEL_NAME = channel_name = os.environ.get("CHANNEL_NAME", "ageojo_test")
    channel_id = os.environ.get("CHANNEL_ID", "CEXMKJAJH")

    service_type = "slack"

    chat_slack_port = os.environ.get("CHAT_SLACK_PORT", 8000)
    discovery_port = os.environ.get("DISCOVERY_PORT", 8001)

    COUNT, MAX_PAGES = 1, 1
    # LATEST_TS = None

    # --infile  --expected-intent
    quotes_infile = "test_quotes_10.txt"
    not_quote_infile = "test_not_quotes_10.txt"

    test_files = [
        (quotes_infile, "quote"),
        (not_quote_infile, "not_quote")
    ]
    for infile, expected_intent in test_files:
        assert Path(infile).exists() and Path(infile).is_file()
        tests = Path(infile).read_text().strip().splitlines()

        for i, transcript in enumerate(tests, start=1):
            params = set_params(kwargs=dict(count=COUNT, max_pages=MAX_PAGES))
            main(tests, expected_intent, service_type, channel_id, slack_access_token, chat_slack_port, discovery_port,
                 params)












































