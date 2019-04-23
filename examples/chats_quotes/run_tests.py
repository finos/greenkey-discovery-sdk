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


SLACK_ACCESS_TOKEN = "xoxp-4953937137-344679330118-509400138422-a20f349799113ba21f5c91e8a190cd14"
slack_access_token = os.environ.get("SLACK_ACCESS_TOKEN", SLACK_ACCESS_TOKEN)

CHANNEL_NAME = channel_name = os.environ.get("CHANNEL_NAME", "ageojo_test")
CHANNEL_ID = channel_id = os.environ.get("CHANNEL_ID", "CEXMKJAJH")

SERVICE_TYPE = service_type = "slack"

chat_slack_port = os.environ.get("CHAT_SLACK_PORT", 8000)
discovery_port = os.environ.get("DISCOVERY_PORT", 8001)

chat_slack_url = "http://localhost:{}/process".format(chat_slack_port)
discovery_url = "http://localhost:{}/process".format(discovery_port)


COUNT, MAX_PAGES = 1, 1



def dump_json(data, outfile):
    json.dump(data, open(outfile, 'w+'))


def load_json(infile):
    return json.load(open(infile, 'r+'))


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
            delay +=2
            time.sleep(delay)# + 2)  # increment delay with each post
            continue
        return {}


# STEP 1 - transcript posted to slack
def post_message_to_slack(transcript=None): 
    """
    transcript str; chat to post to Slack channel given by channnel id
       OUTFILE and SLACK_ACCESS_TOKEN are globals
    """
    url = "https://slack.com/api/chat.postMessage"
    headers = dict(Authorization="Bearer {}".format(SLACK_ACCESS_TOKEN))
    payload = dict(channel=CHANNEL_ID, text=transcript, as_user="true")
    posted_json = post(url, headers=headers, payload=payload)
    return posted_json


# STEP 2 & 3: Chat_slack and Discovery
def post_to_microservice(url, payload):
    if not payload:
        return {}
    headers = {"Content-Type": "application/json"}
    response_json = post(url, headers=headers, payload=payload)
    if response_json and "segments" in response_json and response_json["segments"]:
      return response_json
    else:
        print("Failure. Segment lattice not returned: \n {}".format(response_json))
        return {}


def load_tests(infile):
  """more tightly couples line_no/test_no with line/transcript"""
  with open(infile, 'r+') as f:
    return [(i, line) for i, line in enumerate(f.readlines())]


if __name__ == "__main__":

    import sys
    try:
       infile =  sys.argv[1]
       expected_intent = sys.argv[2]
    except:
       infile = "test_not_quotes_10.txt"
       expected_intent = "not_quote"


    SLACK_ACCESS_TOKEN = "xoxp-4953937137-344679330118-509400138422-a20f349799113ba21f5c91e8a190cd14"
    slack_access_token = os.environ.get("SLACK_ACCESS_TOKEN", SLACK_ACCESS_TOKEN)

    CHANNEL_NAME = channel_name = os.environ.get("CHANNEL_NAME", "ageojo_test")
    CHANNEL_ID = channel_id = os.environ.get("CHANNEL_ID", "CEXMKJAJH")

    service_type = "slack"

    chat_slack_port = os.environ.get("CHAT_SLACK_PORT", 8000)
    discovery_port = os.environ.get("DISCOVERY_PORT", 8001)

    COUNT, MAX_PAGES = 1, 1

    # Load Tests   ->  List[Tuple(test_no, transcript)]
    print("Loading Tests")
    tests = load_tests(infile)
    print("\n", tests[0], "\n")

    # IF make into a function -- need all of the params below
    # for i, transcript in enumerate(tests):  
    for i, (test_no, transcript) in enumerate(tests):  # when tests = load_tests(infile)
      if i==1 or i%25==0:
        print("Test Number: {}  (Loop: {})".format(test_no, i))
      if i%25==0:
        time.sleep(10)
      #test_no=i
      outfile="{}_{}.json".format(test_no, expected_intent)
      try:   # post message to Slack
        posted_json = post_message_to_slack(transcript) #, channel_id, slack, access_token)    
    
        if posted_json and posted_json["ok"] is True:  # get message from chat slack
          time.sleep(5)
          params = dict(channel_name="ageojo_test", max_pages=1, count=1)
          payload = dict(service_type="slack", params=params)      
          chat_segments = post_to_microservice(url=chat_slack_url, payload=payload)
      
          if chat_segments:  # to discovery
            discovery_segments = post_to_microservice(url=discovery_url, payload=chat_segments)
        
            if discovery_segments:  # add test information
              test = dict(test_no=test_no, test_transcript=transcript, expected_intent=expected_intent)
              discovery_segments.update(test)  # SAVE augmented discovery segments
              dump_json(discovery_segments, outfile)
              if i==0 or i%25==0:
                print("\nDiscovery Output:\n")
                pp.pprint(discovery_segments)
                print()
              time.sleep(5)
          # print("\nDiscovery Output for Test: {}\n {}\n".format(test_no, discovery_segments))
      except Exception as e:
        print("\nException: {}\n".format(e))
        time.sleep(10)
        logger.exception("\nFailed: Number={} Expected={} Transcript={}\n".format(test_no, expected_intent, transcript))



