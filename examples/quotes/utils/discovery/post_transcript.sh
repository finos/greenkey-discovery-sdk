#!/bin/bash

DISCOVERY_PORT=8003
TRANSCRIPT="ninety four months one payer three mine versus ninety three three billion"
TAG="local"


curl -X POST http://localhost:DISCOVERY_PORT/discovery:$TAG  \
     -H "Content-Type: application/json" \
     -d '{"transcript": ${TRANSCRIPT}}' 
