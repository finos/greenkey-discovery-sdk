#!/bin/bash

# change PORT and  name of CHANNEL_NAME as desired as well as name of file that JSON prettified data is written too
curl -X POST localhost:8005/process -H "Content-Type: application/json"  --data '{"service_type":"slack", "params":{"channel_name":"ageojo_test"}}' | jq . > ageojo_test_latest.json
