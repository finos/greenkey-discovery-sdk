import json
import os
import random
import subprocess
import sys
from os.path import join as join_path, basename, dirname, exists, isfile as is_file, isdir as is_dir
from pathlib import Path


def get_data(quotes_dir, files):
  """
  :param quotes_dir: str, path to directory to save downlaoded data
  :param files: List[str]; names of downloaded files to keep;
    rest of the files in the directory will be removed
  :param ext: extension; when given,
    all files with that extension will be removed
    except those specified in `files`
  :return:
  """
  cmd = "gsutil -m cp gs://gk-transcription.appspot.com/model_training_data/quotes/quote_or_not_classifier/*.txt ."
  subprocess.call(cmd, shell=True)

  for file in os.listdir(quotes_dir):
    if not file in files and is_file(file) and file.endswith('.txt'):
      os.remove(join_path(quotes_dir, file))


def concat_data(outfile, list_of_files):
  """
  :param outfile: path to file to save output
  :param args: List[str], file names
  :return: concatenates lines from all files passed in list of args
    (provided file exists and is a .txt file)
    if outfile is provided, writes data to file
    else returns data
  data: str; "\n" char to separate each line (as in original file)
  """
  from itertools import chain
  data = list(chain.from_iterable([Path(infile).read_text().splitlines() for infile in list_of_files if exists(infile) and is_file(infile) and infile.endswith('.txt')]))
  Path(outfile).write_text(data="\n".join(data).strip("\n"))



def shuffle_and_split_data(infile, size=0.9):
  """
  :param infile: str, path to txt file containing new-line separated strings
  :param size: float; split-size, default 0.9
  """
  with open(infile, 'r+', encoding='utf-8') as f:
    data = [line.strip() for line in f.readlines()]
    random.shuffle(data)
    train_size = int(len(data) * size)
    train, test = data[:train_size], data[train_size:]
    return train, test


def write_file(outfile, data):
  """
  :param outfile: str, path to file to write data
  :param data: List[str]
  :return: writes data to outfile
    each line in list is a new line in the output file
  """
  with open(outfile, 'w+', encoding='utf-8') as f:
    for line in data:
      f.write("{}\n".format(line))


def train_test_split_and_write(directory=None, train_dir=None, test_dir=None, size=0.9, ext='.txt'):
  """
  :param directory: str, directory containing data files
  :param train_dir: directory to save training data
  :param test_dir: str, directory to save test data
  :param size: float, proportion of data to use for training
  :param ext: str, file extension; used to filter directory for data files
  :return: splits each file in directory into train/test data sets with size proportion of the data for training
    saves files to train and test directory with filenames formatted like: `train_quotes_90.txt` and `test_not_quotes_10.txt`
  """
  if not directory:
    directory = os.getcwd()

  data_files = [join_path(directory, f) for f in os.listdir(directory) if f.endswith(ext)]

  train_files, test_files = [], []
  for infile in data_files:
    train, test = shuffle_and_split_data(infile, size)

    stem = basename(infile).split('.')[0]
    if not train_dir:
      train_dir = dirname(infile)
    train_outfile = join_path(train_dir, "train_{}_{}.txt".format(stem, int(size * 100)))

    if not test_dir:
      test_dir = dirname(infile)
    test_outfile = join_path(test_dir, "test_{}_{}.txt".format(stem, int(100 - size * 100)))

    write_file(data=train, outfile=train_outfile)
    write_file(data=test, outfile=test_outfile)

    train_files.append(train_outfile)
    test_files.append(test_outfile)
  return train_files, test_files


#TODO modify to take in test file names from train_test_split_write
def write_tests(test_files=None):
  """
  generates tests.txt file from the quotes test file and the not_quotes test file
  default: test_quote_{n}.txt and test_not_quote_{n}.txt where n is the (1-TRAIN_SIZE)*100
  """
  TEST_SIZE = 100 - int(100 * TRAIN_SIZE)
  quotes_test = "test_quotes_{}.txt".format(TEST_SIZE)
  not_quotes_test = "test_not_quotes_{}.txt".format(TEST_SIZE)

  if test_files:
    quotes_test, not_quotes_test = test_files[0], test_files[1]

  test_outfile = 'tests.txt'

  print("Writing `tests.txt` file in `quotes/` directory")
  try:
    subprocess.call("python write_test_data.py {} {} {}".format(quotes_test, not_quotes_test, test_outfile), shell=True)
  except (ValueError, FileNotFoundError) as e:
    print(e)
  print("Trying to write `tests.txt` file with default file names...")
  try:
    subprocess.call("python write_test_data.py", shell=True)
  except:
    print("Test could not be written")
  if 'tests.txt' in os.listdir(DIRECTORY):
    print("Test File Written")
    print(Path('tests.txt').read_text().splitlines()[0])
  # Remove separate quote and not_quote test files (with 10%
    #try:
    #  os.remove(quotes_test)
    #  os.remove(not_quotes_test)
    #except (ValueError, FileNotFoundError) as e:
    #  print("Could not remove file: {}".format(e))

  print("Files in `quotes` directory:\n {}".format(os.listdir(DIRECTORY)))

  ###################################################################
  # generate intents.json in `quotes/custom` directory

def write_intents_config():
  """
  generates `intents.json` file in `quotes/custom` directory
    expects environment var `DIRECTORY` to contain a directory `custom`
  :return: saves JSON file intents.json with intent to be classified and paths to training data
  """
  # create custom directory if it does not exist; it should already exist and contain training files
  custom_dir = join_path(DIRECTORY, 'custom')
  os.makedirs(custom_dir, exist_ok=True)

  # TODO generalize to accomodate n number of intents and training files
  train_n = int(TRAIN_SIZE*100)
  train_quotes = "train_quotes_{}.txt".format(train_n)#(TRAIN_SIZE*100)
  train_not_quotes = "train_not_quotes_{}.txt".format(train_n)#TRAIN_SIZE*100)

  training_data = [train_quotes, train_not_quotes]

  intents_config = {
    "intents":
      [
        dict(
          label='quote',
          domain='quote_or_not',
          examples=["/custom/{}".format(train_quotes)]
        ),
        dict(label='not_quote',
             domain='quote_or_not',
             examples=["/custom/{}".format(train_not_quotes)])
      ]
  }

  DEFINITIONS_FILENAME = 'intents.json'
  try:
    print("Writing {} file".format(DEFINITIONS_FILENAME))
    definitions_infile = join_path(custom_dir, DEFINITIONS_FILENAME)
    json.dump(intents_config, open(definitions_infile, 'w+'))
  except:# AssertionError:   # TODO other error for failure to write file?
    print("Failed to write 'intents.json'. File must be added for model training")
  try:
    assert all(
      [exists(join_path(custom_dir, intent_file)) in os.listdir(custom_dir)
       for intent_file in training_data]
    )
  except AssertionError:
    print("The `custom/` directory must {} and all training files named exactly as specified. If any files are missing or data file paths are invalid, Discovery will NOT train an intents classifier upon launch".format(DEFINITIONS_FILENAME))



def main():
  """
  DIRECTORY: str, path to the quotes interpreter directory examples/quotes

  FILES: dict, keys are 'quote' and 'not_quote'; corresponding value is a List[str]
    with each string specifying the *name* of a file containing data
  """
  data_dir, custom_dir = join_path(DIRECTORY, 'data'), join_path(DIRECTORY, 'custom')
  assert exists(data_dir) and is_dir(data_dir) and exists(custom_dir) and is_dir(custom_dir)

  # names of files containing quote and not quote data
  quote_files, not_quote_files = FILES['quote'], FILES['not_quote']

  # (1) GET DATA data from gcloud to quotes_dir;l then remove all .txt files not in list `files`
  get_data(DIRECTORY, files=quote_files + not_quote_files)

  # (2) create quotes and not_quotes.txt files in data_dir with data from all relevant files
  data_grouped = [  # (outfile, args),
    ('quotes.txt', quote_files),
    ('not_quotes.txt', not_quote_files)
  ]
  for filename, list_of_files in data_grouped:
    concat_data(outfile=join_path(data_dir, filename), list_of_files=list_of_files)
  try:
    assert sorted([data_grouped[0][0], data_grouped[1][0]]) == sorted(os.listdir(data_dir))
  except AssertionError:
    print("Files in data directory:\n {}".format(os.listdir(data_dir)))

  # remove raw data files if they exist --> REMOVE BEFORE generating test data files in quotes_dir
  for file in quote_files + not_quote_files:
    try:
      os.remove(file)
    except FileNotFoundError:
      continue

  # (3) shuffle quotes/not quotes and split into train/test & write to files (saved to data_dir)
  train_files, test_files = train_test_split_and_write(directory=data_dir, train_dir=custom_dir, test_dir=DIRECTORY, size=TRAIN_SIZE, ext='.txt')

  ###################################################################
  # (4) generate `tests.txt` from `test_quote_10.txt` and `test_not_quote_10.txt`  (in quotes_dir)

  write_tests(test_files)
  write_intents_config()
#

if __name__ == '__main__':
  try:
    DIRECTORY = sys.argv[1]
  except IndexError:
    DIRECTORY = os.getcwd()  # quotes_dir

  assert exists(DIRECTORY) and is_dir(DIRECTORY)
  # assert basename(DIRECTORY) == 'quotes'

  quotes_dir = DIRECTORY


  try:
    TRAIN_SIZE = float(sys.argv[2])
  except IndexError:
    TRAIN_SIZE = 0.9

  for directory_name in ['data', 'custom', 'results']:
    os.makedirs(join_path(DIRECTORY, directory_name), exist_ok=True)

  # names of files from gcloud bucket to use for quotes interpreter
  quotes_1, quotes_2 = 'quotes.txt', 'new_quotes.txt'
  not_quotes_1, not_quotes_2 = 'notquotes.txt', 'new_not_quotes.txt'  # TODO rename in gcloud: 'not_quotes.txt'

  FILES = {'quote': [quotes_1, quotes_2], 'not_quote': [not_quotes_1, not_quotes_2]}

  sys.exit(main())
