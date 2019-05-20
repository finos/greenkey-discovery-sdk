import requests
import os
import sys
import json


#infile = 'ageojo_test_latest.json'
#data = json.load(open(infile, 'r+'))
#print(data)

infile = "0_quote.json"

data = json.load(open(infile, 'r+'))

data = {"segments": data["segments"][0]}

print(data)

PORT = formatter_port = 8002
print(formatter_port)

url = "http://localhost:{}/process".format(formatter_port)

headers = {"Content-type":"application/json"}

try:
  r = requests.post(url, headers=headers, json=data)
except Exception as e:
  print("Exception: {}".format(e))


print(r.status_code)

#print(r.json())
print(r.text)
