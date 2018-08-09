#!/bin/bash

curl -X POST http://localhost:1234/discover  \
  -H "Content-type: multipart/form-data" \
  -F 'data={"intent":"calling_room", "json_lattice": {"transcript": "five a is calling thirteen c"}};type=application/json'
