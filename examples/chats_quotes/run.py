#!/usr/bin/env python3

# import argparse
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

####################################################################################

####################################################################################
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


####################################################################################
# STEP 1 - transcript posted to slack
# test_dict=None): #transcript, channel_id, # slack_access_token, outfile):
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

####################################################################################
# For Chat_slack and Discovery
def post_to_microservice(url, payload):
    if not payload:
        return {}
    headers = {"Content-Type": "application/json"}
    response_json = post(url, headers=headers, payload=payload)
    if not response_json and not "segments" in response_json and not response_json["segments"]:
        print("Failure. Segment lattice not returned: \n {}".format(response_json))
        return {}
    return response_json




chat_slack_port = os.environ.get("CHAT_SLACK_PORT", 8000)
discovery_port = os.environ.get("DISCOVERY_PORT", 8001)


SLACK_ACCESS_TOKEN = "xoxp-4953937137-344679330118-509400138422-a20f349799113ba21f5c91e8a190cd14"
slack_access_token = os.environ.get("SLACK_ACCESS_TOKEN", SLACK_ACCESS_TOKEN)

CHANNEL_NAME = channel_name = os.environ.get("CHANNEL_NAME", "ageojo_test")
channel_id = os.environ.get("CHANNEL_ID", "CEXMKJAJH")

service_type = "slack"




chat_slack_url = "http://localhost:{}/process".format(chat_slack_port)
discovery_url = "http://localhost:{}/process".format(discovery_port)



def set_params(**kwargs):
    params = dict(
        channel_name=CHANNEL_NAME
    )
    for k,v in kwargs.items():
        params[k] = v
    return params







############################################################################
# Start
############################################################################

try:
    start, end = sys.argv[1], sys.argv[2] #test_file = sys.argv[1]
except IndexError:
    start, end = 0, 1

START, END = start, end
    

#test_file = "tests.txt"
#assert Path(test_file).exists() and Path(test_file).is_file()

#tests = list(load_tests(test_file))
#tests = tests[START:END]
#print(tests)


#quote_tests = "test_quotes_10.txt"
#expected_intent = "quote"

not_quote_tests = "test_not_quotes_10.txt"
expected_intent = "not_quote"

infile = not_quote_tests
tests = Path(infile).read_text().strip().splitlines()

#not_quotes = Path(not_quote_tests).read_text().strip().splitlines()
#tests = not_quotes

#expected_intent = "quote"

#for i, test in enumerate(tests, START):
#    test_name = test["test"]
#    transcript = test["transcript"]
#    expected_intent = test["intent"]
#    print(test_name)


#for i, transcript in enumerate(quotes, START):


#infile = "test_not_quotes_10.txt"

#with open(infile, 'r+') as f:
#  tests = [line.strip() for line in f.readlines() if line.strip()]

#tests =  Path("test_not_quotes_10.txt").read_text().strip().splitlines()
#expected_intent = "not_quote"




for i, transcript in enumerate(tests, START):
    test_no = i
    outfile = "{}_{}.json".format(test_no, expected_intent)

    try:
        posted_json = post_message_to_slack(transcript, channel_id, slack_access_token)

        if posted_json and posted_json["ok"] is True:

            # get from chat slack

            kwargs = dict(latest_ts=datetime.now().timestamp(), count=1, max_pages=1)

            payload = {"service_type": service_type, "params": set_params(kwargs=kwargs)}

            chat_segments = post_to_microservice(url=chat_slack_url, payload=payload)
            
            # to discovery

            if chat_segments:

                discovery_segments = post_to_microservice(url=discovery_url, payload=chat_segments)

                if discovery_segments:
                    
                    test = {"test_no": test_no, "test_transcript": transcript, "expected_intent": expected_intent}
                    discovery_segments.update(test)
                   
                    # SAVE 
                    dump_json(discovery_segments, outfile)

                    print("\nDiscovery Output for Test: {}\n {}\n".format(test_no, discovery_segments))
    except Exception as e:
        print("\nException: {}\n".format(e))
        logger.info("\nFailed: Number={} Expected={} Transcript={}\n".format(test_no, expected_intent, transcript))










































