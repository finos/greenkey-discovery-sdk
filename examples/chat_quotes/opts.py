#!/usr/bin/env python3

import argparse
import os
from datetime import datetime

##################################################################################
# SECRETS / ENV VARS in docker-compose
# SCRIBE_API_URL   # GK_USERNAME  # GK_SECRETKEY     # SLACK_API_URL

SLACK_ACCESS_TOKEN = "xoxp-4953937137-344679330118-509400138422-a20f349799113ba21f5c91e8a190cd14"
slack_access_token = os.environ.get("SLACK_ACCESS_TOKEN", SLACK_ACCESS_TOKEN)

channel_name = os.environ.get("CHANNEL_NAME", "ageojo_test")
channel_id = os.environ.get("CHANNEL_ID", "CEXMKJAJH")

# latest timestamp of retrieved messages
time_now = datetime.now().timestamp()


def general_opts():
    parser = argparse.ArgumentParser(description="posting chats, getting chats, sending chat segments to discovery")

    # microservice ports
    parser.add_argument("--discovery-port", default=8006, help="Port Discovery is listening on")
    parser.add_argument("--chat-slack-port", default=8005, help="Port chat_slack is listening on")

    # Data
    # parser.add_argument("--test-no", required=True, type=int, help="Unique number for test of this transcript")
    # parser.add_argument(
    # 	"--transcript",
    # 	required=True,
    # 	type=str,
    # 	help="Transcript to post to chat, retrieve via chat_slack, and after processing, post chat_segment to discovery"
    # )
    # parser.add_argument("--expected-intent", required=True, type=str, help="Intent corresponding to transcript")

    # Slack related - for posting messages and fetching via chat_slack)
    parser.add_argument(
        "--slack-access-token", default=slack_access_token, help="Access token to post messages to GK workspace"
    )
    parser.add_argument(
        "--channel-name",
        default="ageojo_test",
        type=str,
        help="Name of slack channel in GK workspace to post/get chats"
    )
    parser.add_argument(
        "--channel-id",
        default="CEXMKJAJH",
        type=str,
        help="Name of slack channel id corresponding to channel_name; used by chat_slack to retrieve chats"
    )
    parser.add_argument(
        "--max-pages",
        default=1,
        type=int,
        help="Number of pages for chat_slack to retrieve (default page "
        "has 100 chats)"
    )
    parser.add_argument("--count", default=1, type=int, help="Number of chats to retrieve")
    parser.add_argument(
        "--latest-ts",
        default=time_now,
        type=float,
        help="Timetamp (epoch time). All chats retrieved "
        "will "
        "have "
        "been posted "
        "by "
        "this time or earlier"
    )
    # Request related params
    parser.add_argument(
        "--max-tries",
        default=5,
        type=int,
        help="Number of times to retry posting to service. Used for all GET/POST requests"
    )
    parser.add_argument(
        "--delay", default=3, type=int, help="Number of seconds to wait before sending request to same url"
    )
    parser.add_argument(
        "--timeout",
        default=10,
        type=int,
        help="Number of seconds to wait before terminating request if no response from server"
    )

    parser.add_argument("--outfile", default=None, help="Name of JSON file to save discover output")
    # args = parser.parse_args()
    return parser


def batch_opts(parser):
    parser.add_argument("--tests", default="tests.txt", help="File containing test data tests.txt format")
    parser.add_argument(
        "--chat-segments",
        default="ageojo_chat_segments.json",
        help="File containing chat_segments "
        "from chat_slack to post to discovery"
    )
    return parser


def single_test(parser):
    parser.add_argument("--test-no", required=True, type=int, help="Unique number for test of this transcript")

    parser.add_argument(
        "--transcript",
        required=True,
        type=str,
        help="Transcript to post to chat, retrieve via chat_slack, and after processing, post chat_segment to discovery"
    )
    parser.add_argument("--expected-intent", required=True, type=str, help="Intent corresponding to transcript")
    return parser


def get_env_opts():
    parser = general_opts()
    parser = single_test(parser=parser)
    # parser = batch_opts(parser=parser)
    return parser


# parser = get_env_opts()
# parser.print_help()
# parser.parse_args()
