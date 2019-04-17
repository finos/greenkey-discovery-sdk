import argparse
import random
from os.path import abspath, dirname

parser = argparse.ArgumentParser(description="Write intent-specific test files and tests.txt")
parser.add_argument("--quotes", default="test_quotes_10.txt", help="Path to test data file with quotes")
parser.add_argument("--not-quotes", default="test_not_quotes_10.txt", help="Path to test data file without quotes")
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

args = parser.parse_args()

# get lines from test files for quotes and not quotes   List[Tuple(intent_label, transcript))
# NOTE: intents quote and not_quote are hardcoded
quote_transcripts = [('quote', line.strip()) for line in open(args.quotes, 'r+') if line.strip()]
not_quote_transcripts = [('not_quote', line.strip()) for line in open(args.not_quotes, 'r+') if line.strip()]

# combine quote and not quote transcripts (str) & shuffle tests.txt will not be blocked by intent type
transcripts = quote_transcripts + not_quote_transcripts

if args.shuffle:
    random.shuffle(transcripts)

# write to file: format tests.txt for launch_discovery.py tests
with open(args.outfile, 'w+') as fw:
    for test_no, (intent, transcript) in enumerate(transcripts):
        fw.writelines('test: quotes_not_quotes {}\n'.format(test_no))
        fw.writelines('intent: {}\n'.format(intent))
        fw.writelines('transcript: {}\n\n'.format(transcript))

print("Successfully generated tests.txt in {} directory".format(abspath(dirname(args.outfile))))
