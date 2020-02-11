import os
import json
from os.path import join as join_path
from testing.metrics import compute_all

TABLE_BAR_LENGTH = 160


def json_dump(data, outfile, directory=None):
    """
    :param data: json serializable object
    :param outfile: str; name of output file
    :param directory: str (optional);
    :return: saves data to file named outfile in directory (or current dir if unspecified)
    """
    if not directory:
        directory = os.getcwd()
    outfile = join_path(directory, outfile)
    json.dump(data, open(outfile, "w+"), indent=2)


def print_table(timing_list, top_n=5, first_k_chars=25):
    """ 
    Prints a formatted table ordered by longest test timings. 
        
    :param timing_list: namedtuple, list of namedtuples representing testing results
    """

    print(TABLE_BAR_LENGTH * '-')
    sorted_timing = sorted(
        timing_list, key=lambda tup: tup.time_dif_ms, reverse=True
    )
    print("\nTop", top_n, "longest timed tests:\n")
    print(
        '{:<30s}{:<12s}{:<30s}{:<35s}{:<25s}'.format(
            'test_file_name', 'test_no', 'test_name', 'transcript', 'time(ms)'
        )
    )
    print(TABLE_BAR_LENGTH * '-')

    for x in sorted_timing[:top_n]:
        print(
            '{:<30s}{:<12d}{:<30s}{:<35s}{:<25.2f}'.format(
                x.test_file[:first_k_chars], x.test_no,
                x.test_name[:first_k_chars], x.transcript[:first_k_chars],
                x.time_dif_ms
            )
        )

    print(TABLE_BAR_LENGTH * '-')


def print_failures(test_failures):
    """ 
    Prints a formatted table of failed tests.
    The input is a list of failed tests.
    """

    table_string = '{:<40s}{:<20s}{:<100s}'
    lower_table_string = '{:<60s}{:<100s}'

    print(TABLE_BAR_LENGTH * '-')
    print("\nTest failures:\n")
    print(
        table_string.format(
            'test_name', 'test_type', 'expected_value/observed_value'
        )
    )
    print(TABLE_BAR_LENGTH * '-')

    for t in test_failures:
        print(table_string.format(t[0][:40], t[1][:20], t[2][:100]))
        print(lower_table_string.format(' ', t[3][:100]))
        print()

    print(TABLE_BAR_LENGTH * '-')


def record_results(output_dict, save_results=False):
    print("\n---\n")
    print(
        "Entity Accuracy: {:.2f}".
        format(output_dict["entity_accuracy"])
    )

    # evaluate metrics; treat each possible intent as reference
    metrics_dict = compute_all(
        output_dict["expected_intents"], output_dict["observed_intents"]
    )

    # record message regardless of number of entity errors
    message = "\n({} / {}) tests passed in {} seconds from {}\n".format(
        output_dict["correct_tests"],
        output_dict["total_tests"],
        output_dict["test_time_sec"],
        output_dict["test_file"],
    )
    print(message)

    if save_results:
        os.makedirs('results', exist_ok=True)
        filename = output_dict["test_file"].split("/")[-1]
        json_dump(
            data=output_dict,
            outfile="results/{}".format(
                filename.replace(".txt", "_results.json")
            )
        )
        json_dump(
            data=metrics_dict,
            outfile="results/{}".format(
                filename.replace(".txt", "_metrics.json")
            )
        )

    if output_dict["total_tests"] > output_dict["correct_tests"]:
        return False

    return True
