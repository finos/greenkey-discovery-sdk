#!/bin/bash

curl -X POST http://localhost:1234/discover  \
  -H "Content-type: multipart/form-data" \
  -F 'data={"intent":"room_dialing", "json_lattice": {"transcript": "dial one eight"}};type=application/json'
