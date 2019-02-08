#!/usr/bin/env bash

PORT=1234

TRANSCRIPT="I'll buy 70 purple carrots for \$10 each"

curl -X POST http://localhost:$PORT/discover  \
     -H "Content-Type: application/json" \
     -d '{"transcript": $TRANSCRIPT}'
