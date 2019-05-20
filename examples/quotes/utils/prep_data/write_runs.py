#!/usr/bin/env python3

import os
import random
import json
from os.path import basename, dirname, exists
from os.path import join as join_path, isfile as is_file
from asrtoolkit.clean_formatting import clean_up


def json_load(infile):
    return json.load(open(infile, 'r+'))
def json_dump(data, outfile):
    return json.dump(data, open(outfile, 'w+'))

os.getcwd()

def get_directory():
    root_dir = os.getcwd()
    if basename(root_dir) == 'greenkey-discovery-sdk-private':
        quotes_dir = join_path(root_dir, 'examples', 'quotes')
    elif basename(root_dir) == 'quotes':
        quotes_dir = root_dir
        root_dir = dirname(dirname(quotes_dir))
        assert basename(root_dir) == 'greenkey-discovery-sdk-private'
    else:
        raise Exception('Need to be in quotes directory')
    return quotes_dir



def unformat(infile):
    """
    :param infile: str, path to txt file
    :return: returns List[Dict]
        unformats each line in infile and represents original & unformatted via dict
        2 keys: 'formatted': original text | 'unformatted': clean_up(orignal text)
        using asrtoolkit.clean_formatted.clean_up
    """
    with open(infile, 'r+') as f:
        return [
            {'formatted': " ".join(line.strip().split()),
             'unformatted': line.strip()
             }
                for line in f.readlines() if line.strip()
        ]



def write_test_data(quotes_test_file, not_quotes_test_file, outfile, shuffle=False):
    # get lines from test files for quotes and not quotes
    quote_transcripts = [('quote', line.strip()) for line in open(quotes_test_file, 'r+') if line.strip()]
    not_quote_transcripts = [('not_quote', line.strip()) for line in open(not_quotes_test_file, 'r+') if line.strip()]

    # combine quote and not quote transcripts (str) & shuffle tests.txt will not be blocked by intent type
    transcripts = quote_transcripts + not_quote_transcripts

    if shuffle:
        random.shuffle(transcripts)

    # write to file: format tests.txt for launch_discovery.py tests
    with open(outfile, 'w+') as fw:
        for test_no, (intent, transcript) in enumerate(transcripts):
            transcript = ' '.join([s.strip() for s in transcript.strip().split()])
            fw.writelines('test: quotes_not_quotes {}\n'.format(test_no))
            fw.writelines('intent: {}\n'.format(intent))
            fw.writelines('transcript: {}\n\n'.format(transcript))
    print("Wrote file: {}".format(outfile))


if __name__ == '__main__':

    directory = get_directory()
    assert exists(directory)
    runs_dir = join_path(directory, 'runs_customer_data')
    assert exists(runs_dir)

    security = 'security_db.txt'
    imstrings = 'imstrings/unformatted_imstrings.txt'


    infile = imstrings
infile
    unformatted_imstrings = unformat(infile)

formatted_security = 'security/formatted_security_db.txt'
unformatted_security = 'security/unformatted_security_db.txt'

infile = unformatted_security
    quotes_test_file = infile = join_path(runs_dir, infile)
quotes_test_file
    # use not quotes test data from textclassifiers
    # not_quotes_test_file = 'formatted_test_not_quotes_10.txt'
    # not_quotes_test_file = join_path(directory, not_quotes_test_file)

stem = 'security_db'
    outfile = 'unformatted_runs_{}_tests.txt'.format(stem)
    outfile = join_path(runs_dir, outfile)
quotes_test_file
infile


assert exists(runs_dir)

security_infile = 'security_db.txt'
security_infile = join_path(
    directory, runs_dir, 'raw_data', security_infile
)
assert exists(security_infile)




################################################################################
# See if unformatted version of security_db.txt will work well if round digits
################################################################################

def format_to_unformat_mapper(data, precision=3):
    list_of_dicts = []
    for ddict in data:
        formatted = ddict['formatted']
        unformatted = ddict['unformatted']

        formatted_list = formatted.strip().split()

        rounded_list = []
        for elem in formatted_list:
            if '.' in elem and elem.count('.')==1 and elem.replace(".", "").isdigit():
                rounded_elem = round(float(elem), precision)
                elem = str(rounded_elem)
            rounded_list.append(elem)
        formatted_rounded = ' '.join(rounded_list)
        # use clean_up to unformat the rounded version and add to list
        ddict['unformatted_round_{}'.format(precision)] = clean_up(formatted_rounded)
        list_of_dicts.append(ddict)
    return list_of_dicts


# Write txt file    #TODO Note hardcoded file names
def dict_to_txt_file(list_of_dicts, precision):
    rounded_lines = []
    for ddict in list_of_dicts:
        unfmt_round = ddict['unformatted_round_{}'.format(precision)]
        rounded_lines.append("{}\n".format(unfmt_round))
        # List of strings List[str]

    # Write to txt file
    outfile_round = 'unformatted_security_db_round_{}.txt'.format(precision)
    outfile_round = join_path(runs_dir, 'security', outfile_round)

    with open(outfile_round, 'w+') as f:
        f.writelines(rounded_lines)
    return outfile, rounded_lines


# TODO - incorporate the rounding with the generation of the formatted-unformatted mapper JSON to begin with
# TAKES previously created dict & adds additional key with rounded values - unformatted
# then saves both the dict and the text file
def unformat_and_round_runs(file, precision=3):
    # '/home/amelie/src/greenkey-discovery-sdk-private/examples/quotes/runs_customer_data/security/formatted_and_unformatted_security_db.json'
    # file = join_path(runs_dir, 'security', 'formatted_and_unformatted_security_db.json')
    assert exists(file)
    data = json_load(file)
    list_of_dicts = format_to_unformat_mapper(data, precision=precision)
    # TODO - this should be done once -- earlier when creating dict
    # save as JS   ON -> List[Dict], one Dict per line in original file
    json_dump(list_of_dicts, outfile=file.replace(".json", "_2.json"))
    # Now create text file
    outfile, rounded_lines = dict_to_txt_file(list_of_dicts, precision=precision)
    # return outfile, rounded_lines, list_of_dicts

##########################################################################

file = join_path(runs_dir, 'security', 'formatted_and_unformatted_security_db.json')
unformat_and_round_runs(file, precision=3)
##########################################################################

# Write to txt file
precision=3
outfile_round = 'unformatted_security_db_round_{}.txt'.format(precision)
outfile_round = join_path(runs_dir, 'security', outfile_round)
assert exists(outfile_round)

security_infile = outfile_round
exists(security_infile)

# tests.txt file: write unformated tests for security_db.txt but with floats rounded to 3 places
outfile = 'unformatted_security_db_round_{}_tests.txt'.format(precision)
outfile = join_path(runs_dir, outfile)


# unformatted not_quotes -> test data (10% from textclassifiers)
unformatted_not_quotes_test_file_10 = join_path(
    directory, 'train90_test10_data',
    'unformatted', 'unformatted_test_not_quotes_10.txt'
)
assert exists(unformatted_not_quotes_test_file_10)


quotes_test_file = security_infile
not_quotes_test_file = unformatted_not_quotes_test_file_10

assert exists(quotes_test_file) and is_file(quotes_test_file)
assert exists(not_quotes_test_file) and is_file(not_quotes_test_file)
# not_quotes_test_file

write_test_data(quotes_test_file=quotes_test_file,
                not_quotes_test_file=not_quotes_test_file,
                outfile=outfile,
                shuffle=False)



# (1) create json file -> List[dict], each dict contains 'unformatted' and 'formatted'
#      key 'formatted' contains original run string
#      key 'unformatted' is clean_up(run_string)
#
# (2) create txt files containing the unformatted data
#     filename is same as original with 'unformatted' as prefix

# import json
#
# imstrings = 'imstrings.txt'
# imstrings = join_path(runs_dir, imstrings)
# unformatted_imstrings = unformat(infile=imstrings)
# outfile = 'formatted_and_unformatted_imstrings.json'
# json.dump(unformatted_imstrings, open(join_path(runs_dir, outfile), 'w+'))
#
#
#
# security = 'security_db.txt'
# security = join_path(runs_dir, security)
# unformatted_security = unformat(infile=security)
# outfile = 'formatted_and_unformatted_security_db.json'
# unformatted_security[0]['formatted']
# unformatted_security[0]['unformatted']
# json.dump(unformatted_security, open(join_path(runs_dir, outfile), 'w+'))
#
# list_of_tuples = unformatted_security
#
# list_of_tuples = unformatted_imstrings
# infile = imstrings
#
# outfile = 'unformatted_{}'.format(infile)
# outfile = join_path(runs_dir, outfile)
# print(outfile)
# # outfile = join_path(runs_dir, outfile.replace('.json', '.txt'))
# outfile
#
# with open(outfile, 'w+') as fw:
#     for data_dict in list_of_tuples:
#         unformatted = data_dict['unformatted']
#         fw.write("{}\n".format(unformatted))

##################################################################
# raw data from runs
security_infile = 'security_db.txt'
security_infile = join_path(runs_dir,'raw_data', security_infile)
assert exists(security_infile) and is_file(security_infile)

# creates mapping between formatted & unformatted -> only difference from current is that numbers are rounded
n = 2
unformatted_security_round3 = unformat(infile=security, precision=n)
outfile = 'formatted_and_unformatted_security_db_round_().json'.format(n)
outfile = join_path(runs_dir, 'security', outfile)
json.dump(unformatted_security_round3, open(outfile, 'w+'))


list_of_tuples = unformatted_security_round3


directory = os.getcwd()
assert basename(directory)=='quotes'
# from text classifiers --> use for negative exemplars for test
unformatted_test_not_quotes_10 = join_path(
    directory, 'train90_test10_data',
    'unformatted', 'unformatted_test_not_quotes_10.txt'
)



infile = 'formatted_and_unformatted_security_db.json'
security_json = json.load(open(infile, 'r+'))












