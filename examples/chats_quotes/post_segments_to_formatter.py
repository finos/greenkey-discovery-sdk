import requests
import os
import sys
import json
import pprint as pp
from collections import defaultdict
from pathlib import Path

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Tested and verified with:
#infile = "0_quote.json"
#outfile = "test_formatted_quotes_10.txt"
#data = json.load(open(infile, 'r+'))
# out = post_to_formatter(data)
# pp.pprint(out)
############################################




###################################


MAX_TRIES = max_tries = 5
FORMATTER_PORT = formatter_port = 8005
print(formatter_port)


def load_json(infile):
  return json.load(open(infile, 'r+'))


def dump_json(data, outfile):
  json.dump(open(outfile, 'w+'))


def post_to_formatter(data): #(transcript, test_no, expected_intent):
  url = "http://localhost:{}/process".format(FORMATTER_PORT)

  #outfile = "{}_test_formatted_{}_10.txt".format(test_no, expected_intent)

  headers = {"Content-type":"application/json"}
  #data = {"transcript": transcript}
  for i in range(MAX_TRIES):
    try:
      r = requests.post(url, headers=headers, json=data, timeout=10)
      if r.status_code == 200:
         output = r.json()
         return output
         #json.dump(output, open(outfile, 'w+'))
    except Exception as e:
      print("Exception: {}".format(e))
      msg = "Failed Test: {}".format(test_no)
     # logger.error(msg)
      print(msg)
  return {}



project_dir = os.getcwd()
data_dir = os.path.join(project_dir, 'results/quotes')

project_dir = Path.cwd()
results_dir = project_dir / 'results'
assert results_dir.exists() and results_dir.is_dir()


quotes_dir = results_dir / 'quote'
assert quotes_dir.exists() and quotes_dir.is_dir()



#list_of_fpaths = quotes_dir.glob("*.json")



def format_all(list_of_fpaths, verbose=True):
  results = []
  for i, infile in enumerate(list_of_fpaths):
    data = load_json(infile)
    try:
      out = post_to_formatter(data)
      if verbose:
        pp.pprint(out)
      outfile = "formatted_{}.json".format(infile.stem)
      dump_json(outfile, out)
      results.append(out)
    except Exception as e:
      logger.exception("Failed: {}".format(infile))
  return results


quotes_dir = str(quotes_dir)

list_of_files = [os.path.join(quotes_dir, filename) for filename in sorted(os.listdir(quotes_dir)) if filename.endswith(".json")]


list_of_fpaths = list_of_files[0:5]

print(list_of_fpaths)


#results = format_all(list_of_fpaths, verbose=True)

#print()
#print("Results: \n")
#pp.pprint(results)


#dump_json(results, "foo.json")
