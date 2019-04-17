#!/usr/bin/env python3

import requests
import json
import logging
import time
import pprint as pp

from opts import get_env_opts

logger = logging.getLogger(__name__)

parser = get_env_opts()
args = parser.parse_args()

outfile = args.outfile
if not outfile:
    OUTFILE = "{}_{}_().json".format(args.latest_ts, args.expected_intent, args.test_no)

chat_slack_url = "http://localhost:{}/process".format(args.chat_slack_port)
discovery_url = "http://localhost:{}/process".format(args.discovery_port)

SLACK_ACCESS_TOKEN = args.slack_access_token

####################################################################################


def dump_json(data, outfile):
    json.dump(data, open(outfile, 'w+'))


def load_json(infile):
    return json.load(open(infile, 'r+'))


####################################################################################
# Generic Post - STEP 0
def post(url, headers, payload, timeout=args.timeout, delay=args.delay):
    """ post to url """
    # repeat request at most max_tries; return if succeed
    for i in range(args.max_tries):
        r = requests.post(url, headers=headers, json=payload, timeout=timeout)
        try:
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(e)
            print(r.status_code)
            time.sleep(delay + 1)  # increment delay with each post
            continue
        return {}


####################################################################################
# STEP 1 - transcript posted to slack
def post_message_to_slack(transcript):
    """
    transcript str; chat to post to Slack channel given by channnel id
       OUTFILE and SLACK_ACCESS_TOKEN are globals
    """
    url = "https://slack.com/api/chat.postMessage"
    headers = dict(Authorization="Bearer {}".format(SLACK_ACCESS_TOKEN))
    payload = dict(channel=args.channel_id, text=transcript, as_user="true")
    posted_json = post(url, headers=headers, payload=payload)
    dump_json(data=posted_json, outfile="post_message_{}".format(OUTFILE))
    return validate_post_messaage(posted_json)


# Post transcript to channel : channel_id
def validate_post_messaage(posted_json):
    """
    :param posted_json: dict, JSON response from POST
        message to Slack at endpoint postMessage
    :return: bool; True if succesfully posted message, else False
    """
    return posted_json and posted_json["ok"] is True
    # print("Step 1: Success. Transcript posted to Slack /post.Message")


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


#TODO This function is not so easily portable as relies heavily on CLI args
# Chat_Slack -> fetch posted message
def chat_slack_request_dict():
    """add other params: count, pages, latest/ts, chats"""
    service_type = "slack"
    params = dict(
        channel_name=args.channel_name,
        channel_id=args.channel_id,
        count=args.count,
        max_pages=args.max_pages,
        latest_ts=args.latest_ts
    )
    request_dict = dict(service_type=service_type, params=params)
    return request_dict


def fetch_chats_via_chat_slack(request_dict=None):
    print("fetching chat via chat_slack")
    if not request_dict:
        request_dict = chat_slack_request_dict()
    chat_segments = post_to_microservice(url=chat_slack_url, payload=request_dict)
    if chat_segments:
        print("Chat Slack Successfully fetched Chat")
        chat_segments["expected_intent"] = args.expected_intent  # Adding in expected intent
        dump_json(data=chat_segments, outfile="chat_segments_{}".format(OUTFILE))
    return chat_segments


# Discovery: POST output from chat_slack to Discovery (already added intents)
def extract_intents_via_discovery(chat_segments):
    discovery_segments = post_to_microservice(url=discovery_url, payload=chat_segments)

    if discovery_segments and "segments" in discovery_segments and "intents" in discovery_segments["segments"][0]:
        print("Discovery returned augmented lattice with intents!")
        dump_json(data=discovery_segments, outfile="discovery_segments_{}".format(OUTFILE))
        pp.pprint("Discovery Lattice: {}".format(discovery_segments))
    return discovery_segments


# def insert_expected_intent(discovery_segments):
#     try:
#         for i in range(len(discovery_segments["segments"])):
#             discovery_segments["segments"][i]["intents"]["expected_intent"] = args.expected_intent
#     except Exception as e:
#         print("Error when trying to insert expected intent: {}".format(e))
#         discovery_segments["expected_intent"] = args.expected_intent  # also ^
#         dump_json(data=discovery_segments, outfile="discovery_segments_{}".format(OUTFILE))
#     return discovery_segments


def main(test_no):
    print("--------------------------------------------")
    print("\n Test Number: {}\n".format(test_no))
    print(
        "\n#1 Posting message to chat_slack: \n Intent: {} \n Transcript: {}\n".format(
            args.expected_intent, args.transcript
        )
    )
    chat_segments, discovery_segments = {}, {}
    if post_message_to_slack(args.transcript):  # returns bool b/c validation function
        print("Step 1: Success. Transcript posted to Slack /post.Message")
        # ONLY FETCH chat with `chat_slack` IF transcript POSTED SUCCESSFULLY
        print("\n#2 Fetching posted chat via chat_slack\n")
        chat_segments = fetch_chats_via_chat_slack()
    try:
        print(len(chat_segments["segments"]))
        print("\n#3 Sending chat_segment to discovery:\n {}".format(chat_segments))
        # only post to discovery if chat_segments retrieve
        discovery_segments = extract_intents_via_discovery(chat_segments)
        print("------- Post to Discovery Failed ----------- \n Output: {}".format(discovery_segments))
    except KeyError:
        print("Failed: Chat_Slack did NOT retrieve chat data for test: {}\n".format(test_no))
        print("Nothing will be posted to Discovery. Program Terminating")
    return posted, chat_segments, discovery_segments


if __name__ == '__main__':
    posted, chat_segments, discovery_segments = main(test_no=args.test_no)

    # chat_segments = {}
    # discovery_segments = {}
    #
    # print(
    #     "\n#1 Posting message to chat_slack: \n Intent: {} \n Transcript: {}\n".format(
    #         args.expected_intent, args.transcript
    #     )
    # )
    # posted = post_message_to_slack(args.transcript)
    #
    # if posted and isinstance(posted, dict):
    #     print("Response from posting message to Slack at post.Message")
    #     ts = posted["ts"]  # posted_timestamp
    #     dump_json(posted, outfile="posted_message_{}_{}.json".format(args.expected_intent, args.test_no))  # , ts))
    #
    # print("\n#2 Fetching posted chat via chat_slack\n")
    # chat_segments = fetch_chats_via_chat_slack()
    # print(len(chat_segments["segments"]))
    #
    # chat_slack_outfile = "chat_segments_{}_{}.json".format(args.expected_intent, args.test_no)
    # discovery_outfile = "discovery_segment_{}_{}.json".format(args.expected_intent, args.test_no)
    #
    # if chat_segments:
    #     chat_segments["segments"][0]["expected_intent"] = args.expected_intent
    #     dump_json(chat_segments, chat_slack_outfile)
    #
    # print("\n#3 Sending chat_segment to discovery:\n {}".format(chat_segments))
    # discovery_segments = extract_intents_via_discovery(chat_segments)
    # if discovery_segments:
    #     dump_json(discovery_segments, discovery_outfile)
    #     pp.pprint("Discovery Lattice: {}".format(discovery_segments))
    # else:
    #     print("------- Post to Discovery Failed ----------- \n Output: {}".format(discovery_segments))

# def fetch_chat(params):
#  assert "channel_name" in params    # or "channel_id" in params
#  request_dict = dict(service_type="slack", params=params)
#  response = post(chat_slack_url, headers=microservice_headers, payload=request_dict)
#  if "segments" in response and response["segments"]:
#    return response
#  return {}

# def test_discovery(chat_segments):
#  response = post(discovery_url, headers=microservice_headers, payload=chat_segments)
#  if "segments" in response and response["segments"] and "intents" in response["segments"]:
#    return response
#  return {}

###############################################################################################
# chat_slack - fetch latest (just posted) message from slack

####################################################################################################
# send chat segments to discovery
