#!/bin/bash


CHANNEL_ID="CEXMKJAJH"
SLACK_PASSWORD="xoxp-4953937137-344679330118-509400138422-a20f349799113ba21f5c91e8a190cd14"


#curl -X POST -H 'Authorization: Bearer xoxp-4953937137-344679330118-509400138422-a20f349799113ba21f5c91e8a190cd14' \
#        -H 'Content-type: application/json' \
#        --data '{"channel": "EXMKJAJH", "text": "This is a test"}' \
#        https://slack.com/api/chat.postMessage

curl -X POST -H "Authorization: Bearer ${SLACK_PASSWORD}" \
	-H 'Content-type: application/json' \
	--data '{"channel": "'${CHANNEL_ID}'", "text": "This is a test", "as_user":"true"}' \
	https://slack.com/api/chat.postMessage
