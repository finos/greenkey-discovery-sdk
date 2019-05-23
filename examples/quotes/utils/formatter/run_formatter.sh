#!/bin/bash

curl -X POST http://localhost:8002/process \
     -H "Content-type: application/json" \
     -d '{"intents":["directions"], "transcript": I need directions to fifty five um west monroe by bus"}'
