import requests
import os
import sys
import json
import time
import pprint as pp

import argparse


# SECRETS / ENV VARS in docker-compose
# SCRIBE_API_URL
# GK_USERNAME
# GK_SECRETKEY

#SLACK_API_URL
SLACK_ACCESS_TOKEN = "xoxp-4953937137-344679330118-509400138422-a20f349799113ba21f5c91e8a190cd14"
slack_access_token = os.environ.get("SLACK_ACCESS_TOKEN", SLACK_ACCESS_TOKEN)

channel_name = os.environ.get("CHANNEL_NAME", "ageojo_test")
channel_id = os.environ.get("CHANNEL_ID", "CEXMKJAJH")


# START ARGPARSE:

parser = argparse.ArgumentParser(description="posting chats, getting chats, sending chat segments to discovery")
#parser.add_argument("--tests", default="tests.txt", description="File containing test data tests.txt format")
#parser.add_argument("--chat-segments", default="ageojo_chat_segments.json", description="File containing chat_segment(s) from chat_slack to post to discovery")

# microservice ports 
parser.add_argument("--discovery-port", default=8006, help="Port Discovery is listening on")
parser.add_argument("--chat-slack-port", default=8005, help="Port chat_slack is listening on")

# Data
parser.add_argument("--test-no", required=True, type=int,  help="Unique number for test of this transcript")
parser.add_argument("--transcript", required=True, type=str, help="Transcript to post to chat, retrieve via chat_slack, and after processing, post chat_segment to discovery")
parser.add_argument("--expected-intent", required=True, type=str, help="Intent corresponding to transcript")

# Slack related - for posting messages and fetching via chat_slack)
parser.add_argument("--slack-access-token", default=slack_access_token, help="Access token to post messages to GK workspace")
parser.add_argument("--channel-name", default="ageojo_test", type=str, help="Name of slack channel in GK workspace to post/get chats")
parser.add_argument("--channel-id", default="CEXMKJAJH", type=str, help="Name of slack channel id corresponding to channel_name; used by chat_slack to retrieve chats")

# Request related params
parser.add_argument("--max-tries", default=5, type=int, help="Number of times to retry posting to service. Used for all GET/POST requests")
parser.add_argument("--delay", default=3, type=int, help="Number of seconds to wait before sending request to same url")
parser.add_argument("--timeout", default=10, type=int, help="Number of seconds to wait before terminating request if no response from server")


parser.add_argument("--outfile", help="Name of JSON file to save discover output")

args = parser.parse_args()



service_type = "slack"

chat_slack_url = "http://localhost:{}/process".format(args.chat_slack_port)
discovery_url = "http://localhost:{}/process".format(args.discovery_port)



# STEP 1 - transcript posted to slack
def post_message_to_slack(transcript, channel_id, slack_access_token):
  """transcript str; chat to post to Slack channel given by channnel id"""
  url = "https://slack.com/api/chat.postMessage"
  headers = dict(Authorization="Bearer {}".format(slack_access_token))
  payload = dict(channel=channel_id, text=transcript, as_user="true")
  return post(url, headers=headers, payload=payload)



# Generic Post - STEP 0
def post(url, headers, payload):
  """ post to url """
  for i in range(args.max_tries):
  # loop request at most max_tries; return if succeed
    try:
      r = requests.post(url, headers=headers, json=payload, timeout=args.timeout)
      if r.status_code == 200:
        break
    except:
      print(r.status_code)
      time.sleep(args.delay + 1)  # increment delay with each post
      continue
  try:
    return r.json()
  except:
    return {}



#def fetch_chat(params):
#  assert "channel_name" in params    # or "channel_id" in params
#  request_dict = dict(service_type="slack", params=params)
#  response = post(chat_slack_url, headers=microservice_headers, payload=request_dict)
#  if "segments" in response and response["segments"]:
#    return response
#  return {}


#def test_discovery(chat_segments):
#  response = post(discovery_url, headers=microservice_headers, payload=chat_segments)
#  if "segments" in response and response["segments"] and "intents" in response["segments"]:
#    return response
#  return {}


def post_to_microservice(url, payload):
  if not payload:
    return {}
  headers = {"Content-Type": "application/json"}
  response_json = post(url, headers=headers, payload=payload)
  if not response_json and not "segments" in response_json and not response_json["segments"]:
    print("Failure. Segment lattice not returned: \n {}".format(response_json))
    return {}
  return response_json



def chat_slack_request_dict():
  """add other params: count, pages, latest/ts, chats"""
  service_type="slack"
  params = dict(channel_name=args.channel_name, channel_id=args.channel_id, count=1, pages=1)
  request_dict = dict(service_type=service_type, params=params)
  return request_dict



####################################################################################     
# START 

# MAIN


# Post transcript to channel : channel_id
def post_transcript_to_slack():
  """
  :return dict; if successfully posted message, returns output
	top level keys: response_metadata (dict), message (dict), ts (str, epoch timestamp), ok (bool)
          output['message'].keys()  -> ts, message, channel_id, ?
  """
  posted = post_message_to_slack(args.transcript, args.channel_id, args.slack_access_token)
  if posted and posted["ok"] is True:
    print("Step 1: Success. Transcript posted to Slack /post.Message")
    return posted     
    #if "ts" in posted:
      #return posted['ts']
  return {} # False


###############################################################################################
# chat_slack - fetch latest (just posted) message from slack


def fetch_chats_via_chat_slack():
  print("fetching chat via chat_slack")
  request_dict = chat_slack_request_dict()
  chat_segments = post_to_microservice(url=chat_slack_url, payload=request_dict)
  return chat_segments 

####################################################################################################
# send chat segments to discovery

def extract_intents_via_discovery(chat_segments):
  discovery_segments = post_to_microservice(url=discovery_url, payload=chat_segments)
  print("discovery segments: \n {}".format(discovery_segments))

  if discovery_segments and "segments" in discovery_segments and "intents" in discovery_segments["segments"][0]:
    print("Discovery returned augmented lattice with intents!")
    return discovery_segments
  return {}



def insert_expected_intent(discovery_segments):
  try:
    for i in range(len(discover_segments["segments"])):
      discovery_segments["segments"][i]["intents"]["expected_intent"] = args.expected_intent
  except Exception as e:
    print("Error when trying to insert expected intent: {}".format(e))
    discovery_segments["expected_intent"] = args.expected_intent
  return discovery_segments



def dump_json(data, outfile):
  json.dump(data, open(outfile, 'w+'))


def load_json(infile):
  return json.load(open(infile, 'r+'))


chat_segments = {}
discovery_segments = {}


print("\n#1 Posting message to chat_slack: \n Intent: {} \n Transcript: {}\n".format(args.expected_intent, args.transcript))
posted = post_transcript_to_slack()

if posted and isinstance(posted, dict):
  print("Response from posting message to Slack at post.Message")
  ts = posted["ts"]  # posted_timestamp
  dump_json(posted, outfile="posted_message_{}_{}.json".format(args.expected_intent, args.test_no)) #, ts))


print("\n#2 Fetching posted chat via chat_slack\n")
chat_segments = fetch_chats_via_chat_slack()
print(len(chat_segments["segments"]))

chat_slack_outfile = "chat_segments_{}_{}.json".format(args.expected_intent, args.test_no)
discovery_outfile = "discovery_segment_{}_{}.json".format(args.expected_intent, args.test_no)

if chat_segments:
  chat_segments["segments"][0]["expected_intent"] = args.expected_intent
  dump_json(chat_segments, chat_slack_outfile)
  
print("\n#3 Sending chat_segment to discovery:\n {}".format(chat_segments))
discovery_segments = extract_intents_via_discovery(chat_segments)
if discovery_segments:
  dump_json(discovery_segments, discovery_outfile)
  pp.pprint("Discovery Lattice: {}".format(discovery_segments))
else:
  print("------- Post to Discovery Failed ----------- \n Output: {}".format(discovery_segments))
