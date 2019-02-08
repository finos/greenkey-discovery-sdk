#!/bin/bash

curl -X POST http://localhost:1234/discover  \
     -H "Content-Type: application/json" \
     -d '{"transcript": "I will buy 70 purple carrots for $10 each"}'
