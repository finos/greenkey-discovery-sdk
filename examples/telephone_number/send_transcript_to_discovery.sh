#!/bin/bash

curl -X POST http://localhost:1234/process  \
     -H "Content-Type: application/json" \
     -d '{"transcript": "You can reach me at five five five four three two five nine eight one"}'
