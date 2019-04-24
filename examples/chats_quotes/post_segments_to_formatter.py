import requests
import os
import sys
import json
import time
import pprint as pp
from collections import defaultdict
from pathlib import Path
from os.path import dirname, basename, exists, join as join_path

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

#INPUT_DIR = sys.argv[1]
#OUTPUT_DIR = sys.argv[2]

###################################


MAX_TRIES = max_tries = 5
FORMATTER_PORT = formatter_port = 8005
print(formatter_port)


def load_json(infile):
  return json.load(open(infile, 'r+'))


def dump_json(data, outfile):
  json.dump(data, open(outfile, 'w+'))


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
      time.sleep(10)
     # logger.error(msg)
      print(msg)
  return {}



#project_dir = os.getcwd()
#data_dir = os.path.join(project_dir, 'results/quotes')

#project_dir = Path.cwd()
#results_dir = project_dir / 'results'
#assert results_dir.exists() and results_dir.is_dir()


#quotes_dir = results_dir / 'quote'
#assert quotes_dir.exists() and quotes_dir.is_dir()



#list_of_fpaths = quotes_dir.glob("*.json")



def format_all(list_of_files, output_dir=None, verbose=True):
  results = []
  for i, infile in enumerate(list_of_files):
    if i==0 or i%25==0:
      print("\nFile Number {}: {}\n".format(i, infile))
    data = load_json(infile)
    try:
      out = post_to_formatter(data)
      if verbose:
        if i==0 or i%25==0:
          pp.pprint(out)
      outfile = "formatted_{}".format(basename(infile))  # file.json <- basename
      if output_dir:
        outfile = join_path(output_dir, outfile)
      dump_json(out, outfile) #outfile, out)
      results.append(out)
    except Exception as e:
      logger.exception("\nFailed: {}\n".format(infile))
  return results




#quotes_dir = str(quotes_dir)

def get_files(input_dir):
  list_of_files = [join_path(input_dir, filename) for filename in sorted(os.listdir(input_dir)) if filename.endswith(".json")]
  return list_of_files



# see sample of files
#list_of_fpaths = list_of_files[0:5]
#print("\nSample File names: {}\n".format(list_of_fpaths))


# RUN FORMATTER

if __name__ == "__main__":
  
  intent_dir = os.getcwd()
  INPUT_DIR = join_path(intent_dir, "unformatted")
  OUTPUT_DIR = join_path(intent_dir, "formatted") 

  print("\nStarting Formatter\n")
  list_of_files = get_files(input_dir=INPUT_DIR)
  print(list_of_files[:5], "\n")

  results = format_all(list_of_files, output_dir=OUTPUT_DIR,  verbose=True)



#print()
#print("Results: \n")
#pp.pprint(results)


#dump_json(results, "foo.json")
