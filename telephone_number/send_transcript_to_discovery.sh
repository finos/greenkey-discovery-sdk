#!/bin/bash

curl -X POST http://localhost:1234/discover  \
  -H "Content-type: multipart/form-data" \
  -F 'data={"intent":"room_dialing", "json_lattice": {"transcript": "You can reach me at five five five four three two five nine eight one"}};type=application/json'
