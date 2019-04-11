import requests
import os
import sys
import json


infile = 'ageojo_test_latest.json'

data = json.load(open(infile, 'r+'))

#print(data)


#discovery_port = PORT = sys.argv[1]

PORT = discovery_port = 8006

url = "http://localhost:{}/process".format(discovery_port)
r = requests.post(url, json=data)

print(r.text)
