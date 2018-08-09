#!/bin/bash

curl -X POST http://localhost:1234/discover  \
  -H "Content-type: multipart/form-data" \
  -F 'data={"intent":"room_dialing", "json_lattice": {"transcript": "I need directions to fifty five west monroe avenue by car"}};type=application/json'
