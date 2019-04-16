#!/usr/bin/env python3

import random
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="Write intent-specific test files and tests.txt")
parser.add_argument("--intents", default="quote not_quote", help="String with each intent separated by a space")
parser.add_argument("--directory", help="Path to directory containing test data files")
parser.add_argument("--test_size", default=10, type=int, help="Percent of original data reserved for testing")
parser.add_argument("--outfile", default="tests.txt", help="Name to write tests containing quotes and not quotes data")
parser.add_argument(
    "--shuffle",
    default=False,
    type=bool,
    help="Whether to shuffle concatenated quotes and not "
    "quotes test "
    "strings before writing tests.txt. If False, "
    "tests will be "
    "blocked by intent label and quotes will precede not-quotes"
)


def read_tests(intent_label, directory, test_size):
    """
  :param intent_label: str, name of intent
  :param infile: path to file containing new-line separated strings, each an instance of intent_label
  :return: List[Tuple(intent_label, str)]  where the str is a line in the file
  """
    infile = Path(directory) / "test_{}_{}".format(intent_label, test_size)
    assert infile.exists() and infile.is_file()
    return [(intent_label, line.strip()) for line in open(infile, 'r+') if line.strip()]


def write_tests(transcripts, outfile, shuffle):
    if shuffle:
        random.shuffle(transcripts)
    with open(outfile, 'w+') as fw:  # format tests.txt for test_discovery.py
        for test_no, (intent, transcript) in enumerate(transcripts):
            fw.writelines('test: quotes_not_quotes {}\n'.format(test_no))
            fw.writelines('intent: {}\n'.format(intent))
            fw.writelines('transcript: {}\n\n'.format(transcript))
    print("Successfully generated {} in {} directory".format(outfile, Path(outfile).parent))


if __name__ == "__main__":
    args = parser.parse_args()

    directory = args.directory if args.directory else Path.cwd()

    transcripts = [
        read_tests(intent_label=intent, directory=directory, test_size=args.test_size)
        for intent in args.intents.split()
    ]
    write_tests(transcripts=transcripts, outfile=args.outfile, shuffle=args.shuffle)
