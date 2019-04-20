#!/usr/bin/env python3

# import argparse
import requests
import json
import logging
import time
import sys
from pathlib import Path
from datetime import datetime
import pprint as pp


logger = logging.getLogger(__name__)

#############################################################################################################
# TODO Tejas Meeting
#parser = get_env_opts()
#args = parser.parse_args()

#outfile = args.outfile
#if not outfile:
#    OUTFILE = "{}_{}_{}.json".format(args.latest_ts, args.expected_intent, args.test_no)

#chat_slack_url = "http://localhost:{}/process".format(args.chat_slack_port)
#discovery_url = "http://localhost:{}/process".format(args.discovery_port)

#SLACK_ACCESS_TOKEN = args.slack_access_token

####################################################################################

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
def post(url, headers, payload, timeout=10, delay=3, max_tries=5):
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
            time.sleep(delay + 1)  # increment delay with each post
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

#TODO This function is not so easily portable as relies heavily on CLI args
# Chat_Slack -> fetch posted message
#def chat_slack_request_dict(latest_ts=args.latest_ts, channel_name=args.channel_name, channel_id=args.channel_id, count=args.count, max_pages=args.max_pages, service_type=args.service_type, expected_intent=args.expected_intent, expected_transcript=args.expected_transcript, test_no=args.test_no):

def fetch_chats_via_chat_slack(request_dict=None, test_dict=None, outfile=None, chat_slack_url=None):
    print("\n#2 Fetching posted chat via chat_slack\n")
    # logger.info("\n#2 Fetching posted chat via chat_slack\n")
    chat_segments = post_to_microservice(url=chat_slack_url, payload=request_dict)
    if chat_segments and chat_segments["segments"][0]["transcript"] == test_dict["transcript"]:
        print("Chat Slack Successfully fetched Chat")
        # chat_segments.update(test_dict)     # add on all test info including expected_intent
        chat_segments["expected_intent"] = test_dict["expected_intent"]  # Adding in expected intent
        chat_segments["test_no"] = test_dict["test_no"]
        outfile = "chat_segments_{}".format(outfile)
        dump_json(data=chat_segments, outfile=outfile)
    return chat_segments


# Discovery: POST output from chat_slack to Discovery (already added intents)
def extract_intents_via_discovery(chat_segments, outfile=None, discovery_url=None):
    discovery_segments = post_to_microservice(url=discovery_url, payload=chat_segments)

    if discovery_segments and "segments" in discovery_segments and "intents" in discovery_segments["segments"][0]:
        print("Discovery returned augmented lattice with intents!")
        dump_json(data=discovery_segments, outfile="discovery_segments_{}".format(outfile))
        pp.pprint("Discovery Lattice: {}".format(discovery_segments))
    else:
        print("------- Post to Discovery Failed ----------- \n Output: {}".format(discovery_segments))
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


def main(test_dict=None, request_dict=None, outfile=None, chat_slack_port=None, discovery_port=None):
    chat_slack_url = "http://localhost:{}/process".format(chat_slack_port)
    discovery_url = "http://localhost:{}/process".format(discovery_port)

    test_no, transcript, expected_intent = test_dict["test_no"], test_dict["transcript"], test_dict["expected_intent"]
    if not outfile:
        outfile = "{}_{}.json".format(test_no, expected_intent)
    print("--------------------------------------------")
    print("\n Test Number: {}\n".format(test_no))
    logger.info("\n#1 Posting message to chat_slack: \n Intent: {} \n Transcript: {}\n".format(expected_intent, transcript))
    
    # if not test_dict:
    #     test_dict = track_test_fields(test_no, transcript, expected_intent, outfile)
    chat_segments, discovery_segments = {}, {}

    # message_was_posted, response_json = post_message_to_slack(request_dict, outfile)
    posted_json = post_message_to_slack(transcript=transcript, channel_id=channel_id, slack_access_token=slack_access_token)
    message_was_posted = posted_json and posted_json["ok"] is True and posted_json["message"]["text"] == transcript
    if message_was_posted:
        logger.info("Step 1: Success. Transcript posted to Slack /post.Message")
        try:  # ONLY FETCH chat with `chat_slack` IF transcript POSTED SUCCESSFULLY
            chat_segments = fetch_chats_via_chat_slack(request_dict, test_dict, outfile, chat_slack_url)
            assert chat_segments["segments"]["transcript"] == transcript
            # only post to discovery if chat_segments retrieve   ^^ assertion fails no transcript and no discovery
            print("\n#3 Sending chat_segment to discovery:\n {}".format(chat_segments))
            discovery_segments = extract_intents_via_discovery(chat_segments, outfile,  discovery_url)
            if not discovery_segments:
                print("------- Post to Discovery Failed ----------- \n Output: {}".format(discovery_segments))
        except (KeyError, AssertionError):
            print("Failed: Chat_Slack did NOT retrieve chat data for test: {}\n".format(test_no))
            print("Nothing will be posted to Discovery. Program Terminating")
    return posted_json, chat_segments, discovery_segments


if __name__ == '__main__':
    from opts import get_env_opts
    parser = get_env_opts()
    args = parser.parse_args()

    # in Docker-compose
    chat_slack_port, discovery_port = args.chat_slack_port, args.discovery_port
    service_name = args.service_name
    slack_access_token = args.slack_access_token

    outfile = args.outfile

    test_no, transcript, expected_intent = args.test_no, args.transcript, args.expected_intent
    test_dict = {"test_no": test_no, "transcript": transcript, "expected_intent": expected_intent}
    # test_dict = dict(test_no=test_no, transcript=transcript, expected_intent=expected_intent)

    # for params_dict
    channel_name, channel_id,  = args.channel_name, args.channel_id
    count, max_pages, latest_ts = args.count, args.max_pages, args.latest_ts

    chat_slack_request_dict = dict(
        service_name=service_name, channel_name=channel_name, channel_id=channel_id,
        count=count, max_pages=max_pages, latest_ts=latest_ts, message=transcript,
    )

    main(test_dict=test_dict, request_dict=chat_slack_request_dict, outfile=outfile,
         chat_slack_port=chat_slack_port, discovery_port=discovery_port)
    sys.exit()


 # #############################################################################################################
 #    from collections import defaultdict
 #    import json
 #    #posted. chat_segments, discovery_segments = main(test_no=args.test_no)
 #    tests = load_tests(args.test_file)
 #    results = defaultdict(dict)
 #    for test_no, test in tests:
 #        test["test_no"] = test_no
 #        results[test_no] = {"expected_intent": test["intent"], "results": {}}
 #
 #        test["expected_intent"] = expected_intent = test["intent"]
 #        #del test["intent"]
 #        transcript = test["transcript"]
 #        try:
 #            posted, chat_segments, discovery_segments = main(test_no=test_no, transcript=transcript)
 #            results[test_no]["results"] = {"posted":posted, "chat_segments":chat_segments, "discovery_segments":discovery_segments}
 #            test["posted"] = posted
 #            test["chat_segments"] = chat_segments
 #            test["discovery_segments"] = discovery_segments
 #            results[test_no] = test
 #        except Exception as e:
 #            print("Failed on Test: {}".format(test_no))
 #            print("Exception: {}".format(e))
 #            continue
 #        if test_no == 1 or not (test_no % 10):
 #            #try:
 #                #outfile = f"{test_no}_{test['expected_intent']}_{len(results)}"
 #            #except:
 #            expected_intent = test["expected_intent"]
 #            outfile = "{}_{}".format(test_no, len(results))   #expected_intent, len(results))
 #            json.dump(test, open(outfile, 'w+'))


   
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
