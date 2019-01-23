#!/bin/bash

curl -X POST http://localhost:1234/discover  \
     -H "Content-Type: application/json" \
     -d '{"transcript": "I need directions to fifty five west monroe avenue by car"}'
