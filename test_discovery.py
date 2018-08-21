#!/usr/bin/python
'''
Test Discovery performs system testing of new intents and interpreters.

This tool is intended to be distributed to any developer who wishes to develop their own
Discovery interpreter.

Tests are assumed to pass if the defined entities are present in the most
likely found intent. Tests are also assumed to always return a valid intent
with entities.
'''

from __future__ import print_function
import requests
import subprocess
import json
import os
import time
import glob
import sys

from importlib import import_module
from discovery_utils import validate_entity_definition
from discovery_config import *

if len(sys.argv) > 1:
  if sys.argv[1].startswith("/"):
    DISCOVERY_DIRECTORY = sys.argv[1]
  else:
    DISCOVERY_DIRECTORY = os.getcwd() + "/" + sys.argv[1]
else:
  DISCOVERY_DIRECTORY = os.getcwd()

TEST_FILE = DISCOVERY_DIRECTORY + "/tests.txt"
'''
Functions for handling the Discovery Docker container
'''


def check_discovery_status():
  '''
  Checks whether Discovery is ready to receive new jobs
  '''
  r = requests.get("http://{}:{}/status".format(DISCOVERY_HOST, DISCOVERY_PORT))

  if json.loads(r.text)['status'] == 0:
    return True

  return False


def wait_for_discovery_status(timeout=1, retries=5):
  '''
  Wait for Discovery to be ready
  '''
  for i in range(retries):
    try:
      check_discovery_status()
      return True
    except Exception:
      time.sleep(timeout)

  return False


def launch_discovery():
  '''
  Launches the Discovery engine Docker container
  '''
  launch_command = ' '.join(
    ["docker", "run", "--rm", "-d", "--name", "discovery-dev"] + \
    ["-v", "{}/custom:/custom".format(DISCOVERY_DIRECTORY), \
     "-v", "{}/dico:/dico".format(DISCOVERY_DIRECTORY), \
     "-p", "{}:1234".format(DISCOVERY_PORT)] + \
    ["-e {}='{}'".format(k, v) for k, v in DISCOVERY_CONFIG.iteritems()] + \
    ["docker.greenkeytech.com/discovery"]
  )

  print("Launching Discovery: {}\n".format(launch_command))

  subprocess.call(launch_command, shell=True)


def wait_for_discovery_launch():
  '''
  Wait for launch to complete
  '''

  # Timeout of 25 seconds for launch
  if not wait_for_discovery_status(timeout=5, retries=5):
    print("Couldn't launch Discovery, printing Docker logs:\n---\n")
    subprocess.call("docker logs discovery-dev", shell=True)
    subprocess.call("docker stop discovery-dev", shell=True)
    exit(1)


def shutdown_discovery():
  '''
  Shuts down the Discovery engine Docker container
  '''
  r = requests.get("http://{}:{}/shutdown".format(DISCOVERY_HOST, DISCOVERY_PORT))


'''
Testing functions
'''


def load_tests():
  '''
  Loads and parses the test file
  '''
  test_file = [x.rstrip() for x in open(TEST_FILE)]

  tests = []
  current_test = {}
  for line in test_file:
    key = line.split(":")[0]
    value = line.split(": ")[-1]
    if key == "test":
      if len(current_test.keys()) > 0:
        tests.append(current_test)
      current_test = {key: value}
    elif len(key) > 0:
      current_test[key] = value

  if len(current_test.keys()) > 0:
    tests.append(current_test)

  return tests


def submit_transcript(transcript):
  '''
  Submits a transcript to Discovery
  '''
  d = {"data": json.dumps({"json_lattice": {"transcript": transcript}})}
  r = requests.post("http://{}:{}/discover".format(DISCOVERY_HOST, DISCOVERY_PORT), data=d)

  return json.loads(r.text)


def test_single_case(test):
  failed = False
  print("======\nTesting: {}".format(test['test']))
  resp = submit_transcript(test['transcript'])

  # Fail if a failure response was received
  if "result" in resp and resp['result'] == "failure":
    fail_test(resp)

  if "intents" not in resp:
    fail_test(resp)

  if "entities" not in resp["intents"][0]:
    fail_test(resp)

  # For now, only keep the first intent:
  intent = resp["intents"][0]

  # Get all values of entities
  entities = {x["label"]: x["matches"][0][0]["value"] for x in intent["entities"]}

  for key, value in test.items():
    if key in ['test', 'transcript']:
      continue
    if key not in entities.keys():
      fail_test(resp, "Entity not found: {}".format(key), continued=True)
      failed = True
      errors += 1
      continue
    if entities[key] != value:
      fail_test({}, "Value incorrect: ({}) expected {} != {}".format(key, value, entities[key]), continued=True)
      failed = True
      errors += 1

  extra_entities = {x: entities[x] for x in entities.keys() if x not in test.keys()}

  if len(extra_entities) > 0:
    print("Extra entities: {}\n".format(extra_entities))

  if failed:
    return (1, errors)
  else:
    print("Test passed\n---\n")
    return (0, 0)


def test_all():
  '''
  Runs all defined tests
  '''
  tests = load_tests()

  t1 = int(time.time())

  total_tests = len(tests)
  failed_tests = 0
  errors = 0

  for test in tests:
    (failure, errors) = test_single_case(test)
    failed_tests += failure
    errors += errors

  print(
    "\n---\n({} / {}) tests passed in {}s with {} errors".format(
      total_tests - failed_tests, total_tests, int(time.time()) - t1, errors
    )
  )


def fail_test(resp, message="", continued=False):
  print("Test failed: " + message)
  print("{}\n---\n".format(resp))

  if not continued:
    subprocess.call("docker logs discovery-dev", shell=True)
    subprocess.call("docker stop discovery-dev", shell=True)
    exit(1)


'''
Interpreter validation
'''


def validate_entities():
  '''
  Validate entities
  '''
  entities = glob.glob(DISCOVERY_DIRECTORY + "/custom/entities/*.py")
  sys.path.append(DISCOVERY_DIRECTORY + "/custom/entities")

  for entity in entities:
    if '__init__' in entity:
      continue
    entity_module = import_module(entity.split("/")[-1].replace(".py", ""))
    if 'ENTITY_DEFINITION' in dir(entity_module):
      validate_entity_definition(entity_module.ENTITY_DEFINITION)
    os.remove(entity.replace(".py", ".pyc"))


def validate_json():
  '''
  Validate intents.json
  '''
  try:
    json_object = json.loads(''.join([x.rstrip() for x in open(DISCOVERY_DIRECTORY + "/custom/intents.json")]))
  except Exception as e:
    print("Invalid intents.json")
    print("Error: {}".format(e))
    exit(1)
  return True


if __name__ == '__main__':
  validate_entities()
  validate_json()

  launch_discovery()
  wait_for_discovery_launch()

  if wait_for_discovery_status():
    print("Discovery Ready")

  test_all()

  shutdown_discovery()
