#!/usr/bin/env python3

import os
import random
import sys
from os.path import basename, dirname, exists
from os.path import join as join_path, isfile as is_file
from pathlib import Path

# get test files for quotes & not_quotes as well as name of file to write test results
#try:
#  quotes_test_file = sys.argv[1]
#  not_quotes_test_file = sys.argv[2]
#  outfile = sys.argv[3]
#except IndexError:
#  quotes_test_file = 'test_quotes_20.txt'
#  not_quotes_test_file = 'test_not_quotes_20.txt'
#  outfile = 'tests.txt' #'test_quote_or_not_10.txt'

#try:  
#  assert exists(quotes_test_file) and is_file(quotes_test_file)
#  assert exists(not_quotes_test_file) and is_file(not_quotes_test_file)
#except FileNotFoundError as e:
#  print("Test file cannot be located: {}".format(e))
#  sys.exit(1)


try:
  directory = sys.argv[1]
except IndexError:
  directory = os.getcwd()

try:
  outfile = sys.argv[2]
except IndexError:
  outfile ="tests.txt"

SHUFFLE=False

TEST_SIZE=10


quotes_test_file = join_path(directory, "test_quotes_{}.txt".format(TEST_SIZE)) 
not_quotes_test_file = join_path(directory, "test_not_quotes_{}.txt".format(TEST_SIZE)) 

#assert exists(quotes_test_file) and is_file(quotes_test_file)
#assert exists(not_quotes_test_file) and is_file(not_quotes_test_file)


# get lines from test files for quotes and not quotes
quote_transcripts = [('quote', line.strip()) for line in open(quotes_test_file, 'r+') if line.strip()]
not_quote_transcripts = [('not_quote', line.strip()) for line in open(not_quotes_test_file, 'r+') if line.strip()]

# combine quote and not quote transcripts (str) & shuffle tests.txt will not be blocked by intent type
transcripts = quote_transcripts + not_quote_transcripts


if SHUFFLE:
  random.shuffle(transcripts)


# write to file: format tests.txt for launch_discovery.py tests
with open(outfile, 'w+') as fw:
  for test_no, (intent, transcript) in enumerate(transcripts):
    fw.writelines('test: quotes_not_quotes {}\n'.format(test_no))
    fw.writelines('intent: {}\n'.format(intent))
    fw.writelines('transcript: {}\n\n'.format(transcript))

#print("Successfully generated tests.txt in {} directory".format(abspath(dirname(outfile))))
