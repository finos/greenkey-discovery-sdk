##############################
# #######################################
# (ins)amelie@amu:~/src/gree...es/equal_sample_size$ wc -l *
#     5238 formatted_test_not_quotes_10.txt
#    47131 formatted_train_not_quotes_90.txt
#    58443 formatted_train_quotes_90.txt
#    23578 imstrings.txt
#      394 security_db.txt
#     5239 unformatted_test_not_quotes_10.txt
#    47146 unformatted_train_not_quotes_90.txt
#    58543 unformatted_train_quotes_90.txt
#   245712 total
#####################################################################
import requests
import sys
from os.path import exists
from asrtoolkit.clean_formatting import clean_up


def load_data(infile):
    """
    :param infile: str, path to .txt file
    :return: List[List], each line contains a non-blank line from the file
    """
    with open(infile, 'r+') as f:
        return [line.strip() for line in f.readlines() if line.strip()]


def unformat(text):
    """
    :param text: str
    :return: str, unformat text using clean_up from asrtoolkit.clean_formatting
    """
    return clean_up(text)


def post_to_discovery(text):
    """
    :param text: str, text to post to discovery
    :return: JSON output from Discovery if post was successful; else empty dict
    """
    headers = {"Content-type": "application/json"}
    payload = {"transcript": text}
    r = requests.post(discovery_url, headers=headers, json=payload)

    if r and r.status_code == 200:
        return r.json()
    else:
        if r:
            print("\nError: Status Code: {}\n".format(r.status_code))
        print("\nFailed to post to Discovery: {}\n".format(payload))
        return {}


def main(infile, label='quote'):
    """
    :param infile: str, path to .txt file
    :return: dict; with keys TP, FN, and results
        posts each line in .txt file to discovery, saves output to results,
        then computes TP and FN by comparing observed to exected ('quote')
        TP: int, true positives
        FN: int, false negatives (observed was 'not_quote' when it should have been labeled 'quote')
        results: List[Dict], each Dict is segments lattice returned from discovery, one per posted transcript
    """
    data = load_data(infile)
    results = []
    observed = []
    for i, text in enumerate(data):
        segments = post_to_discovery(text=text)
        if segments:
            results.append(segments)
            observed = segments['intents'][0]  # TODO check
    TP, FN = 0, 0
    for y_pred in observed:
        if y_pred == label:
            TP += 1
        else:
            FN += 1
    return dict(TP=TP, FN=FN, results=results)


if __name__ == '__main__':
    PORT = 8001
    discovery_url = "http://localhost:{}/process".format(PORT)
    label = 'quote'

    try:
        infile = sys.argv[1]
        assert exists(infile)
    except (IndexError, AssertionError) as e:
        print("Requires argument: valid path to a .txt file where each line is a transcript to post to Discovery")
        sys.exit(1)

    main(infile, label=label)
    sys.exit(0)
